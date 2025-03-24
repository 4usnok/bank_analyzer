import unittest
import pandas as pd
from datetime import datetime, timedelta
from src.reports import function_for_generating

class TestFunctionForGenerating(unittest.TestCase):
    def setUp(self):
        """
        Подготовка тестовых данных.
        """
        self.transactions = pd.DataFrame({
            "Дата операции": [
                "01.12.2021 10:15:30", "15.12.2021 18:30:45", "20.11.2021 12:00:00",
                "25.12.2021 14:45:00", "01.09.2021 10:15:30"
            ],
            "Категория": [
                "Супермаркеты", "Супермаркеты", "АЗС", "Рестораны", "Супермаркеты"
            ],
            "Сумма операции": [-500, -300, 200, -200, -100]  # Отрицательные значения — траты
        })

    def test_filter_by_category(self):
        """
        Тест фильтрации по категории.
        """
        result = function_for_generating(self.transactions, "Супермаркеты")
        # Проверяем, что все строки в результате относятся к категории "Супермаркеты"
        self.assertTrue((result["Категория"] == "Супермаркеты").all())

    def test_filter_by_date(self):
        """
        Тест фильтрации по дате.
        """
        result = function_for_generating(self.transactions, "Супермаркеты", "01.12.2021 10:15:30")
        # Проверяем, что все строки в результате относятся к последним трём месяцам
        current_date = datetime.strptime("01.12.2021 10:15:30", "%d.%m.%Y %H:%M:%S")
        three_months_ago = current_date - timedelta(days=90)
        result_dates = pd.to_datetime(result["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        self.assertTrue((result_dates >= three_months_ago).all())
        self.assertTrue((result_dates <= current_date).all())

    def test_filter_by_spending(self):
        """
        Тест фильтрации по тратам (сумма операции < 0).
        """
        result = function_for_generating(self.transactions, "Супермаркеты")
        # Проверяем, что все суммы операций отрицательные
        self.assertTrue((result["Сумма операции"] < 0).all())

    def test_no_data_found(self):
        """
        Тест для случая, когда данные отсутствуют.
        """
        result = function_for_generating(self.transactions, "Несуществующая категория")
        # Проверяем, что результат пустой
        self.assertTrue(result.empty)

    def test_no_date_provided(self):
        """
        Тест для случая, когда дата не передана.
        """
        result = function_for_generating(self.transactions, "Супермаркеты")
        # Проверяем, что все строки относятся к категории "Супермаркеты"
        self.assertTrue((result["Категория"] == "Супермаркеты").all())
        # Проверяем, что все суммы операций отрицательные
        self.assertTrue((result["Сумма операции"] < 0).all())