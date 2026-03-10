FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка браузеров Playwright
RUN playwright install chromium
RUN playwright install-deps

# Копирование проекта
COPY . .

# Создание необходимых директорий
RUN mkdir -p data test_reports test_screenshots

# Удаление дублирующейся папки frontend (используем только backend/static)
RUN rm -rf frontend

# Очистка __pycache__
RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Установка прав
RUN chmod +x backend/run.py

# Открытие портов
EXPOSE 8000

# Команда для запуска
CMD ["python", "backend/run.py"]
