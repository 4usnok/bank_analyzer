import json
import logging
import os
from datetime import datetime, time, timedelta
from typing import Any

import pandas as pd
import requests
import yfinance as yf  # type: ignore  # Добавляем игнорирование проверки типов
from dotenv import load_dotenv

from src.utils import json_read, obj_datetime

load_dotenv(dotenv_path="../.env")

# Настройки и инициализация
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY_CUR")
path_to_set = "user_settings.json"
path_to_xlsx = "../data/operations.xlsx"
path_to_logs = "../logs/app.log"

# Настройка логирования
views_logger = logging.getLogger("views")
log_directory = os.path.dirname(path_to_logs)
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

file_handler = logging.FileHandler(path_to_logs, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s: %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)
views_logger.info("Настройка логирования для views прошла успешно")


def greetings() -> str:
    """Функция выводит приветствие, в зависимости от периода времени"""
    present_time = datetime.now().time()
    views_logger.info(f"Определение приветствия для настоящего времени: {present_time}")
    # Определяем временные периоды
    if time(0, 0) <= present_time < time(6, 0):  # С 00:00 до 06:00
        greet = "Доброй ночи"
        return greet
    elif time(6, 0) <= present_time < time(12, 0):  # С 06:00 до 12:00
        greet = "Доброе утро"
        return greet
    elif time(12, 0) <= present_time < time(18, 0):  # С 12:00 до 18:00
        greet = "Добрый день"
        return greet
    else:  # С 18:00 до 00:00
        greet = "Добрый вечер"
    logging.info(f"Приветствие: {greet}")
    return greet


def get_all_transactions() -> pd.DataFrame:
    """Загружает весь Excel-файл в DataFrame"""
    return pd.read_excel(path_to_xlsx)


def get_period_transaction(all_transactions: pd.DataFrame, date_str: str, days_range: int = 1) -> Any:
    """
    Фильтрует транзакции за период дней от указанной даты

    :param all_transactions: DataFrame с транзакциями
    :param date_str: Дата в формате "%d.%m.%Y %H:%M:%S"
    :param days_range: Количество дней в периоде (по умолчанию 1 день)
    :return: Отфильтрованный DataFrame
    """
    try:
        # Преобразуем входную дату
        end_date = obj_datetime(date_str)
        start_date = end_date - timedelta(days=days_range - 1)

        # Преобразуем даты в DataFrame
        df = all_transactions.copy()
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        # Фильтрация по периоду
        mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
        return df[mask]
    except Exception as e:
        views_logger.error(f"Ошибка фильтрации транзакций: {e}")
        return pd.DataFrame()


def for_each_card(transactions: pd.DataFrame) -> list:
    """Анализирует транзакции по картам"""
    try:
        result = []
        if not transactions.empty:
            # Группируем по картам и считаем сумму
            grouped = transactions.groupby("Номер карты")["Сумма операции с округлением"].agg(["sum", "count"])

            for card, row in grouped.iterrows():
                # Исправленная проверка на NaN/None
                last_digits = (
                    "N/A" if card is None or (isinstance(card, (float, int)) and pd.isna(card)) else str(card)[-4:]
                )
                total_spent = row["sum"]
                cashback = total_spent // 100

                result.append(
                    {
                        "last_digits": last_digits,
                        "total_spent": total_spent,
                        "cashback": cashback,
                        "transactions_count": row["count"],
                    }
                )
        return result
    except Exception as e:
        views_logger.error(f"Ошибка анализа карт: {e}")
        return []


def top_trans(transactions: pd.DataFrame, top_n: int = 5) -> list:
    """Возвращает топ-N транзакций по сумме"""
    try:
        if transactions.empty:
            return []

        top_transactions = transactions.nlargest(top_n, "Сумма операции с округлением")
        return top_transactions[["Дата операции", "Сумма операции с округлением", "Категория", "Описание"]].to_dict(
            "records"
        )
    except Exception as e:
        views_logger.error(f"Ошибка поиска топ-транзакций: {e}")
        return []


def cur_proc() -> Any:
    """Получает актуальные курсы валют"""
    try:
        list_currency = []
        js_read = json_read(path_to_set)

        for cur in js_read["user_currencies"]:
            url = f"{base_url}latest?{api_key}&base=EUR&symbols={cur}"
            response = requests.get(url)
            result = response.json()
            list_currency.append({"currency": cur, "rate": result["rates"][cur]})

        return list_currency
    except Exception as e:
        views_logger.error(f"Ошибка получения курсов валют: {e}")
        return []


def stock_processing() -> list:
    """Получает актуальные данные по акциям"""
    try:
        list_stock = []
        js_read = json_read(path_to_set)

        for stock_symbol in js_read["user_stocks"]:
            stock = yf.Ticker(stock_symbol)
            data = stock.history(period="1d")
            if not data.empty:
                price = round(float(data["Close"].iloc[-1]), 2)
                list_stock.append({"stock": stock_symbol, "price": price})

        return list_stock
    except Exception as e:
        views_logger.error(f"Ошибка получения данных акций: {e}")
        return []


def main_views(time_str: str) -> str:
    """Управляющая функция"""
    try:
        views_logger.info(f"Запуск управляющей функции для времени: {time_str}")

        greeting = greetings()  # Текущее время
        all_transactions = get_all_transactions()
        period_transactions = get_period_transaction(all_transactions, time_str, days_range=1)

        response = {
            "greeting": greeting,
            "cards": for_each_card(period_transactions),
            "top_transactions": top_trans(period_transactions),
            "currency_rates": cur_proc(),
            "stock_prices": stock_processing(),
            "period_info": {
                "start_date": (obj_datetime(time_str) - timedelta(days=0)).strftime("%d.%m.%Y"),
                "end_date": obj_datetime(time_str).strftime("%d.%m.%Y"),
            },
        }

        views_logger.info("Управляющая функция завершена успешно")
        return json.dumps(response, ensure_ascii=False, indent=4, default=str)

    except Exception as e:
        views_logger.error(f"Ошибка в управляющей функции: {e}")
        return json.dumps({"error": str(e)})
