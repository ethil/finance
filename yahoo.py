# Get stock prices
import pandas_datareader.data as web

def stocks(tickers, start_date, end_date):

    panel_data = web.DataReader(tickers, 'yahoo', start_date, end_date)
    print(panel_data.head()) # adjusted for dividends, splits, etc.
    prices = panel_data['Adj Close']

    return prices
