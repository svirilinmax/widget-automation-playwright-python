@echo off
echo  Запуск Widget Test Runner...

REM Проверка наличия Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker не установлен. Пожалуйста, установите Docker.
    exit /b 1
)

REM Сборка и запуск
docker-compose up --build -d

REM Ожидание запуска
echo ⏳ Ожидание запуска сервера...
timeout /t 5 /nobreak >nul

REM Открытие браузера
start http://localhost:8000/static/index.html

echo  Готово! Интерфейс доступен по адресу: http://localhost:8000/static/index.html
