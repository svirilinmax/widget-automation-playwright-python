import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="function")
def page():
    """Фикстура для создания страницы перед каждым тестом"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            locale='ru-RU'
        )
        page = context.new_page()

        # Добавляем обработчик ошибок с подробной информацией
        page.on("pageerror", lambda err: print(f"Page error: {err}"))
        page.on("console", lambda msg: print(f"Console: {msg.text}"))

        yield page

        # Делаем скриншот при падении теста
        if hasattr(page, '_test_failed') and page._test_failed:
            page.screenshot(path=f"failure_{page._test_name}.png")

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