import json
from datetime import datetime
from dotenv import load_dotenv
import os

path_to_file_json = "../user_settings.json"  # Относительный путь к файлу json


def json_read(file):
    """Чтение файла с настройками"""
    with open(file, "r", encoding="utf-8") as file:
        data_file = json.load(file)
    return data_file


def datetime_work(date):
    """Преобразуем строку в объект datetime"""
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date.replace(day=1)
    return start_date


def request_api(date_str, api_key_cur):
    """Формируем API-запрос с https://fixer.io/"""
    load_dotenv("../.env")  # Загрузите переменные из .env файла
    api_key_cur = os.getenv("api_key_cur")  # Получите API ключ
    api_link = f"https://data.fixer.io/api/{date_str}?access_key={api_key_cur}"
    return api_link
