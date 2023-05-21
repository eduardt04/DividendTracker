import yfinance as yf


def get_stock_data(stock_name):
    # Create a Ticker object for the stock
    ticker = yf.Ticker(stock_name)

    # Retrieve the dividend history
    dividends = ticker.dividends

    # Check for data availability
    try:
        last_payment_date = f"{dividends.index[-1].day}-{dividends.index[-1].month}-{dividends.index[-1].year}"
        last_payment_ammount = dividends.values[-1]
        last_price = float(ticker.history().tail(1)["Close"].iloc[0])
        dividends_per_year = 0
        for payment_date in dividends.index:
            if str(payment_date.year) == "2022":
                dividends_per_year += 1
        return (last_price, last_payment_ammount, last_payment_date, dividends_per_year)
    except:
        return None
