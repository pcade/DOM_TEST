# Инструкция по сборке, запуску и тестированию

## Структура проекта

```
.
├── docker/              # Docker конфигурация
├── eda_job_monitor/    # Мониторинг EDA jobs
├── roles/              # Ansible роли
├── scripts/            # Вспомогательные скрипты
├── entrypoint.sh       # Точка входа
└── README.md          # Документация
```

## Предварительные требования

- Docker
- Ansible (если запускается без Docker)
- Python 3.8+

## Сборка Docker образа

```bash
# Сборка образа
docker build -t ssh-audit-role -f docker/Dockerfile .
```

## Запуск контейнера

```bash
# Запуск контейнера с интерактивной оболочкой
docker run -it --rm ssh-audit-role /bin/bash
```

### Запуск Ansible

```bash
# Запуск playbook c помощью Ansible
ansible-playbook -i roles/inventory.yaml roles/playbook.yaml --ask-become-pass

# Запуск playbook c помощью скрпита
chmod +x entrypoint.sh
./entrypoint.sh
```

## Тестирование

### Тестирование парсера SSH конфигурации

```bash
# Запуск парсера
python scripts/parse_ssh_config.py  <path_to_sshd_config> <path_to_standards.json>
```
### Тестирование `Ansible` и `Dockerfile` происходит в пайплайне `CI`
>> настроенно на пуш