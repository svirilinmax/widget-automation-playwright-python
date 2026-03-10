import logging

from pages.constructor_page import ConstructorPage

logger = logging.getLogger(__name__)


class TestNegativeScenarios:
    """Негативные сценарии для страницы конструктора"""

    def test_empty_theme_selection(self, page):
        """
        Проверка поведения при попытке генерации без выбора темы
        """
        constructor = ConstructorPage(page)
        constructor.navigate()

        constructor.select_all_countries()
        constructor.set_dimensions("460", "1000")
        constructor.set_color_theme(0)
        constructor.generate_preview()

        assert constructor.is_code_generated(), "Код должен сгенерироваться (особенность UI)"
        logger.info("Код сгенерировался без выбора темы - задокументированная особенность")

    def test_empty_countries_selection(self, page):
        """
        Проверка поведения при попытке генерации без выбора стран
        """
        constructor = ConstructorPage(page)
        constructor.navigate()

        constructor.select_theme("Affiliate")
        constructor.set_dimensions("460", "1000")
        constructor.set_color_theme(0)
        constructor.generate_preview()

        assert constructor.is_code_generated(), "Код должен сгенерироваться (особенность UI)"
        logger.info("Код сгенерировался без выбора стран - задокументированная особенность")
