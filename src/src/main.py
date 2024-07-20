import json
import os
from datetime import datetime
from math import isnan
from typing import Any

import pandas as pd
import requests

from loader import load_user_settings
from utils import convert_xlsx_to_dataframe, filter_from_month_begin

file_path = "user_settings.json"
data = load_user_settings(file_path)
user_currencies = data.get("user_currencies", [])
user_stocks = data.get("user_stocks", [])
path_to_datafile = str(data.get("path_to_datafile"))


def SP500(user_stocks: list[str]) -> dict[str, Any]:
    """Функция, возвращающая курс выбранных акций"""
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


def create_response(transactions: list[dict[str, Any]], datetime_str: str) -> str:
    """Функция формирования итогового JSON-ответа"""
    current_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").time()
    if 5 <= current_time.hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_time.hour < 18:
        greeting = "Добрый день"
    elif 18 <= current_time.hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    # Суммирование трат по картам
    card_summary = {}
    for transaction in transactions:
        card_number = transaction.get("Номер карты")
        if isinstance(card_number, str):
            card_number = card_number[-4:]
        else:
            continue

        amount = transaction.get("Сумма операции", 0)
        if isinstance(amount, float) and isnan(amount):
            amount = 0

        if amount < 0:  # Учитываем только расходы
            if card_number not in card_summary:
                card_summary[card_number] = {"total_spent": 0, "cashback": 0}

            card_summary[card_number]["total_spent"] += abs(amount)
            card_summary[card_number]["cashback"] += abs(amount) * 0.01

    cards = []
    for card_number, summary in card_summary.items():
        cards.append(
            {
                "last_digits": card_number,
                "total_spent": round(summary["total_spent"], 2),
                "cashback": round(summary["cashback"], 2),
            }
        )

    # Топ-5 транзакций по сумме
    expense_transactions = [trans for trans in transactions if trans["Сумма операции"] < 0]
    top_transactions = sorted(expense_transactions, key=lambda x: abs(x["Сумма операции"]), reverse=True)[:5]
    top_transactions_list = [
        {
            "date": trans["Дата операции"],
            "amount": trans["Сумма операции"],
            "category": trans["Категория"] if pd.notna(trans["Категория"]) else "",
            "description": trans["Описание"],
        }
        for trans in top_transactions
    ]

    exchange_rates = exchange_rate(user_currencies)
    stock_prices = SP500(user_stocks)

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions_list,
        "currency_rates": exchange_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    all_transactions = convert_xlsx_to_dataframe(path_to_datafile)
    datetime_str = "2018-01-19 14:45:00"
    trxns = all_transactions.to_dict(orient="records")
    transactions = filter_from_month_begin(trxns, datetime_str)
    response_json = create_response(transactions, datetime_str)
    print(response_json)
