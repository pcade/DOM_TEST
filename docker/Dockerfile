FROM python:3.11-slim

# Установка зависимостей
RUN apt update && apt upgrade -y && \
    apt install -y sshpass jq git curl make openssh-server \
    && pip install ansible ansible-lint yamllint \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /ansible

# Копируем всё, что нужно для роли
COPY roles ./roles
COPY entrypoint.sh /entrypoint.sh

# Делаем entrypoint.sh исполняемым
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
