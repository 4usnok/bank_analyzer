import json
from datetime import datetime, timedelta, time
import requests
import yfinance as yf
from dotenv import load_dotenv
import logging
import pandas as pd
from src.utils import datetime_work, json_read, request_api, path_to_xlsx
import openpyxl
import os

load_dotenv(dotenv_path="../.env")

path_to_set = os.getenv("PATH_TO_US_SET") # "user_settings.json"
path_to_xlsx = os.getenv("PATH_TO_XLSX") # "data/operations.xlsx"
path_to_work_cur = os.getenv("PATH_TO_WORK_CUR") # "work_file_cur.json"

# В функции `cur_proc` использовал https://fixer.io/
def cur_proc(end_date: str):
    """Функция обращается к API и обрабатывает валюты"""
    # Преобразуем строку в объект datetime
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    start_date = end_date.replace(
        day=1
    )  # Начальная дата — первое число месяца конечной даты

    # Воспользуемся функцией json_read из модуля utils.py
    # для чтения файла json с настройками
    data_file = json_read(path_to_set)

    # Получаем список валют
    list_from_the_dict = data_file.get("user_currencies", [])

    # Проверяем, что список валют не пустой
    if not list_from_the_dict:
        raise ValueError("Список валют 'user_currencies'"
                         " пуст или отсутствует в файле.")

    results = []  # Список для хранения результатов

    # Генерируем список дат от start_date до end_date
    current_date = start_date
    date_str = current_date.strftime("%Y-%m-%d")  # Преобразуем дату в строку
    # Итерируемся по каждой валюте в списке
    for cur_from_the_dict in list_from_the_dict:
        # Воспользуемся функцией request_api из utils
        api_link = request_api(date_str, date_str)
        querystring = {
            "symbols": cur_from_the_dict
        }  # Используем валюту из файла user_settings.json
        # Выполняем запрос
        response = requests.get(api_link, params=querystring)
        # Обрабатываем ответ
        if response.status_code == 200:
            results.append(response.json())  # Добавляем результат в список
        else:
            print(
                f"Ошибка при запросе для базовой валюты "
                f"{cur_from_the_dict} на дату {date_str}: "
                f"{response.status_code}"
            )
    current_date += timedelta(days=1)  # Переходим к следующему дню

    # Сохраняем результаты в файл
    with open(path_to_work_cur, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    return results


# В функции `stock_processing` использовал https://finance.yahoo.com/
def stock_processing(end_date: str):
    """
    Функция обращается к API и обрабатывает акции
    :param end_date:
    :return:
    """
    # Воспользуемся функцией datetime_work
    # из модуля utils.py
    # для чтения файла json с настройками
    start_date_obj = datetime_work("2023-01-06")
    start_date = start_date_obj.strftime("%Y-%m-%d")  # Преобразуем start_date обратно в строку (если нужно)

    # Воспользуемся функцией json_read
    # из модуля utils.py для чтения файла json с настройками
    data_file = json_read(path_to_set)
    if data_file is None:
        raise FileNotFoundError("Файл настроек не найден или содержит некорректный JSON.")

    # Получаем список акций
    list_from_the_dict = data_file.get("user_stocks", [])
    if not list_from_the_dict:
        raise ValueError("Список акций 'user_stocks' пуст или отсутствует в файле.")

    # Итерируемся по каждой акции в списке
    for one_stock in list_from_the_dict:
        # Формируем API-запрос
        data = yf.download(one_stock, start=start_date, end=end_date)
        data_dict = data.reset_index().to_dict(orient="records")

        # Загружаем данные по акции для всего диапазона дат
        ticker = one_stock  # Пример тикера
        results = {  # Создаем структуру JSON
            "stock": ticker,
            "data": data_dict,  # Используем преобразованный список словарей
        }

        # Возвращаем цену закрытия для первой записи
        return results["data"][0]["Close"]

def greetings(current_time=None):
    """Функция выводит приветствие, в зависимости от периода времени"""
    if current_time is None:
        current_time = datetime.now().time()

    # Определяем временные диапазоны
    morning_start = time(6, 0, 0)
    day_start = time(12, 0, 0)
    evening_start = time(18, 0, 0)
    night_start = time(0, 0, 0)

    # Определяем, какое сейчас время суток и выводим соответствующее сообщение
    if night_start <= current_time < morning_start:
        return "Доброй ночи"
    elif morning_start <= current_time < day_start:
        return "Доброе утро"
    elif day_start <= current_time < evening_start:
        return "Добрый день"
    elif evening_start <= current_time or current_time < night_start:
        return "Добрый вечер"


def for_each_card() -> None:
    """Функция выводит:
    1) последние 4 цифры карты;
    2) общая сумма расходов;
    3) кешбэк (1 рубль на каждые 100 рублей).
    """
    try:
        # Чтение Excel-файла с помощью pandas
        df = pd.read_excel(path_to_xlsx)

        # Логирование доступных столбцов (для отладки)
        logging.info(f"Доступные столбцы в файле: {df.columns.tolist()}")

        # Проверка наличия нужных столбцов
        required_columns = ["Номер карты", "Сумма операции с округлением"]
        mis_col = [col for col in required_columns if col not in df.columns]

        if mis_col:
            raise ValueError(f"Отсутствуют столбцы: {mis_col}")

        # Выбор нужных строк и столбцов
        # Предполагаем, что данные начинаются со второй строки (индекс 1)
        selected_data = df.loc[1:3, required_columns]

        # Преобразуем данные в список словарей
        for_each_card_list = selected_data.apply(
            lambda row: {
                "last_digits": str(row["Номер карты"]),  # Последние 4 цифры номера карты
                "total_spent": row["Сумма операции с округлением"],
                "cashback": round(row["Сумма операции с округлением"] // 100),
            },
            axis=1,
        ).tolist()

        return for_each_card_list
    except Exception as e:
        logging.error(f"Ошибка при чтении файла Excel: {e}")
        return []


def top_trans() -> None:
    """Функция выводит топ-5 транзакций по сумме платежа."""
    # Обработка xlsx файла из которого будем брать необходимые данные
    workbook = openpyxl.load_workbook(path_to_xlsx)
    sheet = workbook.active
    top_trans_list = []
    # Собираем все транзакции в список
    try:
        for row in range(2, sheet.max_row + 1):  # данные со второй строки
            tr_date = sheet.cell(row=row, column=2).value  # [2] - номер столбца - "date"
            tr_amount = sheet.cell(row=row, column=5).value  # [5] - номер столбца - "amount"
            tr_category = sheet.cell(row=row, column=10).value  # [10] - номер столбца - "category"
            tr_description = sheet.cell(row=row, column=12).value  # [12] - номер столбца - "description"
            top_trans_list.append(
                {
                    "date": tr_date,
                    "amount": tr_amount,
                    "category": tr_category,
                    "description": tr_description,
                }
            )
        # Сортируем список по убыванию суммы (amount)
        top_trans_list.sort(key=lambda x: x["amount"], reverse=True)
        # Возвращаем топ-5 транзакций
        return top_trans_list[:5]
    except Exception as e:
        logging.error(f"Ошибка при чтении файла Excel: {e}")
        return []


def exchange_rates() -> None:
    """Функция выводит курс валют"""
    exchange_rates_list = []
    # Обработка json файла из которого будем брать
    # необходимые данные апи, чтобы лишний раз не тратить вызовы
    try:
        with open(path_to_work_cur, "r", encoding="utf-8") as file:
            data_file = json.load(file)
            # Раскроем список
            for row in data_file:
                list_from_base = row.get("base", [])
                list_from_rates = row.get("rates", [])
                # Заполним словарь в списке и добавим его в итоговый
                exchange_rates_list.append({"currency": list_from_base, "rate": list_from_rates})
        return exchange_rates_list
    except Exception as e:
        logging.error(f"Ошибка при чтении файла JSON: {e}")
        return []


def stock_prices() -> None:
    """Функция выводит стоимость акций из S&P500."""
    try:
        stock_prices_list = []
        # Открываем файл с настройками
        with open(path_to_set, "r", encoding="utf-8") as file:
            data_file = json.load(file)
        # Получаем список акций
        list_from_the_dict = data_file.get("user_stocks", [])
        # Проверяем, что список акций не пустой
        if not list_from_the_dict:
            raise ValueError("'user_stocks' пуст или отсутствует в файле.")
        # Формируем список с данными о ценах акций
        for one_stock in list_from_the_dict:
            # Получаем текущую цену акции
            stock_info = yf.Ticker(one_stock)
            current_price = stock_info.history(period="1d")["Close"].iloc[-1]
            # Преобразуем цену в целое число
            current_price_int = int(round(current_price))  # Округляем и преобразуем в int
            stock_prices_list.append(
                {
                    "stock": one_stock,
                    "price": current_price_int,  # Цена в виде целого числа
                }
            )
        return stock_prices_list
    except Exception as e:
        logging.error(f"Ошибка при получении цен акций: {e}")
        return []


def main_home_page() -> None:
    """Управляющая функция."""
    json_response = {
        "greeting": greetings(),
        "cards": for_each_card(),
        "top_transactions": top_trans(),
        "currency_rates": exchange_rates(),
        "stock_prices": stock_prices(),
    }
    logging.info("Данные успешно собраны.")
    return json_response


# Пример использования
if __name__ == "__main__":
    try:
        response = main_home_page()
        print(response)
    except Exception as e:
        logging.error(f"Ошибка в главной функции: {e}")
