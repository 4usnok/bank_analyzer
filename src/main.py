from src.views import cur_proc, stock_processing
from src.home_page import main_home_page
from src.services import favorable_categories_of_increased_cashback
from src.reports import function_for_generating
import pandas as pd

# Проверка модуля views для задания: Веб-страницы
# print(stock_processing('2023-10-15'))
# print(cur_proc('2023-10-15'))

# Проверка модуля home_page для задания: Веб-страницы
# print(main_home_page())

# Проверка модуля services для задания: Сервисы
# path_to_file = "../data/operations.xlsx"  # путь к xlsx
# print(favorable_categories_of_increased_cashback(10, 2021, path_to_file))

# Проверка модуля reports для задания: Отчеты
# df_orders = pd.read_excel("../data/operations.xlsx")
# print(function_for_generating(df_orders, 'Различные товары', '31.12.2021 16:44:00'))