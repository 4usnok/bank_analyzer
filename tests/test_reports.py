from src.reports import function_for_generating
import pytest
import pandas as pd

# Фикстура с тестовыми данными
@pytest.fixture
def test_transactions():
    return pd.DataFrame({
        "Дата операции": [
            "01.12.2021 10:15:30", "15.12.2021 18:30:45",
            "20.11.2021 12:00:00", "25.12.2021 14:45:00",
            "01.09.2021 10:15:30"
        ],
        "Категория": [
            "Супермаркеты", "Супермаркеты", "АЗС",
            "Рестораны", "Супермаркеты"
        ],
        "Сумма операции": [-500, -300, 200, -200, -100]
    })

def test_filter_by_category(test_transactions):
    """Тест фильтрации по категории"""
    result = function_for_generating(test_transactions, "Супермаркеты")
    # Проверяем что все категории соответствуют фильтру
    assert (result["Категория"] == "Супермаркеты").all()

def test_filter_by_spending(test_transactions):
    """Тест фильтрации по тратам"""
    result = function_for_generating(test_transactions, "Супермаркеты")
    # Проверяем что все суммы отрицательные
    assert (result["Сумма операции"] < 0).all()

def test_no_data_found(test_transactions):
    """Тест для отсутствующей категории"""
    result = function_for_generating(test_transactions, "Несуществующая категория")
    # Проверяем что результат пустой
    assert result.empty

def test_no_date_provided(test_transactions):
    """Тест без указания даты"""
    result = function_for_generating(test_transactions, "Супермаркеты")
    # Двойная проверка
    assert (result["Категория"] == "Супермаркеты").all()
    assert (result["Сумма операции"] < 0).all()

@pytest.mark.parametrize("date_filter,expected_count", [
    ("01.12.2021 00:00:00", 1),  # Добавляем время
    ("15.12.2021 00:00:00", 1),
    (None, 3)  # Все супермаркеты
])
def test_date_filters(test_transactions, date_filter, expected_count):
    result = function_for_generating(test_transactions, "Супермаркеты", date_filter)
    assert len(result) == expected_count