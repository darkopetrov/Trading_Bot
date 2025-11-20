import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt

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

    def get_total_market_value(self, current_prices):
        val = self.cash
        for ticker, data in self.stocks.items():
            price = current_prices.get(ticker, data['avg_price'])
            val += data['amount'] * price
        return val
    
    def get_total_buy_value(self):
        val = 0.0
        for ticker, data in self.stocks.items():
            val += data['amount'] * data['avg_price']
        val = val + self.cash
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
            elif "bb" in ind:
                window = int(ind.split("_")[1])
                df[f'bb_middle_{window}'] = df['close'].rolling(window=window).mean()
                df[f'bb_std_{window}'] = df['close'].rolling(window=window).std()
                df[f'bb_upper_{window}'] = df[f'bb_middle_{window}'] + (df[f'bb_std_{window}'] * 2)
                df[f'bb_lower_{window}'] = df[f'bb_middle_{window}'] - (df[f'bb_std_{window}'] * 2)
            elif "macd" in ind:
                # Default MACD uses 12-period EMA, 26-period EMA, and 9-period EMA for signal line
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                df['macd'] = exp1 - exp2
                df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
                df['macd_histogram'] = df['macd'] - df['signal_line']
            elif "stoch" in ind: # Stochastic Oscillator
                window = int(ind.split("_")[1])
                df['lowest_low'] = df['low'].rolling(window=window).min()
                df['highest_high'] = df['high'].rolling(window=window).max()
                df[ind] = ((df['close'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low'])) * 100
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
    * `bb_middle_20`, `bb_upper_20`, `bb_lower_20` (for Bollinger Bands)
    * `macd`, `signal_line`, `macd_histogram` (for MACD)
    * `stoch_14` (for Stochastic Oscillator)
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
    st.markdown("""
    **Bollinger Bands Example:**
    * **Buy:** `close < bb_lower_20`
    * **Sell:** `close > bb_upper_20`""")

# --- INPUT SECTION ---
st.header("1. Setup")
tickers_input = st.multiselect("Tickers", ["AZN.ST", "EVO.ST", "VOLV-B.ST", "TELIA.ST", "SKF-B.ST", "NDA-SE.ST", "ESSITY-B.ST", "HEXA-B.ST", "TEL2-B.ST", "SWED-A.ST", "ERIC-B.ST", "HM-B.ST", "ATCO-A.ST", "SHB-A.ST", "SCA-B.ST", "INVE-B.ST", "ALFA.ST", "ASSA-B.ST", "SEB-A.ST", "EPI-A.ST", "SAND.ST", "ADDT-B.ST", "EQT.ST", "NIBE-B.ST", "INDU-C.ST", "LIFCO-B.ST", "BOL.ST", "SKA-B.ST", "SAAB-B.ST", "ABB.ST"], ["VOLV-B.ST"])
start_d = st.date_input("Start", pd.to_datetime("2022-01-01"))
end_d = st.date_input("End", pd.to_datetime("2023-12-01"))

# Typed Input for Cash
cash = st.number_input("Initial Cash", value=100000, step=1000)

st.divider()
st.header("2. Indicators")
indicators_raw = st.text_area("Define Indicators", "sma_50, sma_200, rsi_14, bb_20, macd, stoch_14")
indicator_list = [x.strip() for x in indicators_raw.split(",") if x.strip()]

st.divider()
st.header("3. Buy Logic & Sizing")

st.subheader("Dynamic Position Sizing")

# Initialize session state with the new 'type' field
if 'buy_rules' not in st.session_state:
    st.session_state.buy_rules = [
        {"type": "% Cash", "cond": "low < bb_lower_20", "size": 2.0},
        {"type": "% Position", "cond": "pct_profit < -0.05", "size": 200.0} 
    ]

# Function to add a new blank rule
def add_rule():
    st.session_state.buy_rules.append({"type": "% Cash", "cond": "pct_profit < -0.05", "size": 5.0})

# Function to remove the last rule
def remove_rule():
    if len(st.session_state.buy_rules) > 0:
        st.session_state.buy_rules.pop()

# Display the Rules as a List with 4 Columns
for i, rule in enumerate(st.session_state.buy_rules):
    # Columns: [Index] [Type] [Condition] [Size]
    c1, c2, c3, c4 = st.columns([0.1, 0.25, 0.45, 0.2])
    
    with c1:
        st.markdown(f"**#{i+1}**")
    with c2:
        # Ensure 'type' exists (backward compatibility fix)
        if 'type' not in rule: rule['type'] = "% Cash"
        rule['type'] = st.selectbox("Type", ["% Cash", "% Position"], key=f"rule_t_{i}", label_visibility="collapsed")
    with c3:
        rule['cond'] = st.text_input("Condition", rule['cond'], key=f"rule_c_{i}", label_visibility="collapsed", placeholder="e.g. pct_profit < -0.10")
    with c4:
        rule['size'] = st.number_input("Size %", value=rule['size'], key=f"rule_s_{i}", label_visibility="collapsed")

# Buttons
b1, b2 = st.columns(2)
b1.button("➕ Add Rule", on_click=add_rule)
b2.button("➖ Remove Last", on_click=remove_rule)

st.divider()
st.header("4. Sell Logic")
st.markdown("Use variables: `pct_profit`, `avg_price`, `max_price`")

# Initialize session state for sell rules
if 'sell_rules' not in st.session_state:
    st.session_state.sell_rules = [
        {"cond": "pct_profit > 0.05", "size": 100.0},
        {"cond": "pct_profit < -0.10", "size": 100.0}
    ]

# Function to add a new blank sell rule
def add_sell_rule():
    st.session_state.sell_rules.append({"cond": "pct_profit > 0.05", "size": 100.0})

# Function to remove the last sell rule
def remove_sell_rule():
    if len(st.session_state.sell_rules) > 0:
        st.session_state.sell_rules.pop()

# Display the Sell Rules as a List with 3 Columns
for i, rule in enumerate(st.session_state.sell_rules):
    c1, c2, c3 = st.columns([0.1, 0.6, 0.3])
    
    with c1:
        st.markdown(f"**#{i+1}**")
    with c2:
        rule['cond'] = st.text_input("Condition", rule['cond'], key=f"sell_rule_c_{i}", label_visibility="collapsed", placeholder="e.g. pct_profit > 0.05")
    with c3:
        rule['size'] = st.number_input("Size %", value=rule['size'], key=f"sell_rule_s_{i}", label_visibility="collapsed")

# Buttons for sell rules
b_sell1, b_sell2 = st.columns(2)
b_sell1.button("➕ Add Sell Rule", on_click=add_sell_rule)
b_sell2.button("➖ Remove Last Sell Rule", on_click=remove_sell_rule)


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
            close_prices_history = []
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
                        pct_profit = 0.0
                    
                    context = {
                        "avg_price": avg_p,
                        "max_price": max_p,
                        "pct_profit": pct_profit,
                        "cash": wallet.cash,
                        "amount": amt
                    }

                    # 3. EVALUATE BUY
                    if current_price <= 0: continue
                    
                    # --- NEW LOGIC START ---
                    amount_to_buy = 0
                    rule_matched = False

                    # 1. Check Dynamic Rules
                    for rule in st.session_state.buy_rules:
                        if evaluate_condition(row, rule['cond'], context):
                            
                            size_val = rule['size'] / 100.0
                            
                            if rule['type'] == "% Position":
                                # BUY BASED ON EXISTING AMOUNT
                                # If Size is 100%, we buy exactly what we currently have (Doubling down)
                                current_amt = context['amount']
                                if current_amt > 0:
                                    amount_to_buy = int(current_amt * size_val)
                                else:
                                    # Fallback: If we have 0 shares, % Position implies 0 buy. 
                                    # Force a tiny cash buy or skip? Let's skip to be safe.
                                    amount_to_buy = 0 
                            else:
                                # BUY BASED ON CASH (Standard)
                                amount_to_buy = int((wallet.cash * size_val) / current_price)
                            
                            rule_matched = True
                            break # Stop after first match

                    # 2. If no rule matched, do nothing.
                    if not rule_matched:
                        amount_to_buy = 0
                    # --- NEW LOGIC END ---

                    if amount_to_buy > 0:
                        wallet.buy(ticker, current_price, amount_to_buy)
                    
                    # 4. EVALUATE SELL
                    if amt > 0:
                        amount_to_sell = 0
                        
                        # Check Dynamic Sell Rules
                        for rule in st.session_state.sell_rules:
                            if evaluate_condition(row, rule['cond'], context):
                                size_val = rule['size'] / 100.0
                                amount_to_sell = int(amt * size_val)
                                break # Stop after first match

                        # If no rule matched, or if the rule resulted in 0 amount to sell,
                        # we could add a default sell logic here if desired.
                        # For now, if no rule matches, amount_to_sell remains 0.

                        # Ensure we don't try to sell more than we own
                        amount_to_sell = min(amount_to_sell, amt)

                        if amount_to_sell > 0:
                            wallet.sell(ticker, current_price, amount_to_sell)

                # Log
                total_m_val = wallet.get_total_market_value(current_prices_snapshot)
                total_b_val = wallet.get_total_buy_value()
                history.append({"Date": date, "Portfolio Market Value": total_m_val, "Portfolio Buy Value": total_b_val, "Cash": wallet.cash})

                
            
            progress.empty()
            
            # VISUALIZATION
            res_df = pd.DataFrame(history).set_index("Date")
            final_v = res_df["Portfolio Buy Value"].iloc[-1]

            st.metric("Final Purchase Value", f"{final_v:,.2f} SEK", delta=f"{final_v - cash:,.2f}")
            st.metric("Final Market Value", f"{total_m_val:,.2f} SEK", delta=f"{total_m_val - cash:,.2f}")
            st.metric("Final Cash Left", f"{wallet.cash:,.2f} SEK", delta=f"{wallet.cash - cash:,.2f}")


            # --- CHART 1: Portfolio Value (Scaled) ---
            # We need to "melt" the dataframe to put multiple lines on one Altair chart
            chart_data = res_df.reset_index().melt('Date', value_vars=["Portfolio Market Value", "Portfolio Buy Value"])
            
            c1 = alt.Chart(chart_data).mark_line().encode(
                x='Date',
                # zero=False is the key setting here:
                y=alt.Y('value', title='Value (SEK)', scale=alt.Scale(zero=False)), 
                color='variable',
                tooltip=['Date', 'variable', 'value']
            ).interactive() # Makes it zoomable/pannable
            
            st.altair_chart(c1)

            # --- CHART 2: Stock Price (Scaled) ---
            if len(tickers_input) <= 1:
                aaa = []
                for i in range(len(raw_df.index)):
                    aaa.append({"Date": raw_df.index[i], "Price": raw_df['Close'][tickers_input[0]].iloc[i]})
                aaa_df = pd.DataFrame(aaa)
                
                c2 = alt.Chart(aaa_df).mark_line().encode(
                    x='Date',
                    y=alt.Y('Price', scale=alt.Scale(zero=False)), # Scales to Min/Max
                    tooltip=['Date', 'Price']
                ).interactive()
                st.altair_chart(c2)
            else:
                # For multiple tickers, we need to melt the DataFrame to plot all 'Close' prices
                # The raw_df already has the 'Close' prices for all tickers
                chart_data_multi_ticker = raw_df['Close'].reset_index().melt('Date', var_name='Ticker', value_name='Close')
            
                # Calculate percentage change from the first close price for each ticker
                # This requires grouping by ticker and then applying a transform
                chart_data_multi_ticker['Initial_Close'] = chart_data_multi_ticker.groupby('Ticker')['Close'].transform('first')
                chart_data_multi_ticker['Percentage_Change'] = (chart_data_multi_ticker['Close'] / chart_data_multi_ticker['Initial_Close'] - 1) * 100

                # Plotting Percentage_Change instead of Close
                c2 = alt.Chart(chart_data_multi_ticker).mark_line().encode(x='Date', 
                                                                       y=alt.Y('Percentage_Change', title='Price Movement (%)', scale=alt.Scale(zero=False)),
                    color='Ticker',
                tooltip=['Date', 'Ticker', 
                         alt.Tooltip('Close', format='.2f', title='Close Price'), 
                         alt.Tooltip('Percentage_Change', format='.2f', title='Movement %')
                        ]
                ).interactive()
                st.altair_chart(c2)

            # --- CHART 3: Cash --- 

            c3 = alt.Chart(res_df.reset_index()).mark_line().encode(
                x='Date',
                y=alt.Y('Cash', scale=alt.Scale(zero=False)),
                tooltip=['Date', 'Cash']
            ).interactive()
            st.altair_chart(c3)

            if wallet.stocks:
                st.subheader("Ending Portfolio")
                
                portfolio_data = []
                for ticker, data in wallet.stocks.items():
                    current_price = current_prices_snapshot.get(ticker, data['avg_price']) # Use last known price
                    market_value = data['amount'] * current_price
                    buy_value = data['amount'] * data['avg_price']
                    profit_loss = market_value - buy_value
                    pct_profit_loss = (profit_loss / buy_value) * 100 if buy_value > 0 else 0

                    portfolio_data.append({
                        "Ticker": ticker,
                        "Amount": data['amount'],
                        "Avg Price": f"{data['avg_price']:.2f}",
                        "Current Price": f"{current_price:.2f}",
                        "Market Value": f"{market_value:,.2f}",
                        "P/L": f"{profit_loss:,.2f}",
                        "P/L %": f"{pct_profit_loss:.2f}%"
                    })
                
                portfolio_df = pd.DataFrame(portfolio_data)
                st.dataframe(portfolio_df, hide_index=True)