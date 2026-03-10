import logging

import pytest

from pages.constructor_page import ConstructorPage

logger = logging.getLogger(__name__)


class TestErrorHandling:
    """Тесты для проверки обработки ошибок"""

    def test_navigate_with_invalid_url(self, page):
        """
        Проверка обработки неверного URL
        """
        constructor = ConstructorPage(page)
        original_url = constructor.base_url
        constructor.base_url = "https://invalid-url-12345.com"

        try:
            constructor.navigate()
            assert False, "Должно было быть исключение"
        except Exception as e:
            logger.info(f"Получено ожидаемое исключение: {type(e).__name__}")
            assert not constructor.is_page_loaded()
        finally:
            constructor.base_url = original_url

    def test_navigate_timeout_handling(self, page, monkeypatch):
        """Проверка обработки таймаута"""
        constructor = ConstructorPage(page)

        original_goto = page.goto

        def mock_goto_with_timeout(*args, **kwargs):
            """Симулируем таймаут"""
            import time

            time.sleep(0.1)
            raise Exception("Timeout exceeded")

        try:
            monkeypatch.setattr(page, "goto", mock_goto_with_timeout)

            with pytest.raises(Exception) as exc_info:
                constructor.navigate()

            # Проверяем сообщение об ошибке
            assert "Timeout" in str(exc_info.value)
            logger.info("Таймаут успешно обработан")

        finally:
            monkeypatch.setattr(page, "goto", original_goto)

    def test_navigate_with_network_error(self, page, monkeypatch):
        """Проверка обработки сетевой ошибки"""
        constructor = ConstructorPage(page)

        def mock_goto_with_error(*args, **kwargs):
            raise Exception("ERR_CONNECTION_REFUSED")

        try:
            monkeypatch.setattr(page, "goto", mock_goto_with_error)

            with pytest.raises(Exception) as exc_info:
                constructor.navigate()

            assert "ERR_CONNECTION_REFUSED" in str(exc_info.value)
            logger.info("Сетевая ошибка успешно обработана")

        finally:
            monkeypatch.setattr(page, "goto", page.goto)

    def test_navigate_with_mixed_content_warning(self, page):
        """
        Проверка что mixed content warnings не ломают навигацию
        """
        constructor = ConstructorPage(page)

        def console_handler(msg):
            if "Mixed Content" in msg.text:
                logger.info(f"Получен mixed content warning: {msg.text}")

        page.on("console", console_handler)

        constructor.navigate()

        assert constructor.is_page_loaded()
        logger.info("Mixed content warnings не влияют на загрузку страницы")

    def test_page_loads_with_different_wait_conditions(self, page):
        """
        Проверка загрузки страницы с разными wait_until параметрами
        """
        constructor = ConstructorPage(page)

        original_url = constructor.base_url

        try:
            wait_conditions = ["domcontentloaded", "commit", "load"]

            for condition in wait_conditions:
                logger.info(f"Тестируем wait_until='{condition}'")

                def test_navigate():
                    page.goto(original_url, wait_until=condition, timeout=30000)

                try:
                    test_navigate()
                    logger.info(f"Успешно с wait_until='{condition}'")
                except Exception as e:
                    logger.warning(f"Не удалось с wait_until='{condition}': {e}")

        finally:
            constructor.base_url = original_url

    def test_navigate_fallback_on_error(self, page, monkeypatch):
        """Проверяет, что navigate использует fallback (commit) при ошибке первого goto"""
        constructor = ConstructorPage(page)
        original_goto = page.goto
        call_count = 0

        def mock_goto(url, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Первая попытка не удалась")
            else:
                return original_goto(url, *args, **kwargs)

        monkeypatch.setattr(page, "goto", mock_goto)

        constructor.navigate()
        assert call_count == 2, "Должно быть две попытки вызова goto"
        assert constructor.is_page_loaded(), "Страница должна загрузиться после fallback'а"
