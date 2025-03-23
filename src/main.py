import os

import pandas as pd
from dotenv import load_dotenv

from src.reports import function_for_generating
from src.services import favorable_categories_of_increased_cashback
from src.views import main_home_page

load_dotenv()

path_to_xlsx = os.getenv("PATH_TO_XLSX")

# Проверка модуля views для задания: Веб-страницы
print(main_home_page("2021-12-31 16:44:00"))

# Проверка модуля services для задания: Сервисы
# favorable_categories_of_increased_cashback(10, 2021, path_to_xlsx)
#
# # Проверка модуля reports для задания: Отчеты
# df_orders = pd.read_excel(path_to_xlsx)
# print(function_for_generating(
#     df_orders,
#     'Различные товары',
#     '31.12.2021 16:44:00'
# ))
