import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# 1. SMART WALLET (With Memory for Trailing Stops)
# -----------------------------------------------------------------------------

class Wallet:
    def __init__(self, cash: float):
        self.cash = cash
        # Structure: 
        # { 'TICKER': {'amount': int, 'avg_price': float, 'max_price': float} }
        self.stocks = {} 

    def get_holding(self, ticker):
        return self.stocks.get(ticker, {'amount': 0, 'avg_price': 0.0, 'max_price': 0.0})

    def update_high_watermark(self, ticker, current_price):
        """Tracks the highest price seen since we bought the stock (for trailing stops)."""
        if ticker in self.stocks:
            if current_price > self.stocks[ticker]['max_price']:
                self.stocks[ticker]['max_price'] = current_price

    def buy(self, ticker, price, amount):
        if amount <= 0 or self.cash < (price * amount): return
        
        cost = price * amount
        self.cash -= cost
        
        current = self.get_holding(ticker)
        old_amount = current['amount']
        old_avg = current['avg_price']
        
        new_amount = old_amount + amount
        
        # Calculate Weighted Average Price
        if old_amount > 0:
            total_val = (old_amount * old_avg) + cost
            new_avg = total_val / new_amount
        else:
            new_avg = price
            
        # If new position, max_price is current price. 
        # If adding to position, we generally keep the old max_price or reset. 
        # For simplicity: keep old max unless current is higher.
        new_max = max(current['max_price'], price) if old_amount > 0 else price

        self.stocks[ticker] = {
            'amount': new_amount, 
            'avg_price': new_avg, 
            'max_price': new_max
        }

    def sell(self, ticker, price, amount):
        current = self.get_holding(ticker)
        if current['amount'] >= amount and amount > 0:
            self.cash += price * amount
            remaining = current['amount'] - amount
            
            if remaining <= 0:
                if ticker in self.stocks: del self.stocks[ticker]
            else:
                self.stocks[ticker]['amount'] = remaining
                # We do NOT reset avg_price or max_price on partial sells usually

    def get_total_value(self, current_prices):
        val = self.cash
        for ticker, data in self.stocks.items():
            price = current_prices.get(ticker, data['avg_price'])
            val += data['amount'] * price
        return val

# -----------------------------------------------------------------------------
# 2. DATA ENGINE
# -----------------------------------------------------------------------------

@st.cache_data
def get_data(tickers, start, end):
    if not tickers: return pd.DataFrame()
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=False)
    return df

def pre_calculate_indicators(df, indicators):
    is_multi = isinstance(df.columns, pd.MultiIndex)
    if is_multi:
        tickers = df.columns.get_level_values(1).unique()
        data_map = {}
        for ticker in tickers:
            sub_df = df.xs(ticker, axis=1, level=1).copy()
            data_map[ticker] = apply_indicators_single(sub_df, indicators)
        return data_map
    else:
        ticker = df.columns[0] if len(df.columns) > 0 else "Asset"
        return {ticker: apply_indicators_single(df.copy(), indicators)}

def apply_indicators_single(df, indicators):
    df.columns = [c.lower() for c in df.columns]
    for ind in indicators:
        try:
            if "sma" in ind:
                window = int(ind.split("_")[1])
                df[ind] = df['close'].rolling(window=window).mean()
            elif "ema" in ind:
                window = int(ind.split("_")[1])
                df[ind] = df['close'].ewm(span=window).mean()
            elif "rsi" in ind:
                window = int(ind.split("_")[1])
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
                rs = gain / loss
                df[ind] = 100 - (100 / (1 + rs))
        except: pass
    return df.fillna(0)

# -----------------------------------------------------------------------------
# 3. LOGIC EVALUATOR
# -----------------------------------------------------------------------------

def evaluate_condition(row, condition_str, wallet_context):
    """
    Merges Market Data (row) with Wallet Data (wallet_context)
    to allow rules like 'close < avg_price'.
    """
    try:
        # Combine row data (Open, Close, SMA) with Wallet data (avg_price, cash)
        combined_context = {**row.to_dict(), **wallet_context}
        return eval(condition_str, {"__builtins__": None}, combined_context)
    except Exception as e:
        # st.write(f"Debug Error in rule: {condition_str} -> {e}") # Uncomment for debugging
        return False

# -----------------------------------------------------------------------------
# 4. UI & SIMULATION
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Pro Strategy Builder", layout="centered")
st.title("🧠 Pro Strategy Builder")
# --- HELP SECTION ---
with st.expander("📚 Variable Cheat Sheet (Click to Expand)"):
    st.markdown("""
    **Market Variables:**
    * `close`, `open`, `high`, `low`
    * `sma_50`, `rsi_14` (Whatever you defined)

    **Wallet Variables (Crucial for Stoploss/Martingale):**
    * `avg_price`: Your average buy price for this stock.
    * `pct_profit`: Your current P/L % (e.g., -0.05 is -5%).
    * `max_price`: The highest price reached since you bought (for Trailing Stop).
    * `cash`: Total available cash.
    
    **Examples:**
    * **Stop Loss 5%:** `pct_profit < -0.05`
    * **Take Profit 20%:** `pct_profit > 0.20`
    * **Trailing Stop 10%:** `close < max_price * 0.90`
    * **Martingale (Buy More on dip):** `pct_profit < -0.10` (Put this in BUY condition)
    """)

