#!/bin/bash

# Скрипт для запуска Ansible playbook с проверками

INVENTORY_FILE="roles/inventory.yaml"
PLAYBOOK_FILE="roles/playbook.yaml"

# Проверяем существование inventory файла
if [ ! -f "$INVENTORY_FILE" ]; then
    echo "Ошибка: Файл инвентаря '$INVENTORY_FILE' не найден!"
    exit 1
fi

# Проверяем существование playbook файла
if [ ! -f "$PLAYBOOK_FILE" ]; then
    echo "Ошибка: Файл плейбука '$PLAYBOOK_FILE' не найден!"
    exit 1
fi

echo "Запуск Ansible playbook..."
ansible-playbook -i "$INVENTORY_FILE" "$PLAYBOOK_FILE" --ask-become-pass