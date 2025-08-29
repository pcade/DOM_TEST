#!/usr/bin/env python3
"""
EDA Job Monitor - простой мониторинг контейнеров с Ansible-ролями
"""

import json
import subprocess
import datetime
import sys

def get_timestamp():
    """Возвращает текущую метку времени в формате ISO без миллисекунд"""
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def run_command(cmd):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_containers(prefix):
    """Получает список контейнеров с заданным префиксом"""
    cmd = ["docker", "ps", "-a", "--filter", f"name={prefix}", "--format", "{{.Names}}"]
    output = run_command(cmd)
    if output:
        return [name for name in output.splitlines() if name]
    return []

def get_container_info(container_name):
    """Получает информацию о контейнере"""
    cmd = ["docker", "inspect", container_name]
    output = run_command(cmd)
    if not output:
        return None
    
    try:
        data = json.loads(output)[0]
        state = data.get("State", {})
        return {
            "started_at": state.get("StartedAt", ""),
            "exit_code": state.get("ExitCode", -1),
            "running": state.get("Running", False)
        }
    except (json.JSONDecodeError, IndexError):
        return None

def format_docker_time(docker_time):
    """Форматирует время Docker в нужный формат (без миллисекунд)"""
    if not docker_time:
        return None
    
    try:
        # Убираем миллисекунды и преобразуем в нужный формат
        if '.' in docker_time:
            base_time = docker_time.split('.')[0]
            return base_time + 'Z'
        return docker_time
    except:
        return None

def is_recently_run(container_info, hours=24):
    """Проверяет, запускался ли контейнер за последние N часов"""
    if not container_info or not container_info.get("started_at"):
        return False
    
    started_str = container_info["started_at"]
    formatted_time = format_docker_time(started_str)
    if not formatted_time:
        return False
    
    try:
        # Парсим время
        started_time = datetime.datetime.strptime(formatted_time, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.datetime.utcnow()
        time_diff = current_time - started_time
        return time_diff.total_seconds() <= hours * 3600
    except ValueError:
        return False

def is_successful(container_info):
    """Проверяет, завершился ли контейнер успешно"""
    if not container_info:
        return False
    if container_info.get("running", False):
        return True  # Работающий контейнер считается успешным
    return container_info.get("exit_code", -1) == 0

def check_container(container_name, hours_threshold):
    """Проверяет статус одного контейнера и возвращает (статус_сообщение, здоровый_ли)"""
    info = get_container_info(container_name)
    if not info:
        return "last_seen: unknown", False
    
    recently_run = is_recently_run(info, hours_threshold)
    successful = is_successful(info)
    formatted_time = format_docker_time(info["started_at"])
    
    if recently_run and successful:
        return f"executed_at: {formatted_time}", True
    else:
        return f"last_seen: {formatted_time or 'unknown'}", False

def get_ansible_version():
    """Получает версию Ansible"""
    ansible_version_output = run_command(["ansible", "--version"]) or "unknown"
    if ansible_version_output and "ansible" in ansible_version_output:
        for line in ansible_version_output.split('\n'):
            if line.strip().startswith("ansible"):
                return line.strip().split()[1]
    return "unknown"

def main():
    """Основная функция"""
    prefix = "ansible-job-"
    hours_threshold = 24
    
    # Получаем системную информацию (одна для всех отчетов)
    timestamp = get_timestamp()
    host = run_command(["hostname"]) or "unknown"
    ansible_version = get_ansible_version()
    ansible_user = run_command(["whoami"]) or "unknown"
    
    # Проверяем контейнеры
    containers = get_containers(prefix)
    all_healthy = True
    
    # Для каждого контейнера выводим отдельный JSON
    for container in containers:
        status_message, is_healthy = check_container(container, hours_threshold)
        
        if not is_healthy:
            all_healthy = False
        
        # Формируем отчет для каждого контейнера отдельно
        report = {
            "timestamp": timestamp,
            "host": host,
            "ansible_version": ansible_version,
            "ansible_user": ansible_user,
            "message": {
                "status": "healthy" if is_healthy else "unhealthy",
                "jobs": {
                    container: status_message
                }
            }
        }
        
        print(json.dumps(report, indent=2))
    
    return 0 if all_healthy else 1

if __name__ == "__main__":
    sys.exit(main())