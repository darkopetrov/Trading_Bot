import yfinance as yf
from TICKER_DATA import TICKER_DATA
from datetime import datetime
import shutil
import os
import pandas as pd

def generate_csv_finance_data(ticker, start_date, end_date, filename):

    # Fetch historical data
    data = yf.download(ticker, start=start_date, end=end_date)
    data.to_csv(f"./finnance_data/{filename}.csv")
    new = pd.read_csv(f'./finnance_data/{filename}.csv', index_col=0)
    new1 = new.drop(["Date", "Ticker"])
    new1.to_csv(f"./finnance_data/{filename}.csv")
    


if os.path.exists("./finnance_data/"):
    shutil.rmtree("./finnance_data/")
    
    
os.makedirs("./finnance_data/")

today = datetime.now().strftime("%Y-%m-%d")

for item in TICKER_DATA:
    ticker = item["ticker"]
    generate_csv_finance_data(ticker, "2000-01-01", today, ticker)



