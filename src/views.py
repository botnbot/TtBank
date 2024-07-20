import os
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
import pandas as pd
import requests
import json

load_dotenv(".env")




def SP500(user_stocks: list[str]) -> dict:
    stock_prices = {}
    api_key = os.getenv("AV_API_KEY")
    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=1min&apikey={api_key}"
        response = requests.get(url)
        data = response.json()

        if "Meta Data" in data:
            try:
                last_refreshed = data["Meta Data"]["3. Last Refreshed"]
                stock_prices[stock] = data["Time Series (1min)"][last_refreshed]["1. open"]
            except KeyError:
                stock_prices[stock] = "N/A"
                print(f"Ошибка получения данных для акции {stock}: Неверная структура данных")
        else:
            stock_prices[stock] = "N/A"
            print(f"Ошибка получения данных для акции {stock}: {data}")

    return stock_prices


def exchange_rate(user_currencies: list[str]) -> dict[str, Any]:
    """Функция, возвращающая курс выбранных валют к рублю"""
    apikey = os.getenv("API_KEY")
    results = {}
    for currency in user_currencies:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        headers = {"apikey": apikey}
        response = requests.get(url, headers=headers)
        data = response.json()

        if "result" in data:
            results[currency] = round(data["result"], 2)
        else:
            results[currency] = {"rate_to_rub": "N/A", "error": data.get("error", "Unknown error")}
    return results


def filter_from_month_begin(transactions: list[dict], end_date: str = None) -> list[dict]:
    """Функция фильтрации транзакций по дате (с начала месяца)"""

    date_format_with_time = "%d.%m.%Y %H:%M:%S"
    date_format_without_time = "%d.%m.%Y"

    if end_date:
        try:
            end_date_time = datetime.strptime(end_date, date_format_with_time)
        except ValueError:
            end_date_time = datetime.strptime(end_date, date_format_without_time)
    else:
        end_date_time = datetime.now()

    # Определение даты начала месяца
    start_date = end_date_time.replace(day=1)

    filtered_transactions = []

    for transaction in transactions:
        transaction_date_str = transaction.get("Дата операции")
        if transaction_date_str:
            try:
                transaction_date = datetime.strptime(transaction_date_str, date_format_with_time)
            except ValueError:
                transaction_date = datetime.strptime(transaction_date_str, date_format_without_time)
            if start_date <= transaction_date <= end_date_time:
                filtered_transactions.append(transaction)

    return filtered_transactions