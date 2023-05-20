import requests
import tkinter as tk
import yfinance as yf

from datetime import datetime


def show_dividend_info(stock_info_text, stock_name):
    # Create a Ticker object for the stock
    ticker = yf.Ticker(stock_name)

    # Retrieve the stock information
    try:
        stock_info = ticker.info
    except:
        stock_info_text.set(f"{stock_name} does not exist.")
        return

    # Extract the current price
    if "currentPrice" in stock_info:
        current_price = stock_info["currentPrice"]
    else:
        current_price = "Price not available."

    # Retrieve the dividend history
    dividends = ticker.dividends

    try:
        # Change format of the date of the last payment
        last_payment_date = f"{dividends.index[-1].day}-{dividends.index[-1].month}-{dividends.index[-1].year}"

        last_payment_ammount = dividends.values[-1]

        # Change the output in the application
        stock_info_text.set(
            f"Last payment date: {last_payment_date}\n\
            Last payment amount: {last_payment_ammount}\n\
            Current price: {current_price}"
        )
    except:
        stock_info_text.set(f"{stock_name} has no dividend data.")
