import pandas as pd
import pandas_ta as ta
import yfinance as yf
import os
import time
from datetime import datetime
from TICKER_DATA import TICKER_DATA


TICKERS = [item["ticker"] for item in TICKER_DATA]
# TICKERS = ["INVE-B.ST","BILI-A.ST"]
DATA_DIR = "stocks_data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def update_data(tickers):
    for ticker in tickers:
        file_path = f"{DATA_DIR}/{ticker}.csv"
        if os.path.exists(file_path):
            # Read existing file to find the last date
            existing_df = pd.read_csv(file_path, index_col="Price")
            if not existing_df.empty:
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                last_timestamp = df.index[-1]
                start_date = last_timestamp + pd.Timedelta(hours=1)
                new_data = yf.download(ticker, start=start_date, interval="1h", auto_adjust=True)
                if not new_data.empty:
                    for ind in new_data.index:
                        df.loc[ind] = new_data.loc[ind].tolist()
                        df.to_csv(file_path)
                else:
                    print("Data is already up to date.")
        else: 
            print(file_path) 
        
        
            




if __name__ == "__main__":
    print("Update prices up to Date")
    update_data(TICKERS)
    
    
    
    
    
    
    
    
    
    