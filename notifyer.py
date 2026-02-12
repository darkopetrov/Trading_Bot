import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import os
import requests
import time
from datetime import datetime
import sys
from contextlib import contextmanager
import datetime
import pytz
import holidays
import schedule
import time
from TICKER_DATA import TICKER_DATA
from TICKER_L_C import TICKER_L_C

USER_KEY = "umxxe77rhdu583dpiksvztp2r3imj7"
APP_TOKEN = "a16u3mnwmshokpqbe7re9e2hc214y5"
DATA_DIR = "stocks_data"
# TICKERS = [item["ticker"] for item in TICKER_DATA]
TICKERS = [item["ticker"] for item in TICKER_L_C]
# TICKERS = ["INVE-B.ST","BILI-A.ST"]



@contextmanager
def no_terminal_output():
    """Context manager to suppress stdout and stderr."""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def send_pushover_notification(cheap_stocks):
    """Sends a formatted list of tickers to your phone."""
    if not cheap_stocks:
        return

    # Format the message as a list
    ticker_list = "\n".join([f"• <b>{ticker}</b>" for ticker in cheap_stocks])
    message = f"The following stocks hit your signal:\n{ticker_list}"
    
    payload = {
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": message,
        "title": "📈 Stock Scanner Alert",
        "html": 1,          # Enables <b> tags
        "sound": "cashregister",
        "priority": 1       # Bypasses quiet hours
    }
    
    try:
        requests.post("https://api.pushover.net/1/messages.json", data=payload)
        print("Notification sent to phone.")
    except Exception as e:
        print(f"Failed to send notification: {e}")
        time.sleep(10)
        send_pushover_notification(cheap_stocks)



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
                with no_terminal_output():
                    new_data = yf.download(ticker, start=start_date, interval="1h", auto_adjust=True, progress=False)

                if not new_data.empty:
                    for ind in new_data.index:
                        df.loc[ind] = new_data.loc[ind].tolist()
                        df.to_csv(file_path)
        else:
            print("No Data for ", ticker)


        
def get_analasys_tools(df):
    df['EMA_200'] = ta.ema(df["Close"], length=200)
    macd = ta.macd(df["Close"])
    df = pd.concat([df, macd], axis=1)
    return df.dropna()




def scanner_check(tickers):
    buy_flag = []
    for ticker in tickers:
        file_path = f"{DATA_DIR}/{ticker}.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            df = get_analasys_tools(df)
            curr = df.iloc[-1]
            prev = df.iloc[-2]
            price_above_ema = curr['Close'] > curr['EMA_200']
            macd_lines_below_zero = curr['MACD_12_26_9'] < 0 and curr["MACDs_12_26_9"] < 0
            his_flipped_pos = prev['MACDh_12_26_9'] <= 0 and curr['MACDh_12_26_9'] > 0
            if price_above_ema and macd_lines_below_zero and his_flipped_pos:
                buy_flag.append(ticker)
                
    return buy_flag
            
            
def is_market_open():
    tz = pytz.timezone('Europe/Stockholm')
    now = datetime.datetime.now(tz)
    if now.weekday() >= 5:
        return False

    # 3. Check if it's a Market Holiday
    us_holidays = holidays.US()
    if now.strftime('%Y-%m-%d') in holidays.Sweden():
        return False

    # 4. Check if within Trading Hours (9:30 AM - 4:00 PM)
    market_open = datetime.time(9, 0)
    market_close = datetime.time(18, 1)
    current_time = now.time()

    return market_open <= current_time <= market_close

def main_job(force_run=False):
    global last_sent_hits 
    last_sent_hits = []
    
    if is_market_open() or force_run:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Market Open. Scanning...")
        update_data(TICKERS)
        current_hits = scanner_check(TICKERS)
        
        # ONLY send if the result is DIFFERENT from the last time we sent a notification
        if current_hits:
            if current_hits != last_sent_hits:
                send_pushover_notification(current_hits)
                last_sent_hits = current_hits # Update memory
                print(f"New signals: {current_hits}")
            else:
                print("Signals same as last hour. Skipping notification.")
        else:
            last_sent_hits = [] # Clear memory if no signals
            print("No signals found.")
    else:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Market Closed. Skipping.")
            



schedule.every().hour.at(":00").do(main_job)
if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    print("Bot is active and waiting for market hours...")
    
    main_job(force_run=True)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
    
    
    
    
    
    