import sys
import argparse
from datetime import timedelta
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf

def fetch_data(ticker: str, period='5y', interval='1d'):
    t = yf.Ticker(ticker)
    # historical prices
    hist = t.history(period=period, interval=interval).rename_axis('date').reset_index()
    if hist.empty:
        raise ValueError("No historical price data found for ticker: " + ticker)
    # financials (quarterly & annual)
    fin_q = t.quarterly_financials.T if hasattr(t, 'quarterly_financials') else pd.DataFrame()
    fin_a = t.financials.T if hasattr(t, 'financials') else pd.DataFrame()
    bs_q = t.quarterly_balance_sheet.T if hasattr(t, 'quarterly_balance_sheet') else pd.DataFrame()
    bs_a = t.balance_sheet.T if hasattr(t, 'balance_sheet') else pd.DataFrame()

    # Ensure dataframes have datetime index if available
    for df in [fin_q, fin_a, bs_q, bs_a]:
        if isinstance(df, pd.DataFrame) and not df.empty:
            df.index = pd.to_datetime(df.index)

    info = t.info if hasattr(t, 'info') else {}
    return hist, fin_q, fin_a, bs_q, bs_a, info

def pick_financial_value(df_list, field_names):
    # df_list: list of dataframes indexed by date (most granular first)
    # field_names: list of possible column names to search for
    # returns a combined Series indexed by date where each date takes nearest previous financial report value
    # We'll create a DataFrame by concatenating available dfs
    frames = []
    for df in df_list:
        if isinstance(df, pd.DataFrame) and not df.empty:
            # keep only candidate columns
            avail = [c for c in field_names if c in df.columns]
            if avail:
                frames.append(df[avail])
    if not frames:
        return None
    allf = pd.concat(frames, axis=0).sort_index()
    # fill forward to propagate last known value
    allf = allf.ffill()
    # pick first available column per row
    def first_valid(row):
        for c in row.index:
            if pd.notna(row[c]):
                return row[c]
        return np.nan
    series = allf.apply(first_valid, axis=1)
    series.name = field_names[0]
    return series

def align_financials_to_prices(hist, fin_q, fin_a, bs_q, bs_a, info):
    hist = hist.copy()
    hist['date'] = pd.to_datetime(hist['date'])
    hist.set_index('date', inplace=True)
    # Revenue / Total Revenue
    revenue_series = pick_financial_value([fin_q, fin_a], ['Total Revenue', 'Revenue', 'totalRevenue'])
    # Net Income / Net Income Common Stockholders
    netincome_series = pick_financial_value([fin_q, fin_a], ['Net Income', 'Net Income Common Stockholders', 'NetIncome'])
    # Total debt: try 'Total Debt' or from balance sheet 'Long Term Debt' + 'Short Long Term Debt' etc.
    debt_series = pick_financial_value([bs_q, bs_a], ['Total Debt', 'Total liabilities', 'Total Liab', 'TotalLiab', 'Total Liabilities'])
    # Market cap: try to compute from sharesOutstanding when available in info; otherwise fallback to info.marketCap constant
    shares_series = None
    if 'sharesOutstanding' in info and info.get('sharesOutstanding') is not None:
        # assume constant across dates as fallback
        shares_val = info['sharesOutstanding']
        marketcap_series = pd.Series(index=hist.index, data=hist['Close'].values * shares_val)
    else:
        mv = info.get('marketCap', np.nan)
        marketcap_series = pd.Series(index=hist.index, data=mv)

    # Align each financial series to price dates by forward-fill the most recent prior report
    def align_series(series):
        if series is None:
            return pd.Series(index=hist.index, data=np.nan)
        # reindex financial series to hist.index by forward filling from nearest previous date
        s = series.sort_index()
        s = s.reindex(hist.index, method='ffill')
        return s

    revenue_aligned = align_series(revenue_series)
    profit_aligned = align_series(netincome_series)
    debt_aligned = align_series(debt_series)
    marketcap_aligned = marketcap_series

    df = hist[['Close']].copy()
    df['revenue'] = revenue_aligned.values
    df['profit'] = profit_aligned.values
    df['debt'] = debt_aligned.values
    df['marketcap'] = marketcap_aligned.values
    # Drop rows with all financial NaNs
    df = df.dropna(subset=['Close'])
    return df

def prepare_sequences(df, seq_len=30, target_shift=1):
    # Input features: Close, profit, debt, marketcap, revenue
    features = ['Close', 'profit', 'debt', 'marketcap', 'revenue']
    X_all = df[features].copy()
    # Fill missing financials with forward-fill then zero (if still NaN)
    X_all = X_all.fillna(method='ffill').fillna(0)
    # Scale features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X_all)
    Xs = []
    ys = []
    for i in range(len(X_scaled) - seq_len - target_shift + 1):
        Xs.append(X_scaled[i:i+seq_len])
        # predict next close (unscaled original Close to compute realistic target)
        target_close = X_all['Close'].iloc[i+seq_len+target_shift-1]
        ys.append(target_close)
    Xs = np.array(Xs)
    ys = np.array(ys).reshape(-1, 1)
    # scale targets separately
    y_scaler = MinMaxScaler()
    ys_scaled = y_scaler.fit_transform(ys)
    return Xs, ys_scaled, scaler, y_scaler

def build_model(seq_len, n_features):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(seq_len, n_features)),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def train_for_ticker(ticker, period='5y', interval='1d', seq_len=30, epochs=30, batch_size=32):
    hist, fin_q, fin_a, bs_q, bs_a, info = fetch_data(ticker, period=period, interval=interval)
    df = align_financials_to_prices(hist, fin_q, fin_a, bs_q, bs_a, info)
    if df[['revenue','profit','debt','marketcap']].isna().all().all():
        print("Warning: financial fields missing or not found for", ticker)
    X, y, scaler, y_scaler = prepare_sequences(df, seq_len=seq_len)
    if X.shape[0] < 10:
        raise ValueError("Not enough sequence samples to train. Try increasing period or lowering seq_len.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = build_model(seq_len, X.shape[2])
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
    ]
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs,
                        batch_size=batch_size, callbacks=callbacks, verbose=2)
    # Save model and scalers
    model.save(f"{ticker.replace(':','_')}_lstm_model")
    import joblib
    joblib.dump({'X_scaler': scaler, 'y_scaler': y_scaler}, f"{ticker.replace(':','_')}_scalers.pkl")
    print("Model and scalers saved.")
    return model, history, scaler, y_scaler, df

def main():
    parser = argparse.ArgumentParser(description="Train LSTM on Stockholm ticker using yfinance")
    parser.add_argument("ticker", help="Ticker symbol (include .ST for Stockholm, e.g. ERIC-B.ST)")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--seq", type=int, default=30)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()
    model, history, scaler, yscaler, df = train_for_ticker(args.ticker, period=args.period, interval=args.interval,
                                                           seq_len=args.seq, epochs=args.epochs)
    # print last few processed rows
    print(df.tail(5))

if __name__ == "__main__":
    main()