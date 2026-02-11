import yfinance as yf
import pandas as pd
import os
import shutil
from datetime import datetime
from TICKER_DATA import TICKER_DATA

TICKERS = [item["ticker"] for item in TICKER_DATA]
# TICKERS = ["RUSTA.ST", "INVE-B.ST"]

def generate_csv_finance_data(ticker, filename, days):
    
    try:
        data = yf.download(ticker, interval="1h", period=f"{days}d", progress=False)
        data.to_csv(f"./stocks_data/{filename}.csv")
        new = pd.read_csv(f'./stocks_data/{filename}.csv', index_col=0)
        new1 = new.drop(["Datetime", "Ticker"])
        new1.to_csv(f"./stocks_data/{filename}.csv")
    except Exception as e:
        if days > 0:
            generate_csv_finance_data(ticker=ticker, filename=filename, days=days-1)
        else:
            print(f"Cannot find data for {ticker}")
    


if os.path.exists("./stocks_data/"):
    shutil.rmtree("./stocks_data/")
    
    
os.makedirs("./stocks_data/")

today = datetime.now().strftime("%Y-%m-%d")

for ticker in TICKERS:
    generate_csv_finance_data(ticker, ticker, 730)

