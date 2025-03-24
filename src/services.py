import json
import logging
import os
from datetime import datetime
from functools import reduce
from typing import Any

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
path_to_xlsx = os.getenv("PATH_TO_XLSX")
path_to_logs = os.getenv("PATH_TO_LOGS")
# Настройка логирования
services_logger = logging.getLogger("reports")
# Проверка и создание директории для логов, если она не существует
log_directory = os.path.dirname(path_to_logs)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# Обработчик для записи логов в файл
file_handler = logging.FileHandler(path_to_logs, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
services_logger.addHandler(file_handler)
# Установка уровня логирования
services_logger.setLevel(logging.DEBUG)
# Логируем успешную настройку логирования
services_logger.info("Настройка логирования для services прошла успешно")


def filter_transactions_by_date(transactions: Any, month_input: int, year_input: int) -> Any:
    """
    Фильтрует транзакции по месяцу и году.
    """
    services_logger.info("Начало выполнения функции filter_transactions_by_date")

    def filter_fn(transaction: Any) -> Any:
        try:
            # Преобразуем строку в объект datetime
            date_obj = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            # Забираем из даты месяц и год
            return date_obj.month == month_input and date_obj.year == year_input
        except (KeyError, ValueError) as e:
            services_logger.error(f"Ошибка при обработке транзакции: {e}")
            return False

    # Применяем для фильтрации функцию высшего порядка
    filtered_transactions = list(filter(filter_fn, transactions))
    services_logger.info(f"Фильтрация завершена. Отфильтровано {len(filtered_transactions)} транзакций.")
    return filtered_transactions


def sum_cashback_by_category(transactions: Any) -> Any:
    """
    Суммирует кешбэк по категориям.
    """
    services_logger.info("Начало выполнения функции sum_cashback_by_category")

    def reduce_fn(acc: Any, transaction: Any) -> Any:
        try:
            # Забираем из файла необходимые значения
            category = transaction["Категория"]
            cashback = int(transaction["Бонусы (включая кэшбэк)"])
            acc[category] = acc.get(category, 0) + cashback
        except (KeyError, ValueError) as e:
            services_logger.error(f"Ошибка при обработке транзакции: {e}")
        return acc

    # Применяем для суммирования функцию высшего порядка
    category_cashback = reduce(reduce_fn, transactions, {})
    services_logger.info(f"Суммирование завершено. Категории: {category_cashback}")
    return category_cashback


def favorable_categories_of_increased_cashback(month_input: int, year_input: int, list_input: Any) -> Any:
    """
    Основная функция.
    """
    services_logger.info("Начало выполнения функции favorable_categories_of_increased_cashback")

    if not isinstance(list_input, list):
        services_logger.error("list_input должен быть списком словарей.")
        raise ValueError("list_input должен быть списком словарей.")

    # Фильтруем транзакции
    services_logger.info("Начало фильтрации транзакций")
    filtered_transactions = filter_transactions_by_date(list_input, month_input, year_input)

    # Суммируем кешбэк
    services_logger.info("Начало суммирования кешбэка")
    category_cashback = sum_cashback_by_category(filtered_transactions)

    # Возвращаем результат
    services_logger.info("Успешно сформирован JSON с данными")
    return json.dumps(category_cashback, ensure_ascii=False, indent=4)
