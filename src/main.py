import os

import pandas as pd
from dotenv import load_dotenv

from src.home_page import main_home_page
from src.reports import function_for_generating
from src.services import favorable_categories_of_increased_cashback
from src.views import cur_proc, stock_processing

load_dotenv()

path_to_xlsx = os.getenv("PATH_TO_XLSX")

# Проверка модуля views для задания: Веб-страницы
stock_processing('2023-10-15')
cur_proc('2023-10-15')

# Проверка модуля services для задания: Сервисы
print(favorable_categories_of_increased_cashback(10, 2021, path_to_xlsx))

# Проверка модуля reports для задания: Отчеты
df_orders = pd.read_excel(path_to_xlsx)
print(function_for_generating(
    df_orders,
    'Различные товары',
    '31.12.2021 16:44:00'
))
