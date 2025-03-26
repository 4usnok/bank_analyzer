import unittest
import json
from datetime import datetime
from src.services import (
    filter_transactions_by_date,
    sum_cashback_by_category,
    favorable_categories_of_increased_cashback,
)

class TestReports(unittest.TestCase):
    def setUp(self):
        """
        Подготовка тестовых данных.
        """
        self.transactions = [
            {"Дата операции": "01.12.2021 10:15:30", "Категория": "Супермаркеты", "Бонусы (включая кэшбэк)": 100},
            {"Дата операции": "15.12.2021 18:30:45", "Категория": "Супермаркеты", "Бонусы (включая кэшбэк)": 200},
            {"Дата операции": "20.11.2021 12:00:00", "Категория": "АЗС", "Бонусы (включая кэшбэк)": 50},
            {"Дата операции": "25.12.2021 14:45:00", "Категория": "Рестораны", "Бонусы (включая кэшбэк)": 150},
            {"Дата операции": "01.09.2021 10:15:30", "Категория": "Супермаркеты", "Бонусы (включая кэшбэк)": 300},
        ]

    def test_filter_transactions_by_date(self):
        """
        Тест фильтрации транзакций по дате.
        """
        filtered = filter_transactions_by_date(self.transactions, 12, 2021)
        # Проверяем, что отфильтровано 3 транзакции за декабрь 2021 года
        self.assertEqual(len(filtered), 3)
        # Проверяем, что все транзакции относятся к декабрю 2021 года
        for transaction in filtered:
            date_obj = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            self.assertEqual(date_obj.month, 12)
            self.assertEqual(date_obj.year, 2021)

    def test_sum_cashback_by_category(self):
        """
        Тест суммирования кешбэка по категориям.
        """
        result = sum_cashback_by_category(self.transactions)
        # Проверяем, что кешбэк по категориям суммирован правильно
        self.assertEqual(result, {
            "Супермаркеты": 600,  # 100 + 200 + 300
            "АЗС": 50,
            "Рестораны": 150,
        })

    def test_favorable_categories_of_increased_cashback(self):
        """
        Тест основной функции.
        """
        result = favorable_categories_of_increased_cashback(12, 2021, self.transactions)
        # Преобразуем JSON в словарь для проверки
        result_dict = json.loads(result)
        # Проверяем, что результат содержит правильные суммы кешбэка
        self.assertEqual(result_dict, {
            "Супермаркеты": 300,  # 100 + 200 (только за декабрь 2021)
            "Рестораны": 150,
        })

if __name__ == "__main__":
    unittest.main()