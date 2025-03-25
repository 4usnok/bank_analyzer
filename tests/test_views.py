from unittest.mock import patch, MagicMock
from datetime import datetime, time
import pandas as pd
from src.views import (greetings, for_each_card, top_trans,
                       cur_proc, stock_processing, main_views,
                       get_period_transaction)
import pytest
import json
import numpy as np


# Тестирование функции greetings
def test_greetings_night():
    """Тестируем приветствие для ночного времени (00:00-06:00)"""
    test_times = [
        time(0, 0), time(5, 59)  # 05:59
    ]
    for t in test_times:
        with patch('src.views.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = t
            assert greetings() == "Доброй ночи"

def test_greetings_night():
    """Тестируем приветствие для утреннего времени (00:06-12:00)"""
    test_times = [time(6, 0), time(11, 59)]
    for t in test_times:
        with patch('src.views.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = t
            assert greetings() == "Доброе утро"

def test_greetings_day():
    """Тестируем приветствие для дневного времени (12:00-18:00)"""
    test_times = [
        time(12, 0), time(17, 59)]
    for t in test_times:
        with patch('src.views.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = t
            assert greetings() == "Добрый день"

def test_greetings_evening():
    """Тестируем приветствие для вечернего времени (18:00-00:00)"""
    test_times = [time(18, 0), time(23, 59)]
    for t in test_times:
        with patch('src.views.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = t
            assert greetings() == "Добрый вечер"

def test_greetings_morning():
    """Тестируем приветствие для ночного времени (06:00-12:00)"""
    test_times = [
        time(6, 0), time(9, 15), time(11, 59)]
    for t in test_times:
        with patch('src.views.datetime') as mock_datetime:
            mock_datetime.now.return_value.time.return_value = t
            assert greetings() == "Доброе утро"

# Тестирование функции get_period_transaction
# Тестовые данные
TEST_DATA = {
    "Дата операции": [
        "01.01.2023 12:00:00",
        "02.01.2023 12:00:00",
        "03.01.2023 12:00:00",
        "04.01.2023 12:00:00"
    ],
    "Сумма": [100, 200, 300, 400]
}
@pytest.fixture
def test_df():
    """Фикстура с тестовыми данными"""
    return pd.DataFrame(TEST_DATA)
@patch('src.views.obj_datetime')
def test_get_period_transaction_empty_result(test_df):
    """Тест случая, когда нет транзакций за период"""
    with patch('src.views.obj_datetime', return_value=datetime(2023, 1, 10)):
        result = get_period_transaction(test_df, "10.01.2023 12:00:00")
        assert len(result) == 0

def test_get_period_transaction_invalid_date(test_df):
    """Тест обработки невалидной даты"""
    with patch('src.views.obj_datetime', side_effect=ValueError("Invalid date")):
        result = get_period_transaction(test_df, "invalid_date")
        assert len(result) == 0  # Должен вернуть пустой DataFrame при ошибке


# Тестирование функции for_each_card
def test_for_each_card_normal_case():
    """Тест нормального случая с валидными данными"""
    # 1. Подготовка тестовых данных
    test_data = {
        "Номер карты": ["1234567890123456", "9876543210987654", "5555666677778888"],
        "Сумма операции с округлением": [100, 200, 300]
    }
    test_df = pd.DataFrame(test_data)

    # 2. Вызов функции
    result = for_each_card(test_df)

    # 3. Проверки
    assert len(result) == 3
    assert result[0]["last_digits"] == "3456"
    assert result[0]["total_spent"] == 100
    assert result[0]["cashback"] == 1
    assert result[0]["transactions_count"] == 1

def test_for_each_card_empty_df():
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame()
    result = for_each_card(empty_df)
    assert result == []

def test_for_each_card_with_none():
    """Тест с None в номерах карт"""
    test_data = {
        "Номер карты": ["1234567890123456", None, np.nan],
        "Сумма операции с округлением": [100, 200, 300]
    }
    test_df = pd.DataFrame(test_data)

    result = for_each_card(test_df)
    assert len(result) == 1

# Тестирование функции top_trans
# Подготовим DataFrame для тестирования
TEST_DATA = pd.DataFrame({
    "Дата платежа": ["01.10.2023 12:00:00", "15.10.2023 14:00:00", "16.10.2023 10:00:00", "20.10.2023 18:00:00"],
    "Сумма операции с округлением": [1000, 500, 200, 1500],
    "Категория": ["Еда", "Транспорт", "Развлечения", "Еда"],
    "Описание": ["Обед", "Такси", "Кино", "Ужин"],
})


def test_top_trans_no_data():
    """Тест для случая, когда данные отсутствуют."""
    # Мокируем pd.read_excel, чтобы возвращать пустой DataFrame
    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        # Вызываем функцию с тестовой датой
        result = top_trans("02.10.2023 12:00:00")

        # Ожидаемый результат (пустой список)
        assert result == []

# Тестирование функции cur_proc
@patch('src.views.json_read')
@patch('src.views.requests.get')
def test_cur_proc_success(mock_get, mock_json_read):
    """Тестируем успешное получение курсов валют"""
    # 1. Подготовка тестовых данных
    test_currencies = ["USD", "GBP"]
    mock_json_read.return_value = {"user_currencies": test_currencies}

    # 2. Мокируем ответ API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rates": {"USD": 1.08, "GBP": 0.85}
    }
    mock_get.return_value = mock_response

    # 3. Вызов тестируемой функции
    result = cur_proc()

    # 4. Проверки
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 1.08
    assert result[1]["currency"] == "GBP"
    assert result[1]["rate"] == 0.85

# Тестирование функции stock_processing
@patch('src.views.json_read')
@patch('src.views.yf.Ticker')
def test_stock_processing_success(mock_ticker, mock_json_read):
    """Тест успешного получения данных по акциям"""
    # 1. Настраиваем моки
    mock_json_read.return_value = {"user_stocks": ["AAPL", "GOOG"]}

    # 2. Создаем мок для данных акций
    mock_data = MagicMock()
    mock_data.empty = False
    mock_data.__getitem__.return_value.iloc.__getitem__.return_value = 150.25

    # 3. Настраиваем возвращаемые значения
    mock_stock = MagicMock()
    mock_stock.history.return_value = mock_data
    mock_ticker.return_value = mock_stock

    # 4. Вызываем функцию
    result = stock_processing()

    # 5. Проверяем результат
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.25
    assert result[1]["stock"] == "GOOG"

# Тестирование функции main_views
def test_main_views():
    """Тест для функции main_views."""
    # Создаем тестовые данные для транзакций
    test_transactions = MagicMock()

    with patch("src.views.greetings", return_value="Добрый день") as mock_greetings, \
            patch("src.views.get_all_transactions", return_value=test_transactions) as mock_get_all, \
            patch("src.views.get_period_transaction", return_value=test_transactions) as mock_get_period, \
            patch("src.views.for_each_card", return_value=[{"card": "1234", "spent": 1000}]) as mock_cards, \
            patch("src.views.top_trans", return_value=[{"transaction": "top1", "amount": 500}]) as mock_top_trans, \
            patch("src.views.cur_proc", return_value=[{"currency": "USD", "rate": 1.05}]) as mock_cur_proc, \
            patch("src.views.stock_processing", return_value=[{"stock": "AAPL", "price": 150.0}]) as mock_stocks, \
            patch("src.views.obj_datetime", return_value=datetime(2023, 10, 15)) as mock_obj_datetime:
        # Вызываем функцию
        result = main_views("15.10.2023 12:00:00")  # Предполагаемый формат даты

        # Преобразуем результат в dict для удобства проверки
        result_dict = json.loads(result)

        # Проверяем основные поля
        assert result_dict["greeting"] == "Добрый день"
        assert result_dict["cards"] == [{"card": "1234", "spent": 1000}]
        assert result_dict["top_transactions"] == [{"transaction": "top1", "amount": 500}]
        assert result_dict["currency_rates"] == [{"currency": "USD", "rate": 1.05}]
        assert result_dict["stock_prices"] == [{"stock": "AAPL", "price": 150.0}]