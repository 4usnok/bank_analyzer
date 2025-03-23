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


def obj_datetime(date):
    """Преобразуем строку в объект datetime.time()"""
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return end_date


