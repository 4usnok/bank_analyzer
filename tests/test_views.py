from src.views import cur_proc, stock_processing
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd


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
        return_value={"user_stocks": ["AAPL", "GOOGL"]},  # Значение по умолчанию
    )

    # Мокируем yf.download
    mock_download = mocker.patch("yfinance.download")
    mock_download.return_value = MagicMock(
        reset_index=MagicMock(return_value=MagicMock(to_dict=MagicMock(return_value=[]))
    ))

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
    return {
        "user_stocks": ["AAPL", "GOOGL"],  # Список акций для тестирования
    }

# Тест для проверки корректности работы функции
def test_stock_processing(mocker, mock_user_settings):
    # Мокируем json_read, чтобы он возвращал подготовленные данные
    mocker.patch("views.json_read", return_value=mock_user_settings)

    # Мокируем datetime_work, чтобы он возвращал фиктивную дату
    mocker.patch("views.datetime_work", return_value=datetime(2023, 1, 6))

    # Мокируем yf.download, чтобы он возвращал фиктивные данные по акциям
    mock_data = pd.DataFrame({
        "Close": [150, 155],  # Фиктивные данные по закрытию акций
    }, index=pd.to_datetime(["2023-01-06", "2023-01-07"]))
    mocker.patch("yfinance.download", return_value=mock_data)

    # Вызываем тестируемую функцию
    result = stock_processing("2023-01-07")

    # Проверяем, что функция вернула корректное значение
    assert result == 150  # Ожидаемое значение закрытия акции

def test_stock_processing_empty_stocks():
    # Мокируем json_read, чтобы он возвращал пустой список акций
    with patch("views.json_read", return_value={"user_stocks": []}):
        # Проверяем, что функция выбрасывает исключение
        with pytest.raises(ValueError, match="Список акций 'user_stocks' пуст или отсутствует в файле."):
            stock_processing("2023-01-07")

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])