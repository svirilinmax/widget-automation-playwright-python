# Events Widget Constructor Tests

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.58.0-green.svg)](https://playwright.dev/)
[![Pytest](https://img.shields.io/badge/pytest-9.0.2-yellow.svg)](https://docs.pytest.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

## Автоматизированные тесты для конструктора календаря мероприятий + веб-интерфейс

Комплексное решение для автоматизированного тестирования веб-страницы `https://dev.3snet.info/eventswidget/` с использованием Python, Pytest и Playwright, а также веб-интерфейс для управления тестами на FastAPI.

---

## Оглавление

- [Ключевые характеристики](#ключевые-характеристики)
- [Функциональные возможности](#функциональные-возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Веб-интерфейс](#веб-интерфейс)
- [Структура проекта](#структура-проекта)
- [Покрытие тестов](#покрытие-тестов)
- [Архитектура](#архитектура)
- [Выявленные особенности UI](#выявленные-особенности-ui)
- [Параметры запуска](#параметры-запуска)
- [Примеры использования](#примеры-использования)
- [Разработка и тестирование](#разработка-и-тестирование)
- [Устранение неполадок](#устранение-неполадок)
- [Лицензия и авторство](#лицензия-и-авторство)

---

## Ключевые характеристики

| Параметр | Значение |
|---------|---------|
| **Язык реализации** | Python 3.13+ |
| **Фреймворк тестирования** | Pytest 9.0.2 |
| **Инструмент автоматизации** | Playwright 1.58.0 |
| **Веб-фреймворк** | FastAPI 0.135.1 |
| **Архитектура** | Page Object Model + REST API |
| **Тестовое покрытие** | 31 тест (включая API) |
| **Формат результата** | JSON-отчеты + веб-интерфейс |
| **Лицензия** | MIT |

---

## Функциональные возможности

### Автоматизированные тесты (31 тест)
- **UI тесты** - проверка пользовательского интерфейса
- **Негативные сценарии** - обработка ошибок и граничных значений
- **API тесты** - проверка эндпоинтов веб-интерфейса

### Веб-интерфейс
- **Управление тестами** - запуск всех тестов или выборочно
- **Мониторинг** - отслеживание прогресса выполнения в реальном времени
- **История запусков** - просмотр предыдущих запусков с фильтрацией
- **Детальный анализ** - просмотр ошибок и скриншотов

### Инфраструктура
- **Логирование** - подробное логирование всех шагов
- **Скриншоты** - автоматическое сохранение при падении тестов
- **Docker** - контейнеризация для простого запуска
- **База данных** - SQLite для хранения истории запусков

---

## Установка

### Клонирование репозитория
```bash
    git clone https://github.com/svirilinmax/widget-automation-playwright-python.git
    cd widget-automation-playwright-python
```

### Создание виртуального окружения
```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python -m venv venv
    source venv/bin/activate
```

### Установка зависимостей
```bash
    pip install -r requirements.txt
    playwright install chromium
```

---

## Быстрый старт

### Запуск через Docker (рекомендуется)
```bash
    # Windows
    .\run.bat


    # Linux/Mac
    chmod +x run.sh
    ./run.sh
```

### Запуск всех тестов (без веб-интерфейса)
```bash
    pytest
```

### Запуск с подробным логированием
```bash
    pytest -v --log-cli-level=INFO
```

### Запуск конкретного теста
```bash
    pytest tests/test_ui_constructor.py::TestConstructor::test_happy_path_generate_code -v
```

### Запуск только smoke тестов
```bash
    pytest -m smoke
```

### Запуск с отчетом HTML
```bash
   pytest --html=report.html --self-contained-html
```

---

## Веб-интерфейс

### Запуск веб-интерфейса
```bash
    cd backend
    python run.py
```

После запуска откройте `http://localhost:8000/static/index.html`

### Основные возможности

#### Управление тестами
- Кнопка "Запустить все тесты" - запуск полного набора тестов
- Множественный выбор тестов для выборочного запуска
- Фильтрация по маркерам (smoke, regression)

#### Мониторинг выполнения
- Прогресс-бар с процентом выполнения
- Текущий статус (running, completed, failed)
- Количество пройденных и упавших тестов
- Информационное сообщение о ходе выполнения

#### История запусков
- Поиск по ID запуска
- Фильтрация по статусам (все, успешно, с ошибками)
- Длительность каждого запуска
- Детальная информация по каждому запуску

#### Детали запуска
- Полная информация о запуске (ID, статус, время, длительность)
- Таблица результатов каждого теста
- Просмотр ошибок с подсветкой синтаксиса
- Ссылки на скриншоты при падении

### API эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/tests/list` | Список доступных тестов |
| POST | `/api/tests/run` | Запуск тестов |
| GET | `/api/tests/run/{run_id}` | Статус запуска |
| GET | `/api/tests/runs` | История запусков |
| GET | `/api/results/recent` | Последние результаты |
| GET | `/api/results/stats/summary` | Статистика |

---

## Структура проекта

```
widget-automation-playwright-python/
├── .gitignore                    # Игнорируемые файлы
├── .pre-commit-config.yaml       # Настройки pre-commit хуков
├── pyproject.toml                 # Основной файл конфигурации проекта
├── README.md                      # Документация
├── requirements.txt               # Зависимости проекта
├── conftest.py                     # Фикстуры Playwright
├── docker-compose.yml              # Docker Compose конфигурация
├── Dockerfile                      # Docker образ
├── run.bat                         # Скрипт запуска для Windows
├── run.sh                          # Скрипт запуска для Linux/Mac
├── pages/                          # Page Object паттерн
│   ├── __init__.py
│   └── constructor_page.py        # Page Object для страницы конструктора
├── tests/                          # Тестовые сценарии
│   ├── __init__.py
│   ├── test_ui_constructor.py      # UI тесты (11 тестов)
│   ├── test_negative_scenarios.py  # Негативные сценарии (2 теста)
│   ├── test_error_handling.py      # Тесты обработки ошибок (6 тестов)
│   └── test_results_api.py         # API тесты (12 тестов)
├── backend/                        # Веб-интерфейс на FastAPI
│   ├── run.py                      # Запуск бэкенда
│   ├── app/                         # Основное приложение
│   │   ├── main.py                   # Точка входа FastAPI
│   │   ├── database.py                # Работа с БД
│   │   ├── models.py                  # SQLAlchemy модели
│   │   ├── schemas.py                 # Pydantic схемы
│   │   ├── crud.py                    # CRUD операции
│   │   ├── test_runner.py             # Запуск тестов
│   │   └── routers/                    # Роутеры API
│   │       ├── tests.py                # Эндпоинты для тестов
│   │       └── results.py              # Эндпоинты для результатов
│   ├── static/                       # Фронтенд
│   │   ├── index.html                 # Главная страница
│   │   ├── styles.css                  # Стили
│   │   ├── script.js                   # JavaScript
│   ├── data/                          # База данных SQLite
│   └── test_reports/                   # JSON отчеты о тестах
└── utils/                          # Вспомогательные модули
    └── data_provider.py            # Тестовые данные
```

---

## Покрытие тестов

### Всего тестов: **31**

| Категория | Количество тестов |
|-----------|-------------------|
| UI тесты (`test_ui_constructor.py`) | 11 |
| Тесты обработки ошибок (`test_error_handling.py`) | 6 |
| Негативные сценарии (`test_negative_scenarios.py`) | 2 |
| API тесты (`test_results_api.py`) | 12 |

### UI тесты (`test_ui_constructor.py`)

| Тест | Описание |
|------|----------|
| `test_page_loads_successfully` | Проверка загрузки страницы и видимости формы |
| `test_happy_path_generate_code` | Полный пользовательский сценарий: выбор темы, стран, размеров, генерация |
| `test_dimensions_input_validation` | Валидация поля ширины (отрицательные, текст, спецсимволы, границы) |
| `test_edge_dimensions_values` | Проверка экстремальных значений размеров (-100, 0, 9999) |
| `test_clear_buttons_work` | Проверка кнопок очистки для тематики и стран |
| `test_clear_theme_when_button_not_visible` | Очистка темы когда кнопка не видна |
| `test_clear_countries_when_button_not_visible` | Очистка стран когда кнопка не видна |
| `test_has_error_messages_detection` | Проверка обнаружения сообщений об ошибках |
| `test_is_page_loaded_without_button_check` | Проверка загрузки без проверки кнопки |
| `test_is_page_loaded_when_form_missing` | Проверка когда форма отсутствует |
| `test_get_width_value_empty_field` | Получение значения из пустого поля |

### Тесты обработки ошибок (`test_error_handling.py`)

| Тест | Описание |
|------|----------|
| `test_navigate_with_invalid_url` | Проверка обработки неверного URL |
| `test_navigate_timeout_handling` | Проверка обработки таймаута |
| `test_navigate_with_network_error` | Проверка обработки сетевой ошибки |
| `test_navigate_with_mixed_content_warning` | Проверка mixed content warnings |
| `test_page_loads_with_different_wait_conditions` | Проверка разных wait_until параметров |
| `test_navigate_fallback_on_error` | Проверка fallback механизма при ошибке |

### Негативные сценарии (`test_negative_scenarios.py`)

| Тест | Описание |
|------|----------|
| `test_empty_theme_selection` | Генерация без выбора темы (UI генерирует код) |
| `test_empty_countries_selection` | Генерация без выбора стран (UI генерирует код) |

### API тесты (`test_results_api.py`)

| Тест | Описание |
|------|----------|
| `test_get_all_results` | Получение всех результатов с пагинацией |
| `test_get_all_results_with_filter` | Фильтрация результатов по статусу |
| `test_get_recent_results` | Получение результатов за последние N часов |
| `test_get_result_by_id` | Получение конкретного результата по ID |
| `test_get_test_history` | Получение истории конкретного теста |
| `test_get_results_summary` | Получение сводной статистики |
| `test_get_nonexistent_result` | Обработка несуществующего результата |
| `test_delete_result` | Удаление результата |
| `test_get_screenshot_for_result` | Получение скриншота для результата |

---

## Архитектура

### Page Object Model
Проект использует паттерн Page Object для разделения логики тестов и описания страницы:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Тесты       │───▶│   Page Object   │────▶│   Веб-страница  │
│  (test_*.py)    │     │(constructor_page│     │   (DOM-элементы)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Фикстуры      │
                        │  (conftest.py)  │
                        └─────────────────┘
```

### Веб-интерфейс

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Фронтенд      │───▶│   FastAPI       │────▶│   База данных   │
│  (HTML/CSS/JS)  │     │   (бэкенд)      │     │   (SQLite)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Pytest        │
                        │   (тесты)       │
                        └─────────────────┘
```

### Ключевые компоненты

#### Page Object (`constructor_page.py`)
- Инкапсулирует селекторы элементов
- Предоставляет бизнес-методы (`select_theme`, `select_all_countries`, `generate_preview`)
- Скрывает детали реализации от тестов

#### Фикстуры (`conftest.py`)
- Управление браузером (запуск/остановка)
- Настройка viewport и локали
- Создание скриншотов при падении тестов в `backend/test_screenshots/`
- Обработка консольных ошибок

#### Тестовые данные (`data_provider.py`)
- Централизованное хранение тестовых наборов
- Параметризация тестов

#### Бэкенд (`backend/`)
- REST API на FastAPI
- SQLAlchemy модели для хранения результатов
- Фоновый запуск тестов через `BackgroundTasks`
- JSON-отчеты в `backend/test_reports/`

#### Фронтенд (`backend/static/`)
- Чистый JavaScript без фреймворков
- Адаптивный дизайн
- Реальное время через polling

---

## Выявленные особенности UI

### 1. Кнопка очистки стран
**Проблема**: После выбора всех стран кнопка "Очистить" становится невидимой.
**Статус**: Не баг, а особенность дизайна (UI-логика).
**Обработка в тестах**: Тест проверяет видимость и логирует эту особенность.

### 2. Генерация кода без обязательных полей
**Проблема**: Страница генерирует код даже если не выбрана тема или страны.
**Статус**: Возможный баг или особенность API. Задокументировано как поведение системы.
**Обработка в тестах**: Негативные сценарии проверяют и подтверждают это поведение.

### 3. Mixed Content warnings
**Проблема**: В консоли браузера появляются предупреждения о смешанном контенте.
**Статус**: Не влияет на функциональность, браузер автоматически апгрейдит до HTTPS.
**Обработка**: Предупреждения логируются, но не влияют на прохождение тестов.

### 4. Валидация поля ширины
**Поведение**: При вводе некорректных значений (отрицательные, текст, спецсимволы) поле автоматически сбрасывается на 230.
**Статус**: Ожидаемое поведение (frontend-валидация).
**Обработка**: Тесты проверяют это поведение.

---

## Параметры запуска

### Маркеры тестов
| Маркер | Описание | Пример |
|--------|----------|--------|
| `smoke` | Быстрые проверки основного функционала | `pytest -m smoke` |
| `regression` | Полный регресс | `pytest -m regression` |

### Переменные окружения
```bash
    # Отключение headless режима (для отладки)
    export PLAYWRIGHT_HEADLESS=false  # Linux/Mac
    set PLAYWRIGHT_HEADLESS=false     # Windows
```

### Конфигурация в pyproject.toml
```toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)s] %(message)s"
addopts = "-v --strict-markers --tb=short --maxfail=1"
filterwarnings = [
    "ignore::DeprecationWarning:greenlet.*:",
    "ignore::pytest.PytestUnraisableExceptionWarning",]
```

---

## Примеры использования

### Пример 1: Базовый тест
```python
def test_page_loads_successfully(self, page):
    """Проверка загрузки страницы"""
    constructor = ConstructorPage(page)
    constructor.navigate()

    assert "eventswidget" in page.url
    assert constructor.is_page_loaded()
```

### Пример 2: Параметризованный тест
```python
@pytest.mark.parametrize("width,height", [
    ("-100", "600"),
    ("0", "600"),
    ("9999", "600")
])
def test_edge_dimensions(self, page, width, height):
    """Тест граничных значений"""
    constructor = ConstructorPage(page)
    constructor.navigate()
    constructor.set_dimensions(width, height)
```

### Пример 3: Обработка нестандартного UI
```python
def test_clear_buttons_work(self, page):
    """Тест с обработкой особенностей UI"""
    constructor = ConstructorPage(page)
    constructor.navigate()

    constructor.select_all_countries()

    countries_clear_visible = page.locator(constructor.countries_clear).is_visible()
    if not countries_clear_visible:
        logger.info("Кнопка не видима - особенность UI")
```

### Пример 4: Запуск тестов через API
```python
import requests

# Запуск всех тестов
response = requests.post(
    "http://localhost:8000/api/tests/run",
    json={"test_names": None, "parallel": False}
)
run_id = response.json()["run_id"]

# Проверка статуса
status = requests.get(f"http://localhost:8000/api/tests/run/{run_id}").json()
print(f"Статус: {status['status']}, Пройдено: {status['passed']}, Упало: {status['failed']}")
```

---

## Разработка и тестирование

### Добавление нового теста
1. Определите сценарий (позитивный/негативный)
2. Добавьте метод в соответствующий класс тестов
3. Используйте методы Page Object для взаимодействия
4. Добавьте логирование для отслеживания выполнения

### Локальный запуск с отладкой
```bash
    # Временно отключить headless режим
    # В файле conftest.py измените headless=True на headless=False

    # Запуск с паузой после каждого действия
    pytest --headed --slowmo=1000
```

### Качество кода (pre-commit хуки)
```bash
    # Установка pre-commit хуков
    pre-commit install

    # Ручной запуск проверок
    pre-commit run --all-files
```

### Создание скриншотов
При падении тестов автоматически создаются скриншоты в папке `backend/test_screenshots/`:
```
failure_test_happy_path_generate_code_20240304_123456.png
failure_test_clear_buttons_work_20240304_123457.png
```

---

## Устранение неполадок

### Проблема: Тест падает с TimeoutError
**Причина**: Элемент не появляется на странице вовремя
**Решение**:
- Увеличить таймаут в `set_default_timeout`
- Проверить селектор элемента
- Добавить `wait_for_timeout` перед взаимодействием

### Проблема: Element is not visible
**Причина**: Попытка взаимодействия со скрытым элементом
**Решение**:
- Использовать `force=True` для кликов
- Проверять видимость перед действием
- Использовать альтернативные селекторы

### Проблема: Mixed Content warnings
**Причина**: HTTP-контент на HTTPS-странице
**Решение**: Игнорировать (не влияет на тесты) или добавить в разрешённые

### Проблема: Тесты проходят локально, но падают в CI
**Причина**: Различия в окружении (размер окна, тайминги)
**Решение**:
- Фиксировать viewport в фикстурах
- Добавить явные ожидания вместо `timeout`
- Использовать `retry` для нестабильных тестов

### Проблема: Скриншоты не сохраняются
**Причина**: Неправильный путь к папке
**Решение**: Проверьте, что в `conftest.py` указан правильный путь `backend/test_screenshots/`

### Проблема: Веб-интерфейс не показывает прогресс
**Причина**: Отсутствует элемент runStats в DOM
**Решение**: Проверьте, что в `index.html` есть элемент с id="runStats"

---

## Планы по развитию

- Интеграция с Allure Reports для визуализации результатов
- Добавление тестов на адаптивность (разные разрешения экрана)
- Параллельный запуск тестов (pytest-xdist)
- Интеграция с CI/CD (GitHub Actions)
- Расширение покрытия до 95%

---

## Лицензия и авторство

- **Лицензия**: MIT
- **Разработчик**: Максим Свирилин
- **Репозиторий**: [github.com/svirilinmax/widget-automation-playwright-python](https://github.com/svirilinmax/widget-automation-playwright-python)
- **Вопросы**: mak.svirilin@gmail.com
- **Telegram**: @svirilinmax

---

*Events Widget Constructor Tests — набор автоматизированных тестов, демонстрирующий практики тестирования веб-интерфейсов с использованием Python, Pytest и Playwright.*
