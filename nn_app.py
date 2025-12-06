import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt
from datetime import date
from TICKER_DATA import TICKER_DATA
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# --- Configuration ---
FEATURE_COLUMNS = ['Return', 'Volume', 'RSI', 'MACD_Hist']
MODEL_FILENAME = 'best_stock_predictor.keras'

# Sort by category then name for a structured dropdown
TICKER_DATA.sort(key=lambda x: (x['category'], x['name']))

# Pre-made categories
PREDEFINED_CATEGORIES = {
    "ALL": [item['ticker'] for item in TICKER_DATA],
    "OMXS30": ["ABB.ST", "ADDT-B.ST", "ALFA.ST", "ASSS-B.ST", "AZN.ST", "ATCO-A.ST", "BOL.ST", "EPI-A.ST", "EQT.ST", "ERIC-B.ST", "ESSITY-B.ST", "EVO.ST", "HM-B.ST", "SHB-A.ST", "HEXA-B.ST", "INDU-C.ST", "INVE-B.ST", "LIFCO-B.ST", "NIBE-B.ST", "NDA-SE.ST", "SAAB-B.ST", "SAND.ST", "SCA-B.ST", "SEB-A.ST", "SKA-B.ST", "SKF-B.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST", "VOLV-B.ST"]
}

# -----------------------------------------------------------------------------
# 1. SMART WALLET
# -----------------------------------------------------------------------------
class Wallet:
    def __init__(self, cash: float):
        self.cash = cash
        self.stocks = {} 
        self.transaction_history = []

    def get_holding(self, ticker):
        return self.stocks.get(ticker, {'amount': 0, 'avg_price': 0.0})

    def buy(self, ticker, price, amount, date):
        if amount <= 0: return 
        if self.cash < (price * amount): return
        
        cost = price * amount
        self.cash -= cost
        self.transaction_history.append({
            'Date': date, 
            'Ticker': ticker, 
            'Type': 'BUY', 
            'Amount': amount, 
            'Price': price, 
            'Total Value': cost
        })
        
        current = self.get_holding(ticker)
        old_amount = current['amount']
        old_avg = current['avg_price']
        
        new_amount = old_amount + amount
        
        if old_amount > 0:
            total_val = (old_amount * old_avg) + cost
            new_avg = total_val / new_amount
        else:
            new_avg = price

        self.stocks[ticker] = {
            'amount': new_amount, 
            'avg_price': new_avg,
        }

    def sell(self, ticker, price, amount, date):
        current = self.get_holding(ticker)
        if current['amount'] >= amount and amount > 0:
            revenue = price * amount
            self.cash += revenue

            self.transaction_history.append({
                'Date': date, 
                'Ticker': ticker, 
                'Type': 'SELL', 
                'Amount': amount, 
                'Price': price, 
                'Total Value': revenue
            })

            remaining = current['amount'] - amount
            if remaining <= 0:
                if ticker in self.stocks: del self.stocks[ticker]
            else:
                self.stocks[ticker]['amount'] = remaining

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
# 2. DATA & MODEL ENGINE
# -----------------------------------------------------------------------------

@st.cache_data
def get_data(tickers, start, end):
    if not tickers: return pd.DataFrame()
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=False)
    return df

@st.cache_resource
def load_nn_model(model_path):
    if not os.path.exists(model_path):
        st.error(f"Model file not found at: {model_path}")
        return None
    return load_model(model_path)

def pre_calculate_features(df, ticker):
    # df.columns = [c.lower() for c in df.columns]
    
    # Feature 1: Return
    df['Return'] = df['Close'].pct_change()
    
    # Feature 2: Volume is already there
    
    # Feature 3: RSI
    window_length = 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.ewm(alpha=1/window_length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window_length, adjust=False).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Feature 4: MACD Hist
    k = df['Close'].ewm(span=12, adjust=False).mean()
    d = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = k - d
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Ensure volume is lowercase
    if 'Volume' in df.columns and 'volume' not in df.columns:
        df['volume'] = df['Volume']
        
    df = df.fillna(0)
    return df

