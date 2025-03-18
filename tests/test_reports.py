import json
import pandas as pd
import pytest
from src.reports import function_for_generating  # Замените your_module на имя вашего файла

# Фикстура для тестового DataFrame
@pytest.fixture
def sample_transactions():
    # Тестовые данные
    test_data = {
        "Дата операции": [
            "01.10.2023 12:00:00", "15.11.2023 14:30:00", "20.12.2023 10:00:00",
            "05.09.2023 09:00:00", "25.12.2023 18:00:00"
        ],
        "Категория": [
            "Супермаркет", "Ресторан", "Супермаркет", "Транспорт", "Супермаркет"
        ],
        "Сумма": [100.0, 200.0, 150.0, 50.0, 300.0]
    }
    return pd.DataFrame(test_data)

# Тест 1: Проверка фильтрации по категории без указания даты
def test_filter_by_category(sample_transactions):
    result = function_for_generating(sample_transactions, "Супермаркет")
    result_data = json.loads(result)  # Преобразуем JSON в Python-объект
    assert any(item["Категория"] == "Супермаркет" for item in result_data)  # Проверяем наличие категории

# Тест 2: Проверка фильтрации по категории и дате
def test_filter_by_category_and_date(sample_transactions):
    result = function_for_generating(sample_transactions, "Супермаркет", "25.12.2023 18:00:00")
    result_data = json.loads(result)  # Преобразуем JSON в Python-объект
    assert any(
        item["Категория"] == "Супермаркет" and "2023-12-25" in item["Дата операции"]
        for item in result_data
    )

# Тест 3: Проверка на отсутствие данных по категории
def test_no_data_for_category(sample_transactions):
    result = function_for_generating(sample_transactions, "Кино")
    result_data = json.loads(result)  # Преобразуем JSON в Python-объект
    assert "error" in result_data  # Проверяем наличие ключа "error"
    assert result_data["error"] == "Категория 'Кино' не найдена."  # Проверяем сообщение об ошибке

# Тест 4: Проверка на отсутствие данных за последние три месяца
def test_no_data_for_last_three_months(sample_transactions):
    result = function_for_generating(sample_transactions, "Транспорт", "25.12.2023 18:00:00")
    result_data = json.loads(result)  # Преобразуем JSON в Python-объект
    assert "error" in result_data  # Проверяем наличие ключа "error"
    assert result_data["error"] == "Данные по категории 'Транспорт' за последние три месяца не найдены."  # Проверяем сообщение об ошибке
