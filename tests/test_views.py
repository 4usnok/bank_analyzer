import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, time
import pandas as pd
from src.views import cur_proc, stock_processing, greetings, stock_prices, exchange_rates, top_trans, for_each_card
import json

# Фикстура для мокирования зависимостей
@pytest.fixture
def mock_dependencies(mocker):
    """Фикстура для мокирования зависимостей."""
    # Мокируем datetime_work
    mocker.patch(
        "src.views.datetime_work",  # Указываем правильный путь к модулю
        return_value=datetime(2023, 1, 6),
    )

    # Мокируем json_read
    mocker.patch(
        "src.views.json_read",  # Указываем правильный путь к модулю
        return_value={"user_stocks": ["AAPL"]},  # Значение по умолчанию
    )

    # Мокируем yf.download
    mock_download = mocker.patch("yfinance.download")
    mock_download.return_value = pd.DataFrame({
        "Close": [150, 155],  # Фиктивные данные по закрытию акции
    }, index=pd.to_datetime(["2023-01-06", "2023-01-07"]))

    # Возвращаем мок-объект для yf.download (если нужно)
    return mock_download

# Тесты для функции cur_proc
@pytest.mark.parametrize(
    "end_date, user_currencies, api_response, expected_result, expected_error",
    [
        # Успешный сценарий
        (
            "2023-10-15",  # end_date
            ["USD", "EUR"],  # user_currencies
            [
                MagicMock(status_code=200, json=lambda: {"data": {"USD": 1.0}}),
                MagicMock(status_code=200, json=lambda: {"data": {"EUR": 0.85}}),
            ],  # api_response
            [{"data": {"USD": 1.0}}, {"data": {"EUR": 0.85}}],  # expected_result
            None,  # expected_error
        ),
        # Пустой список валют
        (
            "2023-10-15",  # end_date
            [],  # user_currencies
            [],  # api_response
            None,  # expected_result
            ValueError,  # expected_error
        ),
        # Ошибка API
        (
            "2023-10-15",  # end_date
            ["USD", "EUR"],  # user_currencies
            [
                MagicMock(status_code=500, json=lambda: {"error": "Internal Server Error"}),
                MagicMock(status_code=500, json=lambda: {"error": "Internal Server Error"}),
            ],  # api_response
            [],  # expected_result
            None,  # expected_error
        ),
    ],
)
def test_cur_proc(end_date, user_currencies, api_response, expected_result, expected_error):
    """Тест для функции cur_proc с параметризацией."""
    # Мокируем чтение файла user_settings.json
    with patch(
        "src.views.json_read",  # Указываем правильный путь к модулю
        return_value={"user_currencies": user_currencies},
    ):
        # Мокируем запросы к API
        with patch("requests.get") as mock_get:
            # Настраиваем мок-ответы для каждого запроса
            mock_get.side_effect = api_response

            # Если ожидается ошибка, проверяем, что она возникает
            if expected_error:
                with pytest.raises(expected_error):
                    cur_proc(end_date)
            else:
                # Вызываем функцию и проверяем результат
                result = cur_proc(end_date)
                assert result == expected_result

                # Проверяем, что requests.get был вызван нужное количество раз
                assert mock_get.call_count == len(user_currencies)

# Фикстура для подготовки мок-данных из user_settings.json
@pytest.fixture
def mock_user_settings():
    settings_instance = {
        "user_stocks": ["AAPL"],  # Список акций для тестирования
    }
    return settings_instance

