import yfinance as yf


cash = 10000 # Initial cash amount in SEK
stocks = 0   # Initial number of stocks
courtage = 0.0025 # 0.25%
ticker = "INVE-B.ST" # Stock ticker symbol
start_date = "2023-11-01"
end_date = "2025-12-31"

def buy(cash: float, price: float, stocks: int, amount: int ): 
    # Buy stocks
    total_cost = price * amount * (1 + courtage)
    if cash >= total_cost:
        cash -= total_cost
        stocks += amount
        return cash, stocks
    else:
        return cash, stocks  # Not enough cash to buy
    
def sell(cash: float, price: float, stocks: int, amount: int ):
    # Sell stocks
    if stocks >= amount:
        total_revenue = price * amount * (1 - courtage)
        cash += total_revenue
        stocks -= amount
        return cash, stocks
    else:
        return cash, stocks  # Not enough stocks to sell
    
def generate_data(ticker: str, start: str, end: str):
    # Fetch historical stock data
    data = yf.download(ticker, start=start, end=end)
    return data

def run_simulation(data, cash: float, stocks: int):
    # Placeholder for simulation logic
    value_history = []
    for index, row in data.iterrows():
        date = index
        open_price = row['Open'].values[0]
        high_price = row['High'].values[0]
        low_price = row['Low'].values[0]
        close_price = row['Close'].values[0]
        volume = row['Volume'].values[0]
        # Implement trading strategy here
        if close_price > open_price:  # Simple strategy example
            cash, stocks = buy(cash, close_price, stocks, 1)
        elif close_price < open_price:
            cash, stocks = sell(cash, close_price, stocks, 1)
        value_history.append(cash + stocks * close_price)
    cash, stocks = sell(cash, close_price, stocks, stocks)  # Sell all at the end
    return cash, stocks, value_history


def vaalue_visualization(value_history):
    import matplotlib.pyplot as plt
    plt.plot(value_history)
    plt.title("Portfolio Value Over Time")
    plt.xlabel("Time")
    plt.ylabel("Total Value (SEK)")
    plt.show()
    

if __name__ == "__main__":
    print("Cash:", cash)
    data = generate_data(ticker, start_date, end_date)
    cash, stock, value_his = run_simulation(data, cash, stocks)
    vaalue_visualization(value_his)
    print("Final Cash:", cash)
    
    
    