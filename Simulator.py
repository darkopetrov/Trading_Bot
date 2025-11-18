import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

class Stock:
    def __init__(self, date: str, ticker: str, price: float, amount: int):
        self.date = date
        self.ticker = ticker
        self.price = price
        self.amount = amount

class Wallet:
    def __init__(self, cash: float, stocks: list['Stock']):
        self.cash = cash
        self.stocks = stocks
        
def generate_data(ticker, start: str, end: str):
    if isinstance(ticker, str):
        ticker = [ticker]
    data = yf.download(ticker, start=start, end=end, progress=False)
        
    return data
def buy_stock(wallet: Wallet, date: str, ticker: str, price: float, amount: int):
    if amount <= 0:
        return
    total_cost = price * amount
    if wallet.cash >= total_cost:
        wallet.cash -= total_cost
        for stock in wallet.stocks:
            if stock.ticker == ticker:
                stock_price = (stock.price * stock.amount) + (price * amount)
                stock.amount += amount
                stock.price = stock_price / stock.amount
                return
        if ticker not in [s.ticker for s in wallet.stocks]:
            wallet.stocks.append(Stock(date, ticker, price, amount))
            

def sell_stock(wallet: Wallet, date: str, ticker: str, price: float, amount: int):
    for stock in wallet.stocks:
        if stock.ticker == ticker and stock.amount >= amount:
            stock.amount -= amount
            wallet.cash += price * amount
            if stock.amount == 0:
                wallet.stocks.remove(stock)
            return

def calculate_total_value(wallet: Wallet, current_prices: dict = None):
    total_market_value = wallet.cash
    total_holding_value = wallet.cash
    for stock in wallet.stocks:
        if current_prices and stock.ticker in current_prices:
             current_price = current_prices[stock.ticker]
        else:
             current_price = stock.price 
        total_market_value += stock.amount * current_price
        total_holding_value += stock.amount * stock.price
    return total_market_value, total_holding_value

def get_current_holding(wallet: 'Wallet', ticker: str):
    """Calculates the total amount of a ticker held and the average purchase price."""
    total_amount = 0
    total_cost = 0.0
    
    # Iterate through all Stock objects in the wallet
    for stock in wallet.stocks:
        if stock.ticker == ticker:
            total_amount = stock.amount
            total_cost = stock.amount * stock.price
    if total_amount > 0:
        # Calculate the weighted average purchase price
        average_price = total_cost / total_amount
    else:
        average_price = 0.0
    return total_amount, average_price

def martingale_strategy(
    date: str, 
    ticker: str, 
    historical_data: pd.DataFrame,
    wallet: Wallet
):
    
    risk = 0.005
    martingale_factor = 0.05
    # 1. Isolate the data for the current ticker
    ticker_data = historical_data.xs(ticker, axis=1, level=1)
    if ticker_data.empty:
        return "hold", 0
    
    # 2. Extract the current day's values (which is the last row in ticker_data)
    current_row = ticker_data.iloc[-1]
    required_data = current_row[['Open', 'Close', 'High', 'Low']]
    if required_data.isna().any():
        return "hold", 0
    open_price = current_row['Open']
    close_price = current_row['Close']
    high_price = current_row['High']
    low_price = current_row['Low']
    volume = current_row['Volume']
    if open_price is None or close_price is None or high_price is None or low_price is None or volume is None:
        return "hold", 0
    
    # max_drop = int(((300000 * risk) / open_price) * 15)
    max_drop = 99999999999999999999999999999999999
    # print(max_drop)
    # 4. Implement a martingale strategy
    current_amount, average_buy_price = get_current_holding(wallet, ticker)
    if current_amount > max_drop:
        return "sell", int(current_amount)
    elif current_amount == 0:
        return "buy", int(wallet.cash / close_price * risk)
    elif current_amount > 0 and high_price > average_buy_price * (1.0+martingale_factor):
        return "sell", int(current_amount)
    elif current_amount > 0 and low_price < average_buy_price * (1-martingale_factor):
        return "buy", int(current_amount*2)
    else: 
        return "hold", 0

def simulate_trading(wallet: Wallet, data: pd.DataFrame):
    value_history = []
    
    for i, date in enumerate(data.index):
        historical_data_to_date = data.iloc[:i]
        current_day_data = data.iloc[i]
        current_prices = {}
        for ticker in data.columns.get_level_values(1).unique():
            simple_strategy_result, amount = martingale_strategy(
                date.strftime("%Y-%m-%d"), 
                ticker, 
                historical_data_to_date,
                wallet=wallet
            )
            close_price = current_day_data[('Close', ticker)]
            current_prices[ticker] = close_price

            if simple_strategy_result == "buy":
                buy_stock(wallet=wallet, date=date.strftime("%Y-%m-%d"), ticker=ticker, price=close_price, amount=amount)
            elif simple_strategy_result == "sell":
                sell_stock(wallet=wallet, date=date.strftime("%Y-%m-%d"), ticker=ticker, price=close_price, amount=amount)
                
        total_market_value, total_holding_value = calculate_total_value(wallet, current_prices)
        value_history.append([total_market_value, total_holding_value, wallet.cash])
    
    return value_history


