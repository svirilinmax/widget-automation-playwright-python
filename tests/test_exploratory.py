import pytest
from playwright.sync_api import expect


@pytest.mark.skip(reason="Исследовательский тест, не для регулярного запуска")
def test_explore_countries_dropdown(page):
    """Исследуем, что происходит с выпадающим списком стран"""
    page.goto("https://dev.3snet.info/eventswidget/")

    # Находим все элементы с классом checkselect-over
    dropdowns = page.locator(".checkselect-over").all()
    print(f"\nНайдено дропдаунов: {len(dropdowns)}")

    # Кликаем по второму дропдауну (страны)
    if len(dropdowns) >= 2:
        dropdowns[1].click()
        page.wait_for_timeout(2000)

        # Смотрим, что появилось
        all_texts = page.locator(".checkselect-items *").all_text_contents()
        print(f"Все тексты в выпадающем списке: {all_texts}")

        # Делаем скриншот для анализа
        page.screenshot(path="countries_dropdown.png")
        print("Скриншот сохранен как countries_dropdown.png")


# def test_explore_after_generation(page):
#     """Исследуем, что происходит после генерации с некорректными данными"""
#     page.goto("https://dev.3snet.info/eventswidget/")
#
#     # Заполняем форму
#     page.locator(".checkselect-over").first.click()
#     page.get_by_text("Affiliate").click()
#
#     # Выбираем страны
#     page.locator("div:nth-child(2) .checkselect-over").click()
#     page.get_by_text("Выбрать все").nth(1).click()
#
#     # Вводим отрицательную ширину
#     page.locator("input[name='width']").fill("-100")
#     page.locator("input[name='height']").fill("600")
#
#     # Выбираем тему
#     page.locator(".theme-input > label > .radio__square").first.click()
#
#     # Генерируем превью
#     page.get_by_role("button", name="Сгенерировать превью").click()
#
#     # Ждем и проверяем результат
#     page.wait_for_timeout(3000)
#
#     # Проверяем, появился ли фрейм
#     frame = page.locator("[id=\"3snet-frame\"]")
#     print(f"Фрейм видим: {frame.is_visible()}")
#
#     if frame.is_visible():
#         # Пробуем получить контент фрейма
#         try:
#             frame_content = frame.content_frame()
#             print("Фрейм загружен")
#         except:
#             print("Не удалось получить контент фрейма")
#
#     page.screenshot(path="after_negative_width.png")
#     print("Скриншот сохранен")