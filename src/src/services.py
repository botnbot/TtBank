import json
import re

def filter_personal_transfers(transactions):
    # Регулярное выражение для поиска имени и первой буквы фамилии с точкой
    name_pattern = re.compile(r'\b[A-ЯЁ][а-яё]+\s[A-ЯЁ]\.\b')

    # Функция для проверки, соответствует ли транзакция условиям
    def is_personal_transfer(transaction):
        return (transaction['Категория'] == 'Переводы' and
                name_pattern.search(transaction['Описание']))

    # Функция для преобразования транзакции в формат JSON (или другой формат при необходимости)
    def to_json(transaction):
        return transaction

    # Применяем фильтр и маппинг
    filtered_transactions = filter(is_personal_transfer, transactions)
    mapped_transactions = map(to_json, filtered_transactions)

    # Преобразуем список отфильтрованных и преобразованных транзакций в JSON
    return json.dumps(list(mapped_transactions), ensure_ascii=False, indent=4)