# -----------------------------------------------------------------------------
# 3. UI & SIMULATION
# -----------------------------------------------------------------------------

st.set_page_config(page_title="NN Strategy Backtester", layout="centered")
st.title("🧠 Neural Network Strategy Backtester")

with st.expander("ℹ️ How this works"):
    st.markdown(f"""
    This tool backtests a trading strategy based on a pre-trained Keras neural network model (`{MODEL_FILENAME}`).
    
    1.  **Data Loading**: It fetches historical stock data for the selected tickers.
    2.  **Feature Calculation**: It calculates the same features the model was trained on: `{', '.join(FEATURE_COLUMNS)}`.
    3.  **Prediction**: For each day in the backtest period, it takes the last Sequence Length days of feature data, scales it, and feeds it to the model to get a prediction.
    4.  **Trading Logic**:
        *   **Buy**: If the model's prediction is above the 'Buy Threshold', it buys the stock.
        *   **Sell**: If the prediction is below the 'Sell Threshold', it sells the stock.
    """)

# --- INPUT SECTION ---
st.header("1. Setup")


# Create a list of display names for the multiselect, including category
ticker_display_list = [f"[{item['category']}] {item['name']} ({item['ticker']})" for item in TICKER_DATA]

# Create a mapping from display name to ticker
ticker_map = {f"[{item['category']}] {item['name']} ({item['ticker']})": item['ticker'] for item in TICKER_DATA}

# Create a reverse map from ticker to display name to easily find display names
ticker_to_display_map = {v: k for k, v in ticker_map.items()}

# --- Category Selection ---
category_options = ["Custom"] + list(PREDEFINED_CATEGORIES.keys())
selected_category = st.selectbox("Ticker Category", category_options)

default_selection = []
if selected_category == "Custom":
    default_ticker = "INVE-B.ST"
    default_display = [item for item in ticker_display_list if default_ticker in item]
    default_selection = default_display
else:
    # Get tickers for the selected category and map them to their display names
    category_tickers = PREDEFINED_CATEGORIES[selected_category]
    default_selection = [ticker_to_display_map[ticker] for ticker in category_tickers if ticker in ticker_to_display_map]

tickers_display_input = st.multiselect("Tickers", ticker_display_list, default=default_selection)

# Convert selected display names back to tickers
tickers_input = [ticker_map[display] for display in tickers_display_input]


# Date and cash inputs
start_d = st.date_input("Start", pd.to_datetime("2025-01-01"))
end_d = st.date_input("End", pd.to_datetime(date.today()))
cash = st.number_input("Initial Cash", value=100000, step=1000)
sequence_length = st.number_input("Sequence Length", value=60, step=1)


st.divider()
st.header("2. NN Strategy Settings")

col1, col2 = st.columns(2)
buy_threshold = col1.slider("Buy Threshold", 0.0, 1.0, 0.55, 0.01)
sell_threshold = col2.slider("Sell Threshold", 0.0, 1.0, 0.45, 0.01)
buy_size_pct = st.number_input("Buy Size (% of available cash)", value=10.0, step=1.0)
sell_size_pct = st.number_input("Sell Size (% of current holding)", value=100.0, step=1.0)


run = st.button("Run Simulation", type="primary")

