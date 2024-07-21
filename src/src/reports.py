import re
from typing import Any
def sum_transactions_by_category(transactions: list[dict[str, Any]]) -> dict[str, float]:
    """
    Функция группировки транзакций по категориям и суммирования сумм по категориям.
 """
    category_sums = {}

    for transaction in transactions:
        category = transaction.get('Категория')
        amount = transaction.get('Сумма операции', 0.0)

        if category is not None:
            if category not in category_sums:
                category_sums[category] = 0.0
            category_sums[category] += amount

    return category_sums


print(sum_transactions_by_category(transactions))