# --- INPUT SECTION ---
st.header("1. Setup")
tickers_input = st.multiselect("Tickers", ["AZN.ST", "EVO.ST", "VOLV-B.ST", "TELIA.ST", "SKF-B.ST", "NDA-SE.ST", "ESSITY-B.ST", "HEXA-B.ST", "TEL2-B.ST", "SWED-A.ST", "ERIC-B.ST", "HM-B.ST", "ATCO-A.ST", "SHB-A.ST", "SCA-B.ST", "INVE-B.ST", "ALFA.ST", "ASSA-B.ST", "SEB-A.ST", "EPI-A.ST", "SAND.ST", "ADDT-B.ST", "EQT.ST", "NIBE-B.ST", "INDU-C.ST", "LIFCO-B.ST", "BOL.ST", "SKA-B.ST", "SAAB-B.ST", "ABB.ST"], ["VOLV-B.ST"])
start_d = st.date_input("Start", pd.to_datetime("2022-01-01"))
end_d = st.date_input("End", pd.to_datetime("2023-12-01"))

# Typed Input for Cash
cash = st.number_input("Initial Cash", value=100000, step=1000)

st.divider()
st.header("2. Indicators")
indicators_raw = st.text_area("Define Indicators", "sma_50, sma_200, rsi_14")
indicator_list = [x.strip() for x in indicators_raw.split(",") if x.strip()]

st.divider()
st.header("3. Buy Logic")
buy_condition = st.text_input("Buy Condition", "close > sma_200 and rsi_14 < 30")
buy_size_pct = st.number_input("Buy Size (% of Cash)", value=10.0, step=1.0) / 100.0

st.divider()
st.header("4. Sell Logic")
st.markdown("Use variables: `pct_profit`, `avg_price`, `max_price`")

# Allow multiple OR conditions by chaining them in one line or simply complex logic
sell_condition = st.text_input("Sell Condition", "pct_profit < -0.05 or close < max_price * 0.90")
sell_size_pct = st.number_input("Sell Size (% of Holding)", value=100.0, step=10.0) / 100.0

run = st.button("Run Simulation", type="primary")


# --- MAIN ---
if run:
    st.divider()
    st.header("📊 Simulation Results")
    if not tickers_input:
        st.error("Select tickers.")
    else:
        with st.spinner("Processing..."):
            raw_df = get_data(tickers_input, start_d, end_d)
            
        if raw_df.empty:
            st.error("No data.")
        else:
            # Pre-calc indicators
            data_map = pre_calculate_indicators(raw_df, indicator_list)
            
            wallet = Wallet(cash)
            history = []
            common_index = data_map[tickers_input[0]].index
            
            progress = st.progress(0)
            
            for i, date in enumerate(common_index):
                if i % 50 == 0: progress.progress(i / len(common_index))
                
                current_prices_snapshot = {}

                for ticker in tickers_input:
                    df = data_map[ticker]
                    if date not in df.index: continue
                    
                    row = df.loc[date]
                    current_price = row['close']
                    current_prices_snapshot[ticker] = current_price
                    
                    # 1. UPDATE TRACKING (High Watermark)
                    wallet.update_high_watermark(ticker, current_price)
                    
                    # 2. PREPARE CONTEXT VARIABLES
                    holding = wallet.get_holding(ticker)
                    avg_p = holding['avg_price']
                    max_p = holding['max_price']
                    amt = holding['amount']
                    
                    # Calculate profit percentage (avoid division by zero)
                    if avg_p > 0:
                        pct_profit = (current_price - avg_p) / avg_p
                    else:
                        pct_profit = current_price 
                    
                    context = {
                        "avg_price": avg_p,
                        "max_price": max_p,
                        "pct_profit": pct_profit,
                        "cash": wallet.cash,
                        "amount": amt
                    }

                    # 3. EVALUATE BUY
                    # Condition: User Rule + We must have cash
                    if evaluate_condition(row, buy_condition, context):
                        if current_price <= 0: continue
                        amount_to_buy = int((wallet.cash * buy_size_pct) / current_price)
                        if amount_to_buy > 0:
                            wallet.buy(ticker, current_price, amount_to_buy)
                    
                    # 4. EVALUATE SELL
                    # Condition: User Rule + We must actually own the stock
                    if amt > 0:
                        # Re-eval context just in case buy changed something (though buy/sell usually separate)
                        if evaluate_condition(row, sell_condition, context):
                            amount_to_sell = int(amt * sell_size_pct)
                            if amount_to_sell > 0:
                                wallet.sell(ticker, current_price, amount_to_sell)

                # Log
                total_val = wallet.get_total_value(current_prices_snapshot)
                history.append({"Date": date, "Portfolio Value": total_val, "Cash": wallet.cash})
            
            progress.empty()
            
            # VISUALIZATION
            res_df = pd.DataFrame(history).set_index("Date")
            final_v = res_df["Portfolio Value"].iloc[-1]
            
            st.metric("Final Value", f"{final_v:,.2f} SEK", delta=f"{final_v - cash:,.2f}")
            
            st.line_chart(res_df[["Portfolio Value", "Cash"]])
            
            if wallet.stocks:
                st.subheader("Ending Portfolio")
                # Display nicely formatted table
                recs = []
                for t, d in wallet.stocks.items():
                    curr = data_map[t].iloc[-1]['close']
                    pl_pct = ((curr - d['avg_price']) / d['avg_price']) * 100
                    recs.append({
                        "Ticker": t, 
                        "Amount": d['amount'], 
                        "Avg Buy": f"{d['avg_price']:.2f}", 
                        "Current": f"{curr:.2f}",
                        "P/L": f"{pl_pct:.2f}%"
                    })
                st.dataframe(pd.DataFrame(recs))