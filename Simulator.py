import yfinance as yf


cash = 10000 # Initial cash amount in SEK
stocks = 0   # Initial number of stocks
courtage = 0.0025 # 0.25%
ticker = "INVE-B.ST" # Stock ticker symbol
start_date = "2025-11-01"
end_date = "2025-12-31"

def buy(cash: float, price: float, stocks: int, amount: int ): 
    # Buy stocks
    total_cost = price * amount * (1 + courtage)
    if cash >= total_cost:
        cash -= total_cost
        stocks += amount
        return cash, stocks
    else:
        raise ValueError("Insufficient cash to buy stocks.")
    
def sell(cash: float, price: float, stocks: int, amount: int ):
    # Sell stocks
    if stocks >= amount:
        total_revenue = price * amount * (1 - courtage)
        cash += total_revenue
        stocks -= amount
        return cash, stocks
    else:
        raise ValueError("Insufficient stocks to sell.")
    
def generate_data(ticker: str, start: str, end: str):
    # Fetch historical stock data
    data = yf.download(ticker, start=start, end=end)
    return data


   




if __name__ == "__main__":
    cash, stocks = buy(cash, 100, stocks, 50)  # Buy 50 stocks at 100 SEK each
    cash, stocks = sell(cash, 120, stocks, 20) # Sell 20 stocks at 120 SEK each
    print("Cash:", cash)
    data = generate_data(ticker, start_date, end_date)
    # data_iterator(data)