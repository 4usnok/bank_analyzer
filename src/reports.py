import json
import logging
import os
from datetime import timedelta
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Переменные окружения
path_to_xlsx = os.getenv("PATH_TO_XLSX")  # "data/operations.xlsx"
path_to_logs = os.getenv("PATH_TO_LOGS")  # "../logs/app.log"

# Настройка логирования
reports_logger = logging.getLogger("reports")
# Проверка и создание директории для логов, если она не существует
log_directory = os.path.dirname(path_to_logs)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# Обработчик для записи логов в файл
file_handler = logging.FileHandler(path_to_logs, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)  # Исправлено: передаем file_formater
reports_logger.addHandler(file_handler)
# Обработчик для вывода логов в консоль (опционально)
console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formater)
reports_logger.addHandler(console_handler)
# Установка уровня логирования
reports_logger.setLevel(logging.DEBUG)


def function_for_generating(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> str:
    """
    Функция для формирования отчёта по транзакциям
    в определённой категории за последние три месяца.
    """
    logging.info(
        f"Начало выполнения функции reports_func "
        f"для категории '{category}' и даты '{date}'"
    )

    # Если дата передана, фильтруем транзакции за последние три месяца
    if date:
        # Преобразуем строку даты в объект datetime
        current_date = pd.to_datetime(date, format="%d.%m.%Y %H:%M:%S")
        # Вычисляем дату, которая была три месяца назад
        three_months_ago = current_date - timedelta(
            days=90
        )  # Примерно 90 дней для трёх месяцев
        logging.info(
            f"Текущая дата: {current_date}, "
            f"три месяца назад: {three_months_ago}"
        )

        # Фильтруем транзакции по указанной категории
        filtering_by_category = transactions[
            transactions["Категория"] == category
        ].copy()
        logging.info(
            f"Найдено {len(filtering_by_category)} "
            f"записей по категории '{category}'"
        )

        # Преобразуем столбец 'Дата операции' в формат
        # datetime для корректного сравнения дат
        filtering_by_category.loc[:, "Дата операции"] = pd.to_datetime(
            filtering_by_category["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )

        # Фильтруем транзакции за последние три месяца
        filtering_by_date = filtering_by_category[
            (filtering_by_category["Дата операции"] >= three_months_ago)
            & (filtering_by_category["Дата операции"] <= current_date)
        ]
        logging.info(
            f"Найдено {len(filtering_by_date)} записей за последние три месяца"
        )

        # Если данные найдены, преобразуем их в JSON
        if not filtering_by_date.empty:
            result_json = filtering_by_date.to_json(
                orient="records",
                force_ascii=False,
                date_format="iso",
                indent=4
            )
            logging.info("Успешно сформирован JSON с данными")
            return result_json
        else:
            # Если данные не найдены, возвращаем
            # сообщение об ошибке в формате JSON
            error_message = {
                "error": f"Данные по категории '{category}' "
                         f"за последние три месяца не найдены."
            }
            logging.warning(f"Данные не найдены: {error_message}")
            return json.dumps(error_message,
                              ensure_ascii=False,
                              indent=4
                              )
    else:
        # Если дата не передана, фильтруем только по категории
        filtering_by_category = transactions[
            transactions["Категория"] == category
        ]
        logging.info(
            f"Найдено {len(filtering_by_category)} "
            f"записей по категории '{category}'"
        )

        # Если данные найдены, преобразуем их в JSON
        if not filtering_by_category.empty:
            result_json = filtering_by_category.to_json(
                orient="records",
                force_ascii=False,
                date_format="iso",
                indent=4
            )
            logging.info("Успешно сформирован JSON с данными")
            return result_json
        else:
            # Если категория не найдена,
            # возвращаем сообщение об ошибке в формате JSON
            error_message = {"error": f"Категория '{category}' не найдена."}
            logging.warning(f"Категория не найдена: {error_message}")
            return json.dumps(error_message, ensure_ascii=False, indent=4)
