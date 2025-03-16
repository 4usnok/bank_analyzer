import json
from datetime import datetime, timedelta
import requests
import yfinance as yf
from src.utils import json_read, request_api, datetime_work


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
    data_file = json_read("../user_settings.json")

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
    with open("../work_file_cur.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    return results


# В функции `stock_processing` использовал https://finance.yahoo.com/
def stock_processing(end_date: str):
    # Воспользуемся функцией datetime_work
    # из модуля utils.py
    # для чтения файла json с настройками
    start_date_obj = datetime_work("2023-01-06")
    start_date = start_date_obj.strftime(
        "%Y-%m-%d"
    )  # Преобразуем start_date обратно в строку (если нужно)

    # Воспользуемся функцией json_read
    # из модуля utils.py для чтения файла json с настройками
    data_file = json_read("../user_settings.json")

    # Получаем список акций
    list_from_the_dict = data_file.get("user_stocks", [])
    for one_stocks in list_from_the_dict:
        # Проверяем, что список акций не пустой
        if not list_from_the_dict:
            raise ValueError("Список акций 'user_stocks' пуст "
                             "или отсутствует в файле.")
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
