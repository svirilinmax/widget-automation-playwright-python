import os
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="function")
def page():
    """Фикстура для создания страницы перед каждым тестом"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720}, locale="ru-RU")
        page = context.new_page()

        # Добавляем обработчик ошибок с подробной информацией
        page.on("pageerror", lambda err: print(f"Page error: {err}"))
        page.on("console", lambda msg: print(f"Console: {msg.text}"))

        yield page

        # Делаем скриншот при падении теста
        if hasattr(page, "_test_failed") and page._test_failed:
            # Создаем папку для скриншотов если её нет
            screenshots_dir = "test_screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            # Генерируем имя файла с датой и временем
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"failure_{page._test_name}_{timestamp}.png"
            screenshot_path = os.path.join(screenshots_dir, screenshot_name)

            # Сохраняем скриншот
            page.screenshot(path=screenshot_path)
            print(f" Screenshot saved: {screenshot_path}")

        context.close()
        browser.close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Настройки контекста для всех тестов"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "locale": "ru-RU",
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для отслеживания падений тестов"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            page._test_failed = True
            page._test_name = item.name
