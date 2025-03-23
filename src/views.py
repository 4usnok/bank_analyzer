import json
from datetime import datetime, timedelta, time

import requests
import yfinance as yf
from dotenv import load_dotenv
from src.utils import json_read, obj_datetime
import openpyxl
import os
import logging
import pandas as pd

load_dotenv(dotenv_path="../.env")

# Переменные окружения
api_key = os.getenv("API_KEY_CUR")
path_to_set = os.getenv("PATH_TO_US_SET") # "user_settings.json"
path_to_xlsx = os.getenv("PATH_TO_XLSX") # "data/operations.xlsx"
path_to_work_cur = os.getenv("PATH_TO_WORK_CUR") # "work_file_cur.json"
path_to_logs = os.getenv("PATH_TO_LOGS") # "../logs/app.log"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(path_to_logs, mode='w'),  # Логи в файл (перезаписываем файл)
        logging.StreamHandler()  # Логи в консоль
    ]
)
logging.info("Логирование настроено.")

def greetings(time_str: str) -> str:
    """Функция выводит приветствие, в зависимости от периода времени"""
    logging.info(f"Определение приветствия для времени: {time_str}")
    # Преобразуем строку в объект используя obj_datetime из utils.py
    time_obj = obj_datetime(time_str).time()
    # Определяем временные периоды
    if time(0, 0) <= time_obj < time(6, 0):  # С 00:00 до 06:00
        greet = 'Доброй ночи'
        return greet
    elif time(6, 0) <= time_obj < time(12, 0):  # С 06:00 до 12:00
        greet = 'Доброе утро'
        return greet
    elif time(12, 0) <= time_obj < time(18, 0):  # С 12:00 до 18:00
        greet = 'Добрый день'
        return greet
    else:  # С 18:00 до 00:00
        greet = 'Добрый вечер'
    logging.info(f"Приветствие: {greet}")
    return greet

def for_each_card(time_str: str) -> list:
    """Функция выводит:
    1) последние 4 цифры карты;
    2) общая сумма расходов;
    3) кешбэк (1 рубль на каждые 100 рублей).
    """
    logging.info(f"Обработка данных карт для времени: {time_str}")
    none_list = []
    try:
        workbook = openpyxl.load_workbook(path_to_xlsx)
        sheet = workbook.active
        # Преобразуем входную дату в формат "%d.%m.%Y %H:%M:%S" для поиска в Excel
        # Преобразуем строку в объект используя obj_datetime из utils.py
        formatted_time_str = obj_datetime(time_str).strftime("%d.%m.%Y %H:%M:%S")
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] == formatted_time_str:
                num_card = row[2]  # последние 4 цифры карты
                amount = row[14]  # общая сумма расходов
                cashback = row[14] // 100  # кешбэк (1 рубль на каждые 100 рублей)
                none_list.append(
                    {
                        "last_digits": num_card,
                        "total_spent": amount,
                        "cashback": cashback
                    }
                )
    except Exception as e:
        logging.error(f"Ошибка при обработке данных карт: {e}")
    return none_list

def top_trans(end_date: str) -> list:
    """Функция выводит топ-5 транзакций по сумме платежа в диапазоне от начала месяца до заданной даты."""
    logging.info(f"Поиск топ-5 транзакций до даты: {end_date}")
    top_list = []
    try:
        workbook = openpyxl.load_workbook(path_to_xlsx)
        sheet = workbook.active
        # Преобразуем end_date в объект datetime
        end_date_obj = obj_datetime(end_date)
        # Определяем начало месяца
        start_date_obj = end_date_obj.replace(day=1, hour=0, minute=0, second=0)
        # Преобразуем start_date и end_date в строки для сравнения
        start_date_str = start_date_obj.strftime("%d.%m.%Y %H:%M:%S")
        end_date_str = end_date_obj.strftime("%d.%m.%Y %H:%M:%S")
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_date = row[1]  # Дата из строки Excel
            if start_date_str <= end_date <= end_date_str:
                amount = row[14]  # общая сумма расходов
                category = row[9]  # категории
                description = row[11]  # описание
                top_list.append(
                    {
                        "date": row_date,
                        "amount": amount,
                        "category": category,
                        "description": description
                    }
                )
            # Сортируем транзакции по сумме платежа (по убыванию)
            top_list.sort(key=lambda x: x["amount"], reverse=True)
    except Exception as e:
        logging.error(f"Ошибка при поиске топ-5 транзакций: {e}")
    # Возвращаем топ-5 транзакций
    return top_list[:5]

def cur_proc(date_str: str):
    """Функция API валют"""
    logging.info(f"Получение курсов валют для даты: {date_str}")
    # В функции `cur_proc` использовал https://fixer.io/
    def exchange_rates():
        """Функция выводит курс валют"""
        list_api = []
        list_currency = []
        # Преобразуем строку в объект используя obj_datetime из utils.py
        input_datetime = obj_datetime(date_str)
        # Извлекаем только дату
        target_date = input_datetime.date()
        # Используем функцию json_read из utils
        js_read = json_read(path_to_set)
        for cur in js_read['user_currencies']:
            url = f"http://data.fixer.io/api/{target_date}?access_key={api_key}&base=EUR&symbols={cur}"
            # К сожалению, базовой функцией по условиям подписки, стала EUR
            response = requests.get(url)
            result = response.json()
            list_api.append(result)
        for cur_in in list_api:
            for key, value in cur_in['rates'].items():
                list_currency.append({
                    "currency": key,
                    "rate": value
                })
        return list_currency

    return exchange_rates()

def stock_processing(date_str: str) -> list:
    """Функция API акций"""
    # В функции `stock_processing` использовал https://finance.yahoo.com/
    logging.info(f"Получение данных акций для даты: {date_str}")
    def stock_prices():
        """Функция выводит стоимость акций из S&P500."""
        list_stock = []
        # Преобразуем строку в объект используя obj_datetime из utils.py
        input_datetime = obj_datetime(date_str)
        # Извлекаем только дату
        target_date = input_datetime.date()
        # Используем функцию json_read из utils
        js_read = json_read(path_to_set)
        for row in js_read["user_stocks"]:
            # Начинаем работу с API
            stock = yf.Ticker(row)
            # Получаем данные за указанную дату
            history = stock.history(start=target_date.strftime("%Y-%m-%d"),
                                    end=(target_date + timedelta(days=1)).strftime("%Y-%m-%d"))
            # Выводим дату и цену закрытия
            for date, price in history.iterrows():
                list_stock.append(
                    {
                        "stock": row,
                        "price": round(float(price['Close']), 2)
                    }
                )
        return list_stock
    # Вызов вложенной функции и возврат её результата
    return stock_prices()


def main_home_page(time_str: str) -> str:
    """Управляющая функция."""
    logging.info(f"Запуск управляющей функции для времени: {time_str}")
    greeting = greetings(time_str)
    cards = for_each_card(time_str)
    top_transactions = top_trans(time_str)
    currency_rates = cur_proc(time_str)
    stock_prices = stock_processing(time_str)
    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    logging.info("Управляющая функция завершена успешно.")
    return json.dumps(response, ensure_ascii=False, indent=4)