# --- MAIN SIMULATION ---
if run:
    st.divider()
    st.header("📊 Simulation Results")
    
    model = load_nn_model(MODEL_FILENAME)
    if model is None:
        st.stop()
        
    if not tickers_input:
        st.error("Please select at least one ticker.")
        st.stop()

    with st.spinner("Processing data and running backtest..."):
        # 1. Load and process data for all tickers
        raw_df_multi = get_data(tickers_input, start_d - pd.Timedelta(days=sequence_length * 2), end_d)
        if raw_df_multi.empty:
            st.error("Could not download data for the selected tickers and date range.")
            st.stop()
            
        data_map = {}
        for ticker in tickers_input:
            # Handle single vs multi ticker download format
            if len(tickers_input) > 1:
                df = raw_df_multi.xs(ticker, axis=1, level=1).copy()
            else:
                df = raw_df_multi.copy()
            
            df_featured = pre_calculate_features(df, ticker)
            data_map[ticker] = df_featured[df_featured.index >= pd.to_datetime(start_d)]


        # 2. Setup Scaler (Fit on all available data for consistency)
        # In a real-world scenario, you would save and load the scaler used during training.
        # For this backtester, we fit it on the whole data range.
        combined_features = pd.concat([df[FEATURE_COLUMNS] for df in data_map.values()])
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(combined_features)
        
        # 3. Initialize Wallet and Simulation Loop
        wallet = Wallet(cash)
        history = []
        
        # Use a common index from the first ticker to drive the simulation
        common_index = data_map[tickers_input[0]].index
        
        progress_bar = st.progress(0)
        
        for i, date in enumerate(common_index):
            progress_bar.progress(i / len(common_index))
            
            current_prices_snapshot = {}
            
            for ticker in tickers_input:
                df = data_map[ticker]
                if date not in df.index:
                    continue
                
                row = df.loc[date]
                if len(tickers_input) == 1:
                    current_price = row['Close', ticker]
                else:
                    current_price = row['Close']
                current_prices_snapshot[ticker] = current_price

                # Check if we have enough data to form a sequence
                sequence_end_index = df.index.get_loc(date)
                if sequence_end_index < sequence_length - 1:
                    continue # Not enough historical data yet

                # 4. Prepare data for prediction
                sequence_start_index = sequence_end_index - (sequence_length -1)
                sequence_df = df.iloc[sequence_start_index : sequence_end_index + 1]
                
                # Check for NaNs or infs in sequence
                if sequence_df[FEATURE_COLUMNS].isnull().values.any() or not np.isfinite(sequence_df[FEATURE_COLUMNS].values).all():
                    continue

                # Scale the features
                features_scaled = scaler.transform(sequence_df[FEATURE_COLUMNS])
                X_pred = np.array([features_scaled]) # Reshape for model (1, seq_length, num_features)
                
                # 5. Get Prediction
                prediction = model.predict(X_pred)[0][0]
                print(f"Prediction for {ticker} on {date}: {prediction}")
                
                # 6. Execute Trading Logic
                holding = wallet.get_holding(ticker)

                # BUY LOGIC
                if prediction > buy_threshold and holding['amount'] == 0: # Only buy if not already holding
                    cash_to_use = wallet.cash * (buy_size_pct / 100.0)
                    amount_to_buy = int(cash_to_use / current_price)
                    if amount_to_buy > 0:
                        wallet.buy(ticker, current_price, amount_to_buy, date)

                # SELL LOGIC
                elif prediction < sell_threshold and holding['amount'] > 0:
                    amount_to_sell = int(holding['amount'] * (sell_size_pct / 100.0))
                    if amount_to_sell > 0:
                        wallet.sell(ticker, current_price, amount_to_sell, date)

            # Log portfolio value at the end of the day
            total_m_val = wallet.get_total_market_value(current_prices_snapshot)
            total_b_val = wallet.get_total_buy_value()
            history.append({"Date": date, "Portfolio Market Value": total_m_val, "Portfolio Buy Value": total_b_val, "Cash": wallet.cash})
            
        progress_bar.empty()
        
        # 7. Display Results
        if not history:
            st.warning("No trading activity occurred during the simulation period.")
            st.stop()
            
        res_df = pd.DataFrame(history).set_index("Date")
        final_m_val = res_df["Portfolio Market Value"].iloc[-1]
        
        st.metric("Final Market Value", f"{final_m_val:,.2f}", delta=f"{final_m_val - cash:,.2f}")
        st.metric("Final Cash Left", f"{wallet.cash:,.2f}", delta=f"{wallet.cash - cash:,.2f}")

        # Chart: Portfolio Value
        chart_data = res_df.reset_index().melt('Date', value_vars=["Portfolio Market Value", "Portfolio Buy Value"])
        c1 = alt.Chart(chart_data).mark_line().encode(
            x='Date',
            y=alt.Y('value', title='Value', scale=alt.Scale(zero=False)),
            color='variable',
            tooltip=['Date', 'variable', 'value']
        ).interactive()
        st.altair_chart(c1, width='stretch')

        # Chart: Stock Price vs Trades
        if len(tickers_input) == 1:
            ticker = tickers_input[0]
            st.header(ticker)
            price_df = data_map[ticker][['Close']].reset_index()
            price_df.columns = ['Date', 'Price']
            
            trades_df = pd.DataFrame(wallet.transaction_history)
            if not trades_df.empty:
                trades_df = trades_df[trades_df['Ticker'] == ticker]
            
            price_chart = alt.Chart(price_df).mark_line().encode(
                x='Date',
                y=alt.Y('Price', scale=alt.Scale(zero=False)),
                tooltip=['Date', 'Price']
            ).interactive()
            
            if not trades_df.empty:
                buy_points = alt.Chart(trades_df[trades_df['Type'] == 'BUY']).mark_point(
                    color='green', size=100, filled=True, shape='triangle-up'
                ).encode(x='Date', y='Price', tooltip=['Type', 'Amount', 'Price'])
                
                sell_points = alt.Chart(trades_df[trades_df['Type'] == 'SELL']).mark_point(
                    color='red', size=100, filled=True, shape='triangle-down'
                ).encode(x='Date', y='Price', tooltip=['Type', 'Amount', 'Price'])

                st.altair_chart(price_chart + buy_points + sell_points, width='stretch')
            else:
                 st.altair_chart(price_chart, width='stretch')
        elif len(tickers_input) > 1:
            for ticker in tickers_input:
                st.header(ticker)
                price_df = data_map[ticker][['Close']].reset_index()
                price_df.columns = ['Date', 'Price']
                
                trades_df = pd.DataFrame(wallet.transaction_history)
                if not trades_df.empty:
                    trades_df = trades_df[trades_df['Ticker'] == ticker]
                
                price_chart = alt.Chart(price_df).mark_line().encode(
                    x='Date',
                    y=alt.Y('Price', scale=alt.Scale(zero=False)),
                    tooltip=['Date', 'Price']
                ).interactive()
                
                if not trades_df.empty:
                    buy_points = alt.Chart(trades_df[trades_df['Type'] == 'BUY']).mark_point(
                        color='green', size=100, filled=True, shape='triangle-up'
                    ).encode(x='Date', y='Price', tooltip=['Type', 'Amount', 'Price'])
                    
                    sell_points = alt.Chart(trades_df[trades_df['Type'] == 'SELL']).mark_point(
                        color='red', size=100, filled=True, shape='triangle-down'
                    ).encode(x='Date', y='Price', tooltip=['Type', 'Amount', 'Price'])

                    st.altair_chart(price_chart + buy_points + sell_points, width='stretch')
                else:
                    st.altair_chart(price_chart, width='stretch')

        # Display ending portfolio and transaction history
        if wallet.stocks:
            st.subheader("Ending Portfolio")
            portfolio_data = []
            # Use last known prices for valuation
            last_prices = {t: data_map[t]['Close'].iloc[-1] for t in tickers_input}
            for ticker, data in wallet.stocks.items():
                current_price = last_prices.get(ticker, data['avg_price'])
                market_value = data['amount'] * current_price
                buy_value = data['amount'] * data['avg_price']
                pnl = market_value - buy_value
                pnl_pct = (pnl / buy_value) * 100 if buy_value > 0 else 0
                portfolio_data.append({
                    "Ticker": ticker, "Amount": data['amount'], "Avg Price": data['avg_price'],
                    "Last Price": current_price, "Market Value": market_value, "P/L %": pnl_pct
                })
            st.dataframe(pd.DataFrame(portfolio_data))

        if wallet.transaction_history:
            st.subheader("Transaction History")
            st.dataframe(pd.DataFrame(wallet.transaction_history))