def calculate_cumulative_returns(price_series: pd.Series):
    """Calculates the cumulative percentage return for a single stock price series."""
    daily_returns = price_series.pct_change()
    daily_returns = daily_returns.fillna(0) + 1 
    cumulative_returns = daily_returns.cumprod() - 1
    return cumulative_returns * 100

def value_visualization(value_history, data: pd.DataFrame):
    market_value_history = [item[0] for item in value_history]
    cash_value_history = [item[1] for item in value_history]
    cash_history = [item[2] for item in value_history]
    plt.figure(figsize=(12, 8))
    # plt.subplot(2, 1, 1)
    
    for ticker in data.columns.get_level_values(1).unique():
        close_prices = data[('Close', ticker)]
        percent_movement = calculate_cumulative_returns(close_prices)
        plt.plot(percent_movement, label=ticker)
    
    plt.title("Stock Price Cumulative Performance (%)")
    plt.xlabel("Time (Trading Days)")
    plt.ylabel("Cumulative Return (%)") 
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.figure(figsize=(12, 8))
    # plt.subplot(2, 1, 2)
    plt.plot(data.index, market_value_history, label="Portfolio Market Value")
    plt.plot(data.index, cash_value_history, label="Portfolio Holding Value (Cost)")
    plt.plot(data.index, cash_history, label="Cash Value")
    
    plt.title("Portfolio Total Value Over Time")
    plt.legend()
    plt.xlabel("Time (Trading Days)")
    plt.ylabel("Total Value (SEK)")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout(pad=3.0) # Ensures plots don't overlap
    plt.show()
    


if __name__ == "__main__":
    # tickers = ["INVE-B.ST", "AZN.ST", "APOTEA.ST", "EVO.ST", "SKF-B.ST", "TEL2-B.ST", "KINV-B.ST", "TELIA.ST", "HM-B.ST" , "ESSITY-B.ST", "HEXA-B.ST", "ASSA-B.ST", "NDA-SE.ST", "ATCO-A.ST", "SCA-B.ST", "GETI-B.ST", "ERIC-B.ST", "SWED-A.ST", "SHB-A.ST", "SAAB-B.ST", "SAND.ST", "SEB-A.ST", "SBB-B.ST", "LIFCO-B.ST","VOLV-B.ST", "ELUX-B.ST", "EPI-A.ST", "INDU-C.ST", "ADDT-B.ST", "SINCH.ST","BOL.ST", "ABB.ST", "SKA-B.ST", "EQT.ST", "NIBE-B.ST", "ALFA.ST"]
    tickers = ["AZN.ST", "EVO.ST", "VOLV-B.ST", "TELIA.ST", "SKF-B.ST", "NDA-SE.ST", "ESSITY-B.ST", "HEXA-B.ST", "TEL2-B.ST", "SWED-A.ST", "ERIC-B.ST", "HM-B.ST", "ATCO-A.ST", "SHB-A.ST", "SCA-B.ST", "INVE-B.ST", "ALFA.ST", "ASSA-B.ST", "SEB-A.ST", "EPI-A.ST", "SAND.ST", "ADDT-B.ST", "EQT.ST", "NIBE-B.ST", "INDU-C.ST", "LIFCO-B.ST", "BOL.ST", "SKA-B.ST", "SAAB-B.ST", "ABB.ST"]

    # tickers = ["INVE-B.ST"]
    
    # Start the simulation with X SEK
    start_cash = 300000
    start_date = "2021-09-01"
    end_date = "2023-12-15"
    
    
    wallet = Wallet(start_cash, []) 
    
    print(f"Starting simulation with {len(tickers)} tickers and initial cash: {wallet.cash:.2f} SEK")
    
    data = generate_data(tickers, start_date, end_date)
    if data.empty:
        print("Error: No data fetched for the given dates/tickers.")
    else:
        value_history = simulate_trading(wallet, data)
        print(f"Final Portfolio Market Value SEK: {value_history[-1][0]:.2f} SEK")
        print(f"Final Portfolio Value SEK: {value_history[-1][1]:.2f} SEK")
        print("Profit Market Value %: {:.2f}%".format((value_history[-1][0] - start_cash) / start_cash * 100))
        print("Profit Value %: {:.2f}%".format((value_history[-1][1] - start_cash) / start_cash * 100))
        print(f"Remaining Cash: {wallet.cash:.2f} SEK")
        # for stock in wallet.stocks:
        #     print(f"Holding {stock.amount} of {stock.ticker} at average price {stock.price:.2f} SEK")
        
        value_visualization(value_history, data)
        