# Тест для проверки корректности работы функции stock_processing
def test_stock_processing(mocker):
    """Тест для функции stock_processing."""
    # Мокируем json_read, чтобы он возвращал фиктивные данные
    mock_user_settings = {"user_stocks": ["AAPL"]}
    mocker.patch("src.views.json_read", return_value=mock_user_settings)

    # Мокируем datetime_work, чтобы он возвращал фиктивную дату
    mocker.patch("src.views.datetime_work", return_value=datetime(2023, 1, 6))

    # Мокируем yf.download, чтобы он возвращал фиктивные данные по акциям
    mock_data = pd.DataFrame({
        "Close": [150, 155],  # Фиктивные данные по закрытию акции
    }, index=pd.to_datetime(["2023-01-06", "2023-01-07"]))
    mocker.patch("yfinance.download", return_value=mock_data)

    # Вызываем тестируемую функцию
    result = stock_processing("2023-01-07")

    # Проверяем результат
    assert result == 150  # Ожидаемое значение цены закрытия

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Тест greetings
# Фикстура для тестирования разных временных диапазонов
@pytest.fixture(params=[
    (time(2, 0, 0), "Доброй ночи"),  # Ночь
    (time(8, 0, 0), "Доброе утро"),  # Утро
    (time(14, 0, 0), "Добрый день"),  # День
    (time(20, 0, 0), "Добрый вечер"),  # Вечер
])
def time_and_greeting(request):
    return request.param

# Тест, который использует фикстуру
def test_greetings(time_and_greeting):
    current_time, expected_greeting = time_and_greeting
    assert greetings(current_time) == expected_greeting

# Тест stock_prices

# Фикстура для мокирования чтения файла user_settings.json
@pytest.fixture
def mock_user_settings(mocker):
    # Тестовые данные
    test_data = {"user_stocks": ["AAPL", "GOOGL"]}

    # Мокируем чтение файла
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(test_data)))

# Фикстура для мокирования yfinance.Ticker
@pytest.fixture
def mock_yfinance(mocker):
    # Мокируем yfinance.Ticker
    mock_ticker = mocker.Mock()
    mock_ticker.history.return_value = pd.DataFrame({"Close": [150.0]})
    mocker.patch("yfinance.Ticker", return_value=mock_ticker)

# Тест для проверки корректного выполнения функции
def test_stock_prices_success(mock_user_settings, mock_yfinance):
    # Ожидаемый результат
    expected_result = [
        {"stock": "AAPL", "price": 150},
        {"stock": "GOOGL", "price": 150},
    ]
    # Вызываем функцию и проверяем результат
    result = stock_prices()
    assert result == expected_result

# Тест для проверки ошибки при пустом списке акций
def test_stock_prices_empty_stocks(mocker):
    # Тестовые данные с пустым списком акций
    test_data = {"user_stocks": []}
    # Мокируем чтение файла
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(test_data)))
    # Вызываем функцию и проверяем, что она возвращает пустой список
    result = stock_prices()
    assert result == []

# Тест для проверки ошибки при чтении файла
def test_stock_prices_file_error(mocker):
    # Мокируем чтение файла с ошибкой
    mocker.patch("builtins.open", side_effect=Exception("Ошибка чтения файла"))
    # Вызываем функцию и проверяем, что она возвращает пустой список
    result = stock_prices()
    assert result == []

# Тест для проверки ошибки при получении данных от yfinance
def test_stock_prices_yfinance_error(mocker):
    # Тестовые данные
    test_data = {"user_stocks": ["AAPL"]}
    # Мокируем чтение файла
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(test_data)))
    # Мокируем yfinance.Ticker с ошибкой
    mock_ticker = mocker.Mock()
    mock_ticker.history.side_effect = Exception("Ошибка получения данных")
    mocker.patch("yfinance.Ticker", return_value=mock_ticker)
    # Вызываем функцию и проверяем, что она возвращает пустой список
    result = stock_prices()
    assert result == []

# Тест exchange_rates
@pytest.fixture
def mock_fixture(mocker):
    # Мокируем json файл
    mock_data = [
        {
            "base": "USD",
            "date": "2021-03-17",
            "rates": {
                "EUR": 0.813399,
                "GBP": 0.72007,
                "JPY": 107.346001
            },
            "timestamp": 1519296206
        }
    ]
    # Используем patch с mock_open
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        yield

def test_exchange_rates_file_not_found(mocker):
    # Мокируем open, чтобы вызвать FileNotFoundError
    mocker.patch("builtins.open", side_effect=FileNotFoundError("Файл не найден"))
    # Вызываем функцию
    result = exchange_rates()
    # Ожидаемый результат (пустой список)
    assert result == []

def test_exchange_rates_invalid_json(mocker):
    # Мокируем open, чтобы вернуть невалидный JSON
    mocker.patch("builtins.open", mock_open(read_data="invalid json"))
    # Вызываем функцию
    result = exchange_rates()
    # Ожидаемый результат (пустой список)
    assert result == []

def test_exchange_rates(mocker):
    # Мокируем данные файла
    mock_data = [
        {
            "base": "USD",
            "date": "2021-03-17",
            "rates": {
                "EUR": 0.813399,
                "GBP": 0.72007,
                "JPY": 107.346001
            },
            "timestamp": 1519296206
        }
    ]
    # Мокируем open и json.load
    mocker.patch("builtins.open", mock_open(read_data=json.dumps(mock_data)))
    # Вызываем функцию
    result = exchange_rates()
    # Ожидаемый результат
    expected_result = [
        {
            "currency": "USD",
            "rate": {
                "EUR": 0.813399,
                "GBP": 0.72007,
                "JPY": 107.346001
            }
        }
    ]
    # Проверяем результат
    assert result == expected_result

# Тест top_trans
@pytest.fixture
def mock_excel_file(mocker):
    """Фикстура для мокирования Excel-файла."""
    # Создаем мок-лист
    mock_sheet = MagicMock()
    mock_sheet.max_row = 6  # Указываем количество строк
    mock_sheet.cell.side_effect = lambda row, col: MagicMock(
        value={
            2: f"2023-10-{row}",  # Дата
            5: row * 100,          # Сумма
            10: f"Category {row}", # Категория
            12: f"Description {row}", # Описание
        }[col]
    )
    # Создаем мок-книгу
    mock_workbook = MagicMock()
    mock_workbook.active = mock_sheet
    # Мокируем openpyxl.load_workbook
    mocker.patch("openpyxl.load_workbook", return_value=mock_workbook)
    # Возвращаем мок-объект книги (если нужно)
    return mock_workbook

def test_top_trans_invalid_data(mocker):
    """Тест для обработки ошибок в данных."""
    # Создаем мок-лист с некорректными данными
    mock_sheet = MagicMock()
    mock_sheet.max_row = 2
    mock_sheet.cell.side_effect = lambda row, col: MagicMock(
        value={
            2: None,  # Некорректная дата
            5: "invalid",  # Некорректная сумма
            10: None,  # Некорректная категория
            12: None,  # Некорректное описание
        }[col]
    )
    # Создаем мок-книгу
    mock_workbook = MagicMock()
    mock_workbook.active = mock_sheet
    # Мокируем openpyxl.load_workbook
    mocker.patch("openpyxl.load_workbook", return_value=mock_workbook)
    # Вызываем функцию
    result = top_trans()
    # Ожидаемый результат (пустой список)
    assert result == []

# Тест for_each_card
@pytest.fixture
def mock_excel_file():
    """Фикстура для мокирования Excel-файла."""
    # Тестовые данные
    data = {
        "Номер карты": ["1234567890123456", "9876543210987654", "1111222233334444"],
        "Сумма операции с округлением": [1000, 500, 300],
    }
    # Создаем DataFrame с тестовыми данными
    df = pd.DataFrame(data)

    # Мокируем pd.read_excel, чтобы возвращать тестовый DataFrame
    with patch("pandas.read_excel", return_value=df):
        yield
def test_for_each_card_missing_columns(mock_excel_file):
    """Тест для обработки ошибок (отсутствие столбцов)."""
    # Мокируем pd.read_excel, чтобы возвращать DataFrame без нужных столбцов
    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        # Вызываем функцию
        result = for_each_card()
        # Ожидаемый результат (пустой список)
        assert result == []