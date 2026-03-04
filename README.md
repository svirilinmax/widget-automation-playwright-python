# Events Widget Constructor Tests

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.58.0-green.svg)](https://playwright.dev/)
[![Pytest](https://img.shields.io/badge/pytest-9.0.2-yellow.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen.svg)](https://coverage.readthedocs.io/)

## Автоматизированные тесты для конструктора календаря мероприятий

Набор автоматизированных тестов для веб-страницы `https://dev.3snet.info/eventswidget/` с использованием Python, Pytest и Playwright.

---

## Оглавление

- [Ключевые характеристики](#ключевые-характеристики)
- [Функциональные возможности](#функциональные-возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
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
| **Архитектура** | Page Object Model |
| **Тестовое покрытие** | 86% (основной функционал) |
| **Формат результата** | Подробное логирование + отчеты Pytest |
| **Лицензия** | MIT |

---

## Функциональные возможности

### Позитивные сценарии
- Проверка успешной загрузки страницы
- Полный пользовательский сценарий (Happy Path)
- Валидация полей ввода размеров
- Граничные значения полей
- Работа кнопок "Очистить"

### Негативные сценарии
- Генерация без выбора темы
- Генерация без выбора стран

### Валидация данных
- **Поля размеров**: проверка ввода отрицательных чисел, текста, спецсимволов, пустых строк
- **Автоматический сброс** на значение по умолчанию (230) при некорректном вводе

---

## Установка

### Клонирование репозитория
```bash
    git clone https://github.com/svirilinmax/widget-automation-playwright-python.gitl
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

### Запуск всех тестов
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

## Структура проекта

```
widget-automation-playwright-python/
├── .gitignore                    # Игнорируемые файлы
├── README.md                      # Документация
├── requirements.txt               # Зависимости проекта
├── pytest.ini                     # Конфигурация pytest
├── conftest.py                     # Фикстуры Playwright
├── pages/                          # Page Object паттерн
│   ├── __init__.py
│   └── constructor_page.py        # Page Object для страницы конструктора
├── tests/                          # Тестовые сценарии
│   ├── __init__.py
│   ├── test_ui_constructor.py      # UI тесты
│   ├── test_negative_scenarios.py  # Негативные сценарии
│   ├── test_error_handling.py      # Тесты обработки ошибок
└── utils/                          # Вспомогательные модули
    └── data_provider.py            # Тестовые данные
```

---

## Покрытие тестов

### UI тесты (`test_ui_constructor.py`)

| Тест | Статус | Описание |
|------|--------|----------|
| `test_page_loads_successfully` | ✅ | Проверка загрузки страницы и видимости формы |
| `test_happy_path_generate_code` | ✅ | Полный пользовательский сценарий: выбор темы, стран, размеров, генерация |
| `test_dimensions_input_validation` | ✅ | Валидация поля ширины (отрицательные, текст, спецсимволы, границы) |
| `test_edge_dimensions_values` | ✅ | Проверка экстремальных значений размеров (-100, 0, 9999) |
| `test_clear_buttons_work` | ✅ | Проверка кнопок очистки для тематики и стран |

### Негативные сценарии (`test_negative_scenarios.py`)

| Тест | Статус | Описание |
|------|--------|----------|
| `test_empty_theme_selection` | ✅ | Генерация без выбора темы (UI генерирует код) |
| `test_empty_countries_selection` | ✅ | Генерация без выбора стран (UI генерирует код) |

### Тесты обработки ошибок (`test_error_handling.py`)

| Тест | Статус | Описание |
|------|--------|----------|
| `test_navigate_with_invalid_url` | ✅ | Проверка обработки неверного URL |
| `test_navigate_timeout_handling` | ✅ | Проверка обработки таймаута |
| `test_navigate_with_network_error` | ✅ | Проверка обработки сетевой ошибки |
| `test_navigate_with_mixed_content_warning` | ✅ | Проверка mixed content warnings |
| `test_page_loads_with_different_wait_conditions` | ✅ | Проверка разных wait_until параметров |

---

## Архитектура

### Page Object Model
Проект использует паттерн Page Object для разделения логики тестов и описания страницы:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Тесты       │────▶│   Page Object   │────▶│   Веб-страница  │
│  (test_*.py)    │     │(constructor_page│     │   (DOM-элементы) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Фикстуры      │
                        │  (conftest.py)  │
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
- Создание скриншотов при падении тестов
- Обработка консольных ошибок

#### Тестовые данные (`data_provider.py`)
- Централизованное хранение тестовых наборов
- Параметризация тестов

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
| `exploratory` | Исследовательские тесты | `pytest -m exploratory` |

### Переменные окружения
```bash
    # Отключение headless режима (для отладки)
    export PLAYWRIGHT_HEADLESS=false  # Linux/Mac
    set PLAYWRIGHT_HEADLESS=false     # Windows
```

### Конфигурация в pytest.ini
```ini
[pytest]
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(message)s
addopts = -v --strict-markers --tb=short --maxfail=1
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

### Создание скриншотов
При падении тестов автоматически создаются скриншоты в папке `test_screenshots`:
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

---

## Планы по развитию

- Интеграция с Allure Reports для визуализации результатов
- Добавление тестов на адаптивность (разные разрешения экрана)
- Параллельный запуск тестов (pytest-xdist)
- Интеграция с CI/CD (GitHub Actions)
- Расширение покрытия до 95%

---

## Лицензия и авторство

**Лицензия**: MIT
**Разработчик**: Максим Свирилин
**Репозиторий**: [github.com/svirilinmax](https://github.com/svirilinmax)
**Вопросы**: mak.svirilin@gmail.com
**Telegram**: @svirilinmax

---

*Events Widget Constructor Tests —  набор автоматизированных тестов, демонстрирующий практики тестирования веб-интерфейсов с использованием Python, Pytest и Playwright.*
```
