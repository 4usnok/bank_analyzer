import json
import logging
from datetime import datetime

import openpyxl

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def favorable_categories_of_increased_cashback(month, year, path_to_xlsx):
    """Функция для анализа выгодности категорий повышенного кешбэка."""
    try:
        # Чтение Excel-файла
        book = openpyxl.load_workbook(path_to_xlsx)
        sheet = book.active

        # Словарь для хранения результатов
        result_dict = {}

        # Проход по строкам
        for row in range(2, sheet.max_row + 1):
            # Чтение данных из ячеек
            cat_find = sheet.cell(row=row, column=10).value  # Категория (столбец J)
            pay_find = sheet.cell(
                row=row, column=13
            ).value  # Процент кешбэка (столбец M)
            amount_find = sheet.cell(
                row=row, column=7
            ).value  # Сумма операции (столбец G)
            date_find = sheet.cell(row=row, column=2).value  # Дата (столбец B)

            # Пропустить строку, если данные отсутствуют
            if None in (cat_find, pay_find, amount_find, date_find):
                logging.warning(f"Пропущена строка {row}: отсутствуют данные")
                continue

            # Преобразование даты
            try:
                dt_object = datetime.strptime(date_find, "%d.%m.%Y")
            except ValueError as e:
                logging.error(f"Ошибка в строке {row}: некорректная дата '{date_find}'")
                continue

            # Проверка месяца и года
            if month == dt_object.month and year == dt_object.year:
                # Вычисление кешбэка
                cashback = round(pay_find * amount_find) * -1

                # Объединяем результаты в один словарь
                if cat_find in result_dict:
                    result_dict[
                        cat_find
                    ] += cashback  # Суммируем кешбэк для существующей категории
                else:
                    result_dict[cat_find] = cashback  # Добавляем новую категорию

        # Преобразуем результат в JSON
        result_json = json.dumps(result_dict, ensure_ascii=False, indent=4)
        return result_json

    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {e}")
        return json.dumps({})  # Возвращаем пустой JSON-объект в случае ошибки
