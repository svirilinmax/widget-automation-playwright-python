# Тестовые данные для проверки полей ввода
DIMENSIONS_TEST_CASES = [
    {"input": "-100", "expected": "230", "description": "отрицательное число"},
    {"input": "abc", "expected": "230", "description": "текст"},
    {"input": "0", "expected": "230", "description": "ноль"},
    {"input": "   ", "expected": "230", "description": "пробелы"},
    {"input": "!@#", "expected": "230", "description": "спецсимволы"},
    {"input": "500", "expected": "500", "description": "корректное значение"},
    {"input": "", "expected": "230", "description": "пустая строка"},
    {"input": "1000", "expected": "1000", "description": "максимальное значение"},
]

# Граничные значения для параметризованных тестов
EDGE_DIMENSIONS = [
    ("-100", "600", "accept"),
    ("0", "600", "accept"),
    ("9999", "600", "accept"),
]

# Темы для выбора
THEMES = ["Affiliate", "Blockchain", "Development", "Igaming"]


def get_test_data(data_set):
    """Получить тестовые данные по имени набора"""
    data_sets = {
        "dimensions": DIMENSIONS_TEST_CASES,
        "edge": EDGE_DIMENSIONS,
        "themes": THEMES,
    }
    return data_sets.get(data_set, [])
