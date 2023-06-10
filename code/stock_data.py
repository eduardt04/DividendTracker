import yfinance as yf
from datetime import datetime, timedelta


def get_stock_data(stock_name):
    # Create a Ticker object for the stock
    ticker = yf.Ticker(stock_name)

    # Retrieve the dividend history
    dividends = ticker.dividends

    # Check for data availability
    try:
        dividends_per_year = 0
        for payment_date in dividends.index:
            if str(payment_date.year) == "2022":
                dividends_per_year += 1
        estimated_gap = 12 / dividends_per_year * 30
        estimated_next_date = dividends.index[-1] + timedelta(days=int(estimated_gap))
        estimated_next_date = f"{estimated_next_date.day}-{estimated_next_date.month}-{estimated_next_date.year}"
        last_payment_ammount = dividends.values[-1]
        last_price = float(ticker.history().tail(1)["Close"].iloc[0])
        return (
            last_price,
            last_payment_ammount,
            estimated_next_date,
            dividends_per_year,
        )
    except:
        return None
