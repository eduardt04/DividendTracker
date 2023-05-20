import yfinance as yf

from datetime import datetime


class Stock:
    def __init__(self, stock_name):
        self.stock_name = stock_name

        # Create a Ticker object for the stock
        ticker = yf.Ticker(stock_name)

        # Retrieve the dividend history
        dividends = ticker.dividends

        try:
            # Change format of the date of the last payment
            self.last_payment_date = f"{dividends.index[-1].day}-{dividends.index[-1].month}-{dividends.index[-1].year}"
            self.last_payment_ammount = dividends.values[-1]
            self.last_price = float(ticker.history().tail(1)["Close"].iloc[0])
        except:
            self.last_payment_date = None
            self.last_payment_ammount = None
            self.last_price = None
