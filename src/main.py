import pandas as pd

from src.reports import function_for_generating
from src.services import favorable_categories_of_increased_cashback
from src.views import main_views

# Относительные пути для файлов
path_to_xlsx = "../data/operations.xlsx"

# Проверка модуля views для задания: Веб-страницы
print(main_views("2021-12-31 16:44:00"))
#
# Проверка модуля service для задания: Сервисы (Выгодные категории повышенного кешбэка)
data_as_dataframe = pd.read_excel(path_to_xlsx)  # считали датафрейм с транзакциями
data_as_dicts = data_as_dataframe.to_dict(orient="records")  # преобразовали в список словарей
print(favorable_categories_of_increased_cashback(12, 2021, data_as_dicts))
#
# # Проверка модуля reports для задания: Отчеты (Траты по категории)
df_orders = pd.read_excel(path_to_xlsx)
print(function_for_generating(df_orders, "Различные товары", "31.12.2021 16:44:00"))
