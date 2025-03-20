import json
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

path_to_xlsx = os.getenv("PATH_TO_US_SET")


def json_read(file):
    """Чтение файла с настройками"""
    with open(path_to_xlsx, "r", encoding="utf-8") as file:
        data_file = json.load(file)
    return data_file


def datetime_work(date):
    """Преобразуем строку в объект datetime"""
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date.replace(day=1)
    return start_date


def request_api(date_str, api_key_cur):
    """Формируем API-запрос с https://fixer.io/"""
    base_url_cur = os.getenv("BASE_URL_CUR")
    api_key_cur = os.getenv("API_KEY_CUR")  # Получите API ключ
    api_link = f"{base_url_cur}{date_str}?access_key={api_key_cur}"
    return api_link
