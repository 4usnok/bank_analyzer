import os
import logging
import functools
import pandas as pd
from datetime import timedelta
from typing import Callable, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Переменные окружения
path_to_xlsx = os.getenv("PATH_TO_XLSX")  # Путь к файлу с транзакциями
path_to_logs = os.getenv("PATH_TO_LOGS")  # Путь к файлу логов

# Настройка логирования
reports_logger = logging.getLogger("reports")

# Проверка и создание директории для логов, если она не существует
log_directory = os.path.dirname(path_to_logs)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Очистка существующих обработчиков (если они есть)
reports_logger.handlers.clear()

# Обработчик для записи логов в файл
file_handler = logging.FileHandler(path_to_logs, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)

# Установка уровня логирования
reports_logger.setLevel(logging.DEBUG)

# Логируем успешную настройку логирования
reports_logger.info("Настройка логирования для reports прошла успешно")


def export_to_file(filename: Optional[str] = None):
    """
    Декоратор для экспорта результата функции в файл.
    Поддерживает JSON, CSV и Excel.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Вызываем оригинальную функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename:
                output_filename = filename
            else:
                output_filename = f"{func.__name__}_report.json"  # Имя по умолчанию

            # Экспортируем результат в файл
            if output_filename.endswith(".json"):
                result.to_json(output_filename, orient="records", force_ascii=False, indent=4)
            elif output_filename.endswith(".csv"):
                result.to_csv(output_filename, index=False)
            elif output_filename.endswith(".xlsx"):
                result.to_excel(output_filename, index=False)
            else:
                raise ValueError("Неподдерживаемый формат файла. Используйте .json, .csv или .xlsx.")

            reports_logger.info(f"Отчёт успешно экспортирован в файл: {output_filename}")
            return result

        return wrapper

    return decorator


@export_to_file(filename="../reports_save.json")
def function_for_generating(
        transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Функция для формирования отчёта по тратам в определённой категории
    за последние три месяца.
    """
    reports_logger.info(
        f"Начало выполнения функции function_for_generating "
        f"для категории '{category}' и даты '{date}'"
    )

    # Фильтруем по категории
    filtering_by_category = transactions[transactions["Категория"] == category].copy()
    reports_logger.info(
        f"Найдено {len(filtering_by_category)} записей по категории '{category}'"
    )

    # Если дата передана, фильтруем за последние три месяца
    if date:
        current_date = pd.to_datetime(date, format="%d.%m.%Y %H:%M:%S")
        three_months_ago = current_date - timedelta(days=90)
        reports_logger.info(
            f"Текущая дата: {current_date}, три месяца назад: {three_months_ago}"
        )

        # Преобразуем столбец 'Дата операции' в datetime
        filtering_by_category.loc[:, "Дата операции"] = pd.to_datetime(
            filtering_by_category["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )

        # Фильтруем по датам
        filtering_by_category = filtering_by_category[
            (filtering_by_category["Дата операции"] >= three_months_ago)
            & (filtering_by_category["Дата операции"] <= current_date)
            ]
        reports_logger.info(
            f"Найдено {len(filtering_by_category)} записей за последние три месяца"
        )

    # Фильтруем по тратам (сумма операции < 0)
    filtering_by_spending = filtering_by_category[
        filtering_by_category["Сумма операции"] < 0
        ]
    reports_logger.info(
        f"Найдено {len(filtering_by_spending)} записей с тратами"
    )

    return filtering_by_spending


# Загрузка данных из Excel
try:
    transactions = pd.read_excel(path_to_xlsx)
    reports_logger.info(f"Данные успешно загружены из файла: {path_to_xlsx}")
except Exception as e:
    reports_logger.error(f"Ошибка при загрузке данных из файла: {e}")
    raise
