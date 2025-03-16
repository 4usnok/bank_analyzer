import json
import os
from datetime import datetime, timedelta

import requests
import yfinance as yf
from dotenv import load_dotenv


# В функции `cur_proc` использовал https://fixer.io/
def cur_proc(end_date: str):
    """Функция обращается к API и обрабатывает валюты"""
    # Преобразуем строку в объект datetime
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    start_date = end_date.replace(
        day=1
    )  # Начальная дата — первое число месяца конечной даты

    # Открываем файл с настройками
    with open("../user_settings.json", "r", encoding="utf-8") as file:
        data_file = json.load(file)

    # Получаем список валют
    list_from_the_dict = data_file.get("user_currencies", [])

    # Проверяем, что список валют не пустой
    if not list_from_the_dict:
        raise ValueError("Список валют 'user_currencies' пуст или отсутствует в файле.")

    results = []  # Список для хранения результатов

    # Генерируем список дат от start_date до end_date
    current_date = start_date
    date_str = current_date.strftime("%Y-%m-%d")  # Преобразуем дату в строку
    # Итерируемся по каждой валюте в списке
    for cur_from_the_dict in list_from_the_dict:
        # Формируем API-запрос
        load_dotenv("../.env")  # Загрузите переменные из .env файла
        api_key_cur = os.getenv("api_key_cur")  # Получите API ключ
        api_link = f"https://data.fixer.io/api/{date_str}?access_key={api_key_cur}"
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
                f"Ошибка при запросе для базовой валюты {cur_from_the_dict} на дату {date_str}: {response.status_code}"
            )
    current_date += timedelta(days=1)  # Переходим к следующему дню

    # Сохраняем результаты в файл
    with open("../work_file_cur.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    return results


# В функции `stock_processing` использовал https://finance.yahoo.com/
def stock_processing(end_date: str):
    # Поработаем с датами:
    end_date = "2023-01-06"  # преобразуем строку в объект datetime
    end_date_obj = datetime.strptime(
        end_date, "%Y-%m-%d"
    )  # Преобразуем end_date в объект datetime
    start_date_obj = end_date_obj.replace(
        day=1
    )  # Вычисляем start_date как первое число месяца
    start_date = start_date_obj.strftime(
        "%Y-%m-%d"
    )  # Преобразуем start_date обратно в строку (если нужно)

    # Открываем файл с настройками
    with open("../user_settings.json", "r", encoding="utf-8") as file:
        data_file = json.load(file)

    # Получаем список акций
    list_from_the_dict = data_file.get("user_stocks", [])
    for one_stocks in list_from_the_dict:
        # Проверяем, что список акций не пустой
        if not list_from_the_dict:
            raise ValueError("Список акций 'user_stocks' пуст или отсутствует в файле.")
            # Итерируемся по каждой акции в списке
        # Формируем API-запрос
        data = yf.download(one_stocks, start=start_date, end=end_date)
        data_dict = data.reset_index().to_dict(orient="records")
        # Загружаем данные по акции для всего диапазона дат
        ticker = one_stocks  # Пример тикера
        results = {  # Создаем структуру JSON
            "stock": ticker,
            "data": data_dict,  # Используем преобразованный список словарей
        }

        return results["data"][0][("Close", one_stocks)]
