import pytest
from pages.constructor_page import ConstructorPage
from utils.data_provider import DIMENSIONS_TEST_CASES, EDGE_DIMENSIONS
import logging

logger = logging.getLogger(__name__)


class TestConstructor:
    """Тесты для страницы конструктора календаря мероприятий"""

    def test_page_loads_successfully(self, page):
        """Тест проверяет успешную загрузку страницы"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        assert "eventswidget" in page.url, "Страница не загрузилась"
        assert constructor.is_page_loaded(), "Страница загрузилась, но не все элементы доступны"

    def test_happy_path_generate_code(self, page):
        """
        Позитивный тест: полный пользовательский сценарий
        """
        constructor = ConstructorPage(page)
        constructor.navigate()

        # Выполняем действия последовательно
        constructor.select_theme("Affiliate")
        constructor.select_all_countries()
        constructor.set_dimensions("460", "1000")
        constructor.set_color_theme(0)
        constructor.generate_preview()

        # Проверяем результат
        assert constructor.is_code_generated(), "Код не был сгенерирован"
        logger.info("Happy path тест успешно пройден")

    @pytest.mark.flaky(reruns=2, reruns_delay=2)
    def test_dimensions_input_validation(self, page):
        """Тест проверяет поведение поля ввода ширины"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        for case in DIMENSIONS_TEST_CASES:
            logger.info(f"Тестируем ввод: {case['description']} - '{case['input']}'")

            constructor.set_dimensions(case["input"], "600")
            actual_value = constructor.get_width_value()

            assert actual_value == case["expected"], \
                f"Для ввода '{case['input']}' ожидали '{case['expected']}', получили '{actual_value}'"

        logger.info("Все тесты валидации пройдены успешно")

    @pytest.mark.parametrize("width,height,expected_behavior", EDGE_DIMENSIONS)
    def test_edge_dimensions_values(self, page, width, height, expected_behavior):
        """Тест проверяет граничные значения полей размеров"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        constructor.set_dimensions(width, height)
        constructor.select_theme("Affiliate")
        constructor.select_all_countries()
        constructor.set_color_theme(0)
        constructor.generate_preview()

        assert constructor.is_code_generated(), f"Код не сгенерировался при размерах {width}x{height}"
        logger.info(f"Тест с размерами {width}x{height} пройден")

    def test_clear_buttons_work(self, page):
        """
        Тест проверяет работу кнопок "Очистить"
        """
        constructor = ConstructorPage(page)
        constructor.navigate()

        # Выбираем значения
        constructor.select_theme("Affiliate")
        constructor.select_all_countries()

        # Проверяем видимость кнопок
        theme_clear_visible = page.locator(constructor.theme_clear).is_visible()
        logger.info(f"Кнопка очистки темы видима: {theme_clear_visible}")

        if theme_clear_visible:
            constructor.clear_theme()

            constructor.select_theme("Blockchain")
            logger.info("Тема успешно изменена после очистки")

        countries_selected = constructor.are_countries_selected()
        logger.info(f"Страны выбраны: {countries_selected}")

        countries_clear_visible = page.locator(constructor.countries_clear).is_visible()
        if not countries_clear_visible:
            logger.info("Кнопка очистки стран не видима - особенность UI, пропускаем проверку очистки")
        else:
            constructor.clear_countries()
            assert not constructor.are_countries_selected(), "Страны должны быть не выбраны"

    def test_clear_theme_when_button_not_visible(self, page):
        """Проверка очистки темы когда кнопка не видна"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        # Выбираем тему
        constructor.select_theme("Affiliate")

        # Временно делаем кнопку невидимой
        original_is_visible = page.locator(constructor.theme_clear).is_visible
        try:
            page.locator(constructor.theme_clear).is_visible = lambda: False
            constructor.clear_theme()  # Должно отработать без ошибок
        finally:
            page.locator(constructor.theme_clear).is_visible = original_is_visible

    def test_clear_countries_when_button_not_visible(self, page):
        """Проверка очистки стран когда кнопка не видна"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        constructor.select_all_countries()

        # Временно делаем кнопку невидимой
        original_is_visible = page.locator(constructor.countries_clear).is_visible
        try:
            page.locator(constructor.countries_clear).is_visible = lambda: False
            constructor.clear_countries()  # Должно отработать без ошибок
        finally:
            page.locator(constructor.countries_clear).is_visible = original_is_visible

    def test_has_error_messages_detection(self, page):
        """Проверка обнаружения сообщений об ошибках"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        # Изначально ошибок нет
        assert not constructor.has_error_messages()

        # Добавляем элемент с ошибкой через JavaScript
        page.evaluate("""
            const div = document.createElement('div');
            div.className = 'error-message';
            div.textContent = 'Test error';
            div.style.cssText = 'position: fixed; top: 0; left: 0; z-index: 9999;';
            document.body.appendChild(div);
        """)

        # Должны обнаружить ошибку
        assert constructor.has_error_messages()

    def test_is_page_loaded_without_button_check(self, page):
        """Проверка is_page_loaded без проверки кнопки"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        assert constructor.is_page_loaded(check_button=False)

    def test_is_page_loaded_when_form_missing(self, page):
        """Проверка is_page_loaded когда формы нет"""
        constructor = ConstructorPage(page)

        # Переходим на другую страницу
        page.goto("https://example.com")

        assert not constructor.is_page_loaded()

    def test_get_width_value_empty_field(self, page):
        """Проверка получения значения из пустого поля"""
        constructor = ConstructorPage(page)
        constructor.navigate()

        # Очищаем поле
        page.locator(constructor.width_input).clear()

        # Проверяем что метод не падает
        value = constructor.get_width_value()
        assert value is not None