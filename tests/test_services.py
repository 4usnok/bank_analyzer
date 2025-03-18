import pytest
from unittest.mock import patch, MagicMock
import json
from src.services import favorable_categories_of_increased_cashback  # Импортируйте вашу функцию


# Фикстура для мока os.path.exists
@pytest.fixture
def mock_os_path_exists(mocker):
    """Фикстура для мока os.path.exists."""
    with patch("openpyxl.load_workbook") as mock_exists:
        yield mock_exists


# Параметризация для тестирования разных сценариев
@pytest.mark.parametrize(
    "month, year, file_path, expected_result",
    [
        (10, 2021, "fake_file.xlsx", "{}"),  # Файл не существует
        (10, 2021, "none_file.xlsx", "{}"),  # Другой несуществующий файл
    ],
)
def test_file_not_found(mock_os_path_exists, month, year, file_path, expected_result):
    """
    Тестирование на случай отсутствия файла.
    Проверяем, что функция возвращает пустой JSON, если файл не существует.
    """
    # Настраиваем мок, чтобы он возвращал False (файл не существует)
    mock_os_path_exists.return_value = False

    # Вызываем функцию
    result = favorable_categories_of_increased_cashback(month, year, file_path)

    # Проверяем, что результат соответствует ожидаемому
    assert result == expected_result


def test_file_json():
    """Тестирование обработки фейкового Excel-файла и возврата JSON."""
    # Мокируем openpyxl.load_workbook
    with patch("openpyxl.load_workbook") as mock_load_workbook:
        # Создаем мок для книги и листа
        mock_book = MagicMock()
        mock_sheet = MagicMock()

        # Настраиваем мок для возврата данных
        mock_sheet.max_row = 3  # Две строки данных (первая строка — заголовок)
        mock_sheet.cell.side_effect = [
            # Первая строка данных
            MagicMock(value="Категория1"),  # cat_find (столбец J)
            MagicMock(value=0.1),  # pay_find (столбец M)
            MagicMock(value=100),  # amount_find (столбец G)
            MagicMock(value="01.10.2023"),  # date_find (столбец B)
            # Вторая строка данных
            MagicMock(value="Категория2"),  # cat_find (столбец J)
            MagicMock(value=0.2),  # pay_find (столбец M)
            MagicMock(value=200),  # amount_find (столбец G)
            MagicMock(value="01.10.2023"),  # date_find (столбец B)
        ]
        # Настраиваем мок для книги
        mock_book.active = mock_sheet  # book.active вернёт mock_sheet
        mock_load_workbook.return_value = mock_book  # load_workbook вернёт mock_book

        # Вызываем функцию
        result = favorable_categories_of_increased_cashback(10, 2023, "fake_file.xlsx")

        # Ожидаемый JSON
        expected_json = '''{
            "Категория1": -10,
            "Категория2": -40
        }'''

        # Преобразуем JSON в словари и сравниваем
        expected_dict = json.loads(expected_json)
        result_dict = json.loads(result)
        assert result_dict == expected_dict
