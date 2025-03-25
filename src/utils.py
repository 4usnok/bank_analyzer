import json
from datetime import datetime
from typing import Any

# Относительные пути для файлов
path_to_xlsx = "../user_settings.json"


def json_read(file_path: str) -> Any:
    """Чтение файла с настройками"""
    with open(path_to_xlsx, "r", encoding="utf-8") as file:
        return json.load(file)


def obj_datetime(date: str) -> Any:
    """Преобразуем строку в объект datetime.time()"""
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return end_date
