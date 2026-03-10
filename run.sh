#!/bin/bash

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

# Проверка наличия docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose не установлен. Пожалуйста, установите docker-compose."
    exit 1
fi

# Сборка и запуск
echo " Запуск Widget Test Runner..."
docker-compose up --build -d

# Ожидание запуска
echo " Ожидание запуска сервера..."
sleep 5

# Открытие браузера
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000/static/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8000/static/index.html
fi

echo " Готово! Интерфейс доступен по адресу: http://localhost:8000/static/index.html"
