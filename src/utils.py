from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

load_dotenv(".env")

def convert_xlsx_to_dataframe(file_name: str) -> pd.DataFrame:
    df = pd.DataFrame()
    try:
        if not Path(file_name).is_file():
            raise FileNotFoundError(f"Файл '{file_name}' не найден.")

        df = pd.read_excel(file_name)

    except ValueError as e:
        print(f"Произошла ошибка при чтении файла '{file_name}': {e}")
    except Exception as e:
        print(f"Произошла ошибка при чтении файла '{file_name}': {str(e)}")

    return df

def filter_from_month_begin(transactions, end_date: str = None) -> list[dict]:
    """Функция фильтрации транзакций по дате (с начала месяца)"""

    # Определение форматов дат
    date_format_with_time_iso = "%Y-%m-%d %H:%M:%S"
    date_format_with_time_rus = "%d.%m.%Y %H:%M:%S"
    date_format_without_time_iso = "%Y-%m-%d"
    date_format_without_time_rus = "%d.%m.%Y"

    # Определение даты окончания
    if end_date:
        try:
            end_date_time = datetime.strptime(end_date, date_format_with_time_iso)
        except ValueError:
            end_date_time = datetime.strptime(end_date, date_format_without_time_iso)
    else:
        end_date_time = datetime.now()

    # Определение даты начала месяца
    start_date = end_date_time.replace(day=1)

    filtered_transactions = []

    for transaction in transactions:
        transaction_date_str = transaction.get("Дата операции")
        if transaction_date_str:
            # Попытка разобрать дату транзакции
            try:
                transaction_date = datetime.strptime(transaction_date_str, date_format_with_time_iso)
            except ValueError:
                try:
                    transaction_date = datetime.strptime(transaction_date_str, date_format_without_time_iso)
                except ValueError:
                    try:
                        transaction_date = datetime.strptime(transaction_date_str, date_format_with_time_rus)
                    except ValueError:
                        transaction_date = datetime.strptime(transaction_date_str, date_format_without_time_rus)
            if start_date <= transaction_date <= end_date_time:
                filtered_transactions.append(transaction)

    return filtered_transactions

