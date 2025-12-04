import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from datetime import date, timedelta
import os

# --- Configuration (MUST MATCH TRAINING CODE) ---
SEQUENCE_LENGTH = 60 # Number of past days the LSTM looks at
FEATURE_COLUMNS = ['Return', 'Volume', 'RSI', 'MACD_Hist']
MODEL_FILENAME = 'best_stock_predictor.keras' # Ensure this file is present

# --- 1. Feature Engineering Function (Modified for Streamlit) ---
def add_technical_indicators(df):
    """Calculates RSI, MACD, and MACD Histogram and adds them to the DataFrame."""
    
    # --- RSI (Relative Strength Index) ---
    window_length = 14
    delta = df['Close'].diff()
    # Handle the case where all deltas are 0 to prevent division by zero in rs calculation
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # Use EWM for Rolling Averages
    avg_gain = gain.ewm(span=window_length, adjust=False).mean() # span is equivalent to 1/alpha for alpha=1/window
    avg_loss = loss.ewm(span=window_length, adjust=False).mean()
    
    # Check for zero average loss to prevent division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = avg_gain / avg_loss
    # Replace infinite/NaN results from division by zero or 0/0
    rs[rs == np.inf] = 50.0 # Arbitrary high value or clip
    rs = rs.fillna(0)
    
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # --- MACD (Moving Average Convergence Divergence) ---
    k = df['Close'].ewm(span=12, adjust=False).mean() # Fast EMA
    d = df['Close'].ewm(span=26, adjust=False).mean() # Slow EMA
    
    df['MACD'] = k - d
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df

# --- 2. Data Loading and Preprocessing Function (Simplified) ---
@st.cache_data
def load_data(ticker):
    """Loads data, adds indicators, and calculates returns/target for a single ticker."""
    try:
        end_date = date.today()
        # Fetch enough data to cover the longest indicator window (26 days for MACD) + sequence length
        start_date = end_date - timedelta(days=400) # Get roughly a year of data
        
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.error(f"Could not retrieve data for {ticker}. Check the ticker symbol.")
            return None
        
        # 1. Add Features
        data = add_technical_indicators(data.copy())
        
        # 2. Calculate Returns and Target (Target is only for visualization/reference in app)
        data['Return'] = data['Close'].pct_change()
        data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
        
        # 3. Drop NaNs
        data.dropna(inplace=True)
        
        return data
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None

# --- 3. Sequence Creator for Prediction ---
def create_prediction_sequence(data, scaler):
    """Prepares the last N days of data for model prediction."""
    
    # Get the last 'SEQUENCE_LENGTH' rows of the feature data
    features = data[FEATURE_COLUMNS].tail(SEQUENCE_LENGTH).values
    
    if features.shape[0] < SEQUENCE_LENGTH:
        st.error(f"Not enough data to create a sequence of length {SEQUENCE_LENGTH}. Need at least {SEQUENCE_LENGTH} days.")
        return None, None
    
    # Scale the features using the trained scaler (or one re-fitted on historical data)
    features_scaled = scaler.transform(features)
    
    # Reshape for LSTM input: (1, SEQUENCE_LENGTH, num_features)
    X = np.array([features_scaled])
    
    # Get the latest close price for contextual display
    latest_close = data['Close'].iloc[-1]
    
    return X, latest_close

# --- 4. Streamlit App Layout ---
def main():
    st.set_page_config(page_title="LSTM Stock Trend Predictor", layout="centered")
    st.title("📈 LSTM Stock Trend Predictor")
    st.markdown("Use a Long Short-Term Memory (LSTM) model to predict the next day's price trend (Up/Down).")
    
    
    # --- Sidebar Inputs ---
    st.sidebar.header("Configuration")
    ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, GOOGL)", value='TSLA').upper()
    
    # NOTE: In a real deployment, the scaler should be saved and loaded alongside the model!
    st.sidebar.warning("Note: The model is loaded, but the MinMaxScaler used for training needs to be re-fitted or loaded separately for a true real-time app.")
    
    # The app assumes the model is already trained and saved as 'best_stock_predictor.keras'
    if not os.path.exists(MODEL_FILENAME):
        st.error(f"The trained model file **{MODEL_FILENAME}** was not found. Please run the training script and save the model first.")
        return

    # --- Load Model and Data ---
    with st.spinner('Loading Model and Data...'):
        model = st.cache_resource(load_model)(MODEL_FILENAME)
        data = load_data(ticker)
        
        if data is None:
            return # Exit if data loading failed

        # --- Re-fit a Scaler on the loaded data (A robust app would load the saved scaler) ---
        # NOTE: This scaler is ONLY being used for the *prediction* step's data normalization.
        # For true production deployment, the scaler used during *training* must be saved and loaded.
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Fit the scaler on all historical features for the selected ticker
        scaler.fit(data[FEATURE_COLUMNS].values)
        
        # Prepare the prediction sequence
        X_pred, latest_close = create_prediction_sequence(data, scaler)
    
    if X_pred is None:
        return # Exit if sequence creation failed

    # --- Prediction Button ---
    if st.button(f'Predict Trend for {ticker}', key='predict_button', help="Predicts if tomorrow's Close > today's Close"):
        st.subheader(f"Prediction for {ticker}")
        
        # Make Prediction
        prediction = model.predict(X_pred)[0][0]
        
        # Determine the trend
        if prediction >= 0.5:
            trend = "**UP** (Price is likely to increase)"
            color = 'green'
            emoji = '⬆️'
        else:
            trend = "**DOWN** (Price is likely to decrease or stay the same)"
            color = 'red'
            emoji = '⬇️'
        
        st.metric(
            label=f"Predicted Trend for Tomorrow ({date.today() + timedelta(days=1)} trading day)",
            value=f"{emoji} {trend}",
            delta=f"Certainty: {prediction*100:.2f}%",
            delta_color=color if color == 'green' else 'inverse'
        )

        st.info(f"Latest Close Price: **${latest_close:.2f}**")
        st.caption(f"Based on a {SEQUENCE_LENGTH}-day lookback window.")

    # --- Data Visualization ---
    st.subheader(f"Historical Price & Features for {ticker}")
    st.line_chart(data['Close'].tail(180), use_container_width=True)
    st.dataframe(data[FEATURE_COLUMNS + ['Close', 'Target']].tail(5))


if __name__ == '__main__':
    main()