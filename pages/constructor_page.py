from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class ConstructorPage:
    """Page Object для страницы конструктора календаря"""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = "https://dev.3snet.info/eventswidget/"

    # Базовые селекторы
    form_selector = "form.constructor__form"
    generate_button = "button.button.green-bg:has-text('Сгенерировать превью')"

    # Селекторы для шагов
    step1_container = "div.constructor__step:has(div:text('Шаг 1'))"
    step2_container = "div.constructor__step:has(div:text('Шаг 2'))"

    # Шаг 1: Тематика
    theme_dropdown = f"{step1_container} .checkselect"
    theme_option = "span:has-text('{theme}')"
    theme_clear = f"{step1_container} .checkselect-clear"

    # Шаг 2: Страны
    countries_dropdown = f"{step2_container} .checkselect"
    countries_clear = f"{step2_container} .checkselect-clear"

    # Для проверки выбранных стран
    selected_countries_count = f"{step2_container} .checkselect-counter"

    # Шаг 3: Размеры
    width_input = "input[name='width']"
    height_input = "input[name='height']"

    # Шаг 4: Цветовая гамма
    color_theme_radios = ".theme-input .radio"

    # Результаты
    preview_container = "div#preview"
    code_textarea = "textarea#code"

    def navigate(self):
        """Открыть страницу конструктора"""
        logger.info(f"Открываем страницу: {self.base_url}")
        self.page.set_default_timeout(60000)

        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            logger.info("Страница загружена (domcontentloaded)")
        except Exception as e:
            logger.warning(f"Первая попытка не удалась: {e}")
            self.page.goto(self.base_url, wait_until="commit", timeout=60000)
            logger.info("Страница загружена (commit)")

        self.page.wait_for_selector(self.form_selector, state="visible", timeout=30000)
        logger.info("Форма найдена, страница успешно загружена")

    def is_page_loaded(self, check_button: bool = True) -> bool:
        """Проверить, что страница загружена корректно"""
        try:
            self.page.wait_for_selector(self.form_selector, state="visible", timeout=5000)
            if check_button:
                self.page.wait_for_selector(self.generate_button, state="visible", timeout=5000)
            return True
        except Exception as e:
            logger.error(f"Страница не загружена: {e}")
            return False

    def select_theme(self, theme_name: str = "Affiliate"):
        """Выбрать тематику"""
        logger.info(f"Выбираем тему: {theme_name}")

        # Открываем дропдаун
        dropdown = self.page.locator(self.theme_dropdown)
        dropdown.click(force=True)
        self.page.wait_for_timeout(500)

        # Выбираем тему
        option_selector = self.theme_option.format(theme=theme_name)
        option = self.page.locator(option_selector).first
        option.click(force=True)

        # Закрываем дропдаун (кликаем вне его)
        self.page.locator(self.form_selector).click()
        logger.info(f"Тема '{theme_name}' выбрана")

    def select_all_countries(self):
        """
        Выбрать все страны
        """
        logger.info("Выбираем все страны")

        # Открываем дропдаун стран
        dropdown = self.page.locator(self.countries_dropdown)
        dropdown.click(force=True)
        logger.debug("Дропдаун стран открыт")

        self.page.wait_for_timeout(1000)

        #Ищем видимый элемент внутри дропдауна для клика
        try:
            box = dropdown.bounding_box()
            if box:
                self.page.mouse.click(box['x'] + 50, box['y'] + box['height'] + 15)
                self.page.wait_for_timeout(500)
                logger.info("Клик по области дропдауна выполнен")

                counter = self.page.locator(self.selected_countries_count).first
                if counter.is_visible() and counter.text_content() != "0":
                    logger.info(f"Страны выбраны, счетчик: {counter.text_content()}")
                    dropdown.click(force=True)
                    return
        except Exception as e:
            logger.warning(f"Клик по области не сработал: {e}")

    def set_dimensions(self, width: str, height: str):
        """Установить ширину и высоту"""
        logger.info(f"Устанавливаем размеры: {width} x {height}")

        width_field = self.page.locator(self.width_input)
        width_field.clear()
        if width:
            width_field.fill(width)

        height_field = self.page.locator(self.height_input)
        height_field.clear()
        if height:
            height_field.fill(height)

        # Убираем фокус с полей
        self.page.locator(self.form_selector).click()

    def get_width_value(self) -> str:
        """Получить текущее значение поля ширины"""
        return self.page.locator(self.width_input).input_value()

    def set_color_theme(self, theme_index: int = 0):
        """Выбрать цветовую тему по индексу"""
        logger.info(f"Выбираем цветовую тему (индекс {theme_index})")
        radio = self.page.locator(self.color_theme_radios).nth(theme_index)
        radio.click()

    def generate_preview(self):
        """Сгенерировать превью"""
        logger.info("Генерируем превью")
        button = self.page.locator(self.generate_button)
        button.click()

        try:
            self.page.wait_for_selector(f"{self.preview_container}:has(*)", timeout=10000)
            logger.info("Превью сгенерировано успешно")
        except Exception as e:
            logger.warning(f"Превью не появилось: {e}")

    def is_code_generated(self) -> bool:
        """Проверить, сгенерировался ли код"""
        try:
            textarea = self.page.locator(self.code_textarea)
            textarea.wait_for(state="visible", timeout=5000)
            code = textarea.input_value()
            return len(code.strip()) > 0
        except Exception as e:
            logger.error(f"Ошибка при проверке кода: {e}")
            return False

    def has_error_messages(self) -> bool:
        """Проверить наличие сообщений об ошибках"""
        error_patterns = [
            "text=ошибк",
            "text=error",
            "text=invalid",
            ".error-message",
        ]

        for pattern in error_patterns:
            try:
                elements = self.page.locator(pattern)
                for i in range(elements.count()):
                    if elements.nth(i).is_visible():
                        return True
            except:
                continue
        return False

    def clear_theme(self):
        """Очистить выбранную тематику"""
        logger.info("Очищаем тематику")
        button = self.page.locator(self.theme_clear)
        if button.is_visible():
            button.click()
            self.page.wait_for_timeout(300)
        else:
            logger.info("Кнопка очистки темы не видима - пропускаем")

    def clear_countries(self):
        """
        Очистить выбранные страны
        """
        logger.info("Пытаемся очистить страны")
        button = self.page.locator(self.countries_clear)

        if button.is_visible():
            button.click()
            self.page.wait_for_timeout(300)
            logger.info("Кнопка очистки стран нажата")
        else:
            logger.info("Кнопка очистки стран не видима - это нормально для данного UI")

    def are_countries_selected(self) -> bool:
        """
        Проверить, выбраны ли страны по счетчику
        """
        try:
            counter = self.page.locator(self.selected_countries_count).first
            if counter.is_visible():
                count_text = counter.text_content()
                return count_text != "0" and count_text is not None
        except:
            pass
        return False