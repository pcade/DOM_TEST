#!/usr/bin/env python3
"""
EDA Job Monitor - простой мониторинг контейнеров с Ansible-ролями
"""
import json
import subprocess
import datetime
import sys

def get_timestamp():
    """Возвращает текущую метку времени в формате ISO"""
    return datetime.datetime.utcnow().isoformat() + "Z"

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

def is_recently_run(container_info, hours=24):
    """Проверяет, запускался ли контейнер за последние N часов"""
    if not container_info or not container_info.get("started_at"):
        return False
    
    started_str = container_info["started_at"].replace("Z", "")
    try:
        started_time = datetime.datetime.fromisoformat(started_str)
        time_diff = datetime.datetime.utcnow() - started_time
        return time_diff.total_seconds() <= hours * 3600
    except ValueError:
        return False

def is_successful(container_info):
    """Проверяет, завершился ли контейнер успешно"""
    if not container_info:
        return False
    if container_info.get("running", False):
        return True
    return container_info.get("exit_code", -1) == 0

def check_container(container_name, hours_threshold):
    """Проверяет статус одного контейнера"""
    info = get_container_info(container_name)
    if not info:
        return f"last_seen: unknown"
    
    recently_run = is_recently_run(info, hours_threshold)
    successful = is_successful(info)
    
    if recently_run and successful:
        return f"executed_at: {info['started_at']}"
    else:
        return f"last_seen: {info['started_at'] or 'unknown'}"

def main():
    """Основная функция"""
    prefix = "ansible-job-"
    hours_threshold = 24
    
    # Получаем системную информацию
    timestamp = get_timestamp()
    host = run_command(["hostname"]) or "unknown"
    ansible_version = run_command(["ansible", "--version"]) or "unknown"
    if "ansible" in ansible_version:
        ansible_version = ansible_version.split('\n')[0].split()[1]
    ansible_user = run_command(["whoami"]) or "unknown"
    
    # Проверяем контейнеры
    containers = get_containers(prefix)
    jobs_status = {}
    all_healthy = True
    
    for container in containers:
        status = check_container(container, hours_threshold)
        jobs_status[container] = status
        if "last_seen" in status:
            all_healthy = False
    
    # Формируем отчет
    report = {
        "timestamp": timestamp,
        "host": host,
        "ansible_version": ansible_version,
        "ansible_user": ansible_user,
        "message": {
            "status": "healthy" if all_healthy else "unhealthy",
            "jobs": jobs_status
        }
    }
    
    print(json.dumps(report, indent=2))
    return 0 if all_healthy else 1

if __name__ == "__main__":
    sys.exit(main())