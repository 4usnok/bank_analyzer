import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, time
import pandas as pd
from src.views import greetings, for_each_card, top_trans, cur_proc, stock_processing, main_views
import json

# Тестирование функции greetings
@pytest.mark.parametrize(
    "time_str, expected_greeting",
    [
        ("2023-10-15 00:00:00", "Доброй ночи"),  # Граничное значение (начало ночи)
        ("2023-10-15 03:00:00", "Доброй ночи"),  # Ночь
        ("2023-10-15 05:59:59", "Доброй ночи"),  # Граничное значение (конец ночи)
        ("2023-10-15 06:00:00", "Доброе утро"),  # Граничное значение (начало утра)
        ("2023-10-15 08:00:00", "Доброе утро"),  # Утро
        ("2023-10-15 11:59:59", "Доброе утро"),  # Граничное значение (конец утра)
        ("2023-10-15 12:00:00", "Добрый день"),  # Граничное значение (начало дня)
        ("2023-10-15 15:00:00", "Добрый день"),  # День
        ("2023-10-15 17:59:59", "Добрый день"),  # Граничное значение (конец дня)
        ("2023-10-15 18:00:00", "Добрый вечер"),  # Граничное значение (начало вечера)
        ("2023-10-15 20:00:00", "Добрый вечер"),  # Вечер
        ("2023-10-15 23:59:59", "Добрый вечер"),  # Граничное значение (конец вечера)
    ],
)
def test_greetings(time_str, expected_greeting):
    """Тест для функции greetings с параметризацией."""
    result = greetings(time_str)
    assert result == expected_greeting

# Тест для проверки обработки некорректных данных
def test_greetings_invalid_input():
    """Тест для проверки обработки некорректных данных."""
    with pytest.raises(ValueError):
        greetings("неправильный формат времени")

# Тестирование функции for_each_card
TEST_DATA = pd.DataFrame({
    "Дата операции": ["15.10.2023 12:00:00", "15.10.2023 14:00:00", "16.10.2023 10:00:00"],
    "Номер карты": ["1234567890123456", "9876543210987654", "1111222233334444"],
    "Сумма операции с округлением": [1000, 500, 200],
})

def test_for_each_card_no_data():
    """Тест для случая, когда данные отсутствуют."""
    # Мокируем pd.read_excel, чтобы возвращать пустой DataFrame
    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        # Вызываем функцию с тестовой датой
        result = for_each_card("2023-10-15 12:00:00")

        # Ожидаемый результат (пустой список)
        assert result == []


def test_for_each_card_invalid_data():
    """Тест для случая с некорректными данными."""
    # Мокируем pd.read_excel, чтобы возвращать DataFrame с некорректными данными
    invalid_data = pd.DataFrame({
        "Дата операции": ["15.10.2023 12:00:00"],
        "Номер карты": [None],  # Некорректные данные
        "Сумма операции с округлением": ["invalid"],  # Некорректные данные
    })
    with patch("pandas.read_excel", return_value=invalid_data):
        # Вызываем функцию с тестовой датой
        result = for_each_card("2023-10-15 12:00:00")

        # Ожидаемый результат (пустой список, так как данные некорректны)
        assert result == []

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
FAKE_API_RESPONSE_USD = {
    "success": True,
    "timestamp": 1697308800,
    "base": "EUR",
    "date": "2023-10-15",
    "rates": {
        "USD": 1.05,
    }
}

FAKE_API_RESPONSE_GBP = {
    "success": True,
    "timestamp": 1697308800,
    "base": "EUR",
    "date": "2023-10-15",
    "rates": {
        "GBP": 0.85,
    }
}

def test_cur_proc():
    """Тест для функции cur_proc с успешным ответом от API."""
    # Мокируем requests.get, чтобы возвращать фиктивные ответы от API
    with patch("requests.get") as mock_get:
        # Настраиваем мок-ответы для каждого запроса
        mock_response_usd = MagicMock()
        mock_response_usd.json.return_value = FAKE_API_RESPONSE_USD

        mock_response_gbp = MagicMock()
        mock_response_gbp.json.return_value = FAKE_API_RESPONSE_GBP

        # Настраиваем side_effect для последовательных вызовов
        mock_get.side_effect = [mock_response_usd, mock_response_gbp]

        # Мокируем json_read, чтобы возвращать фиктивные валюты
        with patch("src.views.json_read", return_value={"user_currencies": ["USD", "GBP"]}):
            # Мокируем obj_datetime, чтобы возвращать фиктивную дату
            with patch("src.views.obj_datetime", return_value=datetime(2023, 10, 15, 12, 0, 0)):
                # Вызываем функцию с тестовой датой
                result = cur_proc("2023-10-15 12:00:00")

                # Ожидаемый результат
                expected_result = [
                    {"currency": "USD", "rate": 1.05},
                    {"currency": "GBP", "rate": 0.85},
                ]

                # Проверяем результат
                assert result == expected_result

# Тестирование функции stock_processing
FAKE_STOCK_DATA = {
    "Close": [150.0, 155.0],  # Цены закрытия
}

def test_stock_processing():
    """Тест для функции stock_processing с успешным ответом от API."""
    # Мокируем, чтобы возвращать фиктивные данные
    with patch("yfinance.Ticker") as mock_ticker:
        # Настраиваем мок-объект
        mock_stock = MagicMock()
        mock_stock.history.return_value = MagicMock(
            iterrows=lambda: [
                (datetime(2023, 10, 15), {"Close": 150.0}),
                (datetime(2023, 10, 16), {"Close": 155.0}),
            ]
        )
        mock_ticker.return_value = mock_stock

        # Мокируем json_read, чтобы возвращать фиктивные акции
        with patch("src.views.json_read", return_value={"user_stocks": ["AAPL", "GOOGL"]}):
            # Мокируем obj_datetime, чтобы возвращать фиктивную дату
            with patch("src.views.obj_datetime", return_value=datetime(2023, 10, 15, 12, 0, 0)):
                # Вызываем функцию с тестовой датой
                result = stock_processing("2023-10-15 12:00:00")

                # Ожидаемый результат
                expected_result = [
                    {"stock": "AAPL", "price": 150.0},
                    {"stock": "AAPL", "price": 155.0},
                    {"stock": "GOOGL", "price": 150.0},
                    {"stock": "GOOGL", "price": 155.0},
                ]

                # Проверяем результат
                assert result == expected_result

# Тестирование функции main_views
def test_main_views():
    """Тест для функции main_home_page."""
    # Мокируем все зависимости
    with patch("src.views.greetings", return_value="Добрый день") as mock_greetings, \
         patch("src.views.for_each_card", return_value=[{"card": "1234", "spent": 1000}]) as mock_cards, \
         patch("src.views.top_trans", return_value=[{"transaction": "top1", "amount": 500}]) as mock_top_trans, \
         patch("src.views.cur_proc", return_value=[{"currency": "USD", "rate": 1.05}]) as mock_cur_proc, \
         patch("src.views.stock_processing", return_value=[{"stock": "AAPL", "price": 150.0}]) as mock_stock_processing:

        # Вызываем функцию с тестовым временем
        result = main_views("2023-10-15 12:00:00")

        # Ожидаемый результат
        expected_response = {
            "greeting": "Добрый день",
            "cards": [{"card": "1234", "spent": 1000}],
            "top_transactions": [{"transaction": "top1", "amount": 500}],
            "currency_rates": [{"currency": "USD", "rate": 1.05}],
            "stock_prices": [{"stock": "AAPL", "price": 150.0}],
        }
        expected_result = json.dumps(expected_response, ensure_ascii=False, indent=4)

        # Проверяем результат
        assert result == expected_result