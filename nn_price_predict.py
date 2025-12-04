import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# --- Configuration ---
FOLDER_PATH = 'finnance_data'
SEQUENCE_LENGTH = 60 # Number of past days the LSTM looks at
EPOCHS = 50 
BATCH_SIZE = 32
FEATURE_COLUMNS = ['Return', 'Volume', 'RSI', 'MACD_Hist']
MODEL_FILENAME = 'best_stock_predictor.keras'

# --- 1. Feature Engineering Function ---
def add_technical_indicators(df):
    """Calculates RSI, MACD, and MACD Histogram and adds them to the DataFrame."""
    
    # --- RSI (Relative Strength Index) ---
    window_length = 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    avg_gain = gain.ewm(alpha=1/window_length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window_length, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # --- MACD (Moving Average Convergence Divergence) ---
    k = df['Close'].ewm(span=12, adjust=False).mean() # Fast EMA
    d = df['Close'].ewm(span=26, adjust=False).mean() # Slow EMA
    
    df['MACD'] = k - d
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df

# --- 2. Data Loading and Preprocessing Function ---
def load_and_process_data(folder_path):
    """Loads all CSVs, calculates features and target, and concatenates results."""
    all_features_data = []
    all_target_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            path = os.path.join(folder_path, filename)
            df = pd.read_csv(path, parse_dates=True, index_col=0)
            
            # 1. Add Features
            df = add_technical_indicators(df)

            # 2. Calculate Returns and Target
            df['Return'] = df['Close'].pct_change()
            # Target is 1 if tomorrow's close > today's close
            df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
            
            # 3. Drop NaNs introduced by rolling windows (RSI, MACD, etc.) and the target shift
            df.dropna(inplace=True)
            
            # 4. Append
            if not df.empty:
                all_features_data.append(df[FEATURE_COLUMNS].values)
                all_target_data.append(df['Target'].values)
            
    return all_features_data, all_target_data

# --- 3. Sliding Window Sequence Creator ---
def create_sequences(features, targets, seq_length):
    """Converts time-series data into sequences (X) and corresponding labels (y)."""
    X = []
    y = []
    for i in range(len(features) - seq_length):
        # Sequence: past N days (e.g., 60 days)
        seq = features[i:i+seq_length]
        # Label: the outcome on the day *after* the sequence ends
        label = targets[i+seq_length] 
        X.append(seq)
        y.append(label)
    return np.array(X), np.array(y)


# ----------------------------------------------------
#               MAIN EXECUTION BLOCK
# ----------------------------------------------------

print(f"Starting data loading from folder: {FOLDER_PATH}")

# Load and calculate initial features/targets
feature_list, target_list = load_and_process_data(FOLDER_PATH)

if not feature_list:
    print(f"Error: No data found or processing failed in {FOLDER_PATH}.")
else:
    # 1. Scaling (Fit on combined data)
    print("Scaling data...")
    all_features_concatenated = np.vstack(feature_list)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(all_features_concatenated)

    # 2. Create final scaled sequences
    X_all, y_all = [], []
    for features, target in zip(feature_list, target_list):
        features_scaled = scaler.transform(features)
        
        # Create sequences for each ticker
        X_seq, y_seq = create_sequences(features_scaled, target, SEQUENCE_LENGTH)
        
        if len(X_seq) > 0:
            X_all.append(X_seq)
            y_all.append(y_seq)

    X = np.vstack(X_all)
    y = np.concatenate(y_all)

    print(f"Total sequences created: {len(X)}")

    # 3. Split Data (Using time-series split logic, not random split)
    # We split by index to maintain time sequence integrity
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Determine input shape for the model
    input_shape = (X_train.shape[1], X_train.shape[2]) # (SEQUENCE_LENGTH, num_features)
    
    print(f"Training set size: {len(X_train)}")
    print(f"Input shape: {input_shape}")

    # 4. Model Definition
    print("Building LSTM Model...")
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(units=100, return_sequences=False))
    model.add(Dropout(0.3))
    model.add(Dense(units=1, activation='sigmoid'))

    model.compile(optimizer='adam', 
                    loss='binary_crossentropy', 
                    metrics=['accuracy'])

    # 5. Callbacks (Early Stopping and Checkpoints)
    early_stop = EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True, verbose=1)
    checkpoint = ModelCheckpoint(filepath=MODEL_FILENAME, monitor='val_loss', save_best_only=True, verbose=1)

    # 6. Training
    print("Starting training...")
    model.fit(
        X_train, y_train, 
        epochs=EPOCHS,  
        batch_size=BATCH_SIZE, 
        validation_data=(X_test, y_test),
        callbacks=[early_stop, checkpoint] 
    )
    
    print(f"\nTraining finished. Best model saved as: {MODEL_FILENAME}")
    
    # Evaluate the best saved model on the test set
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Final Test Accuracy: {acc*100:.2f}%")
    
    # Now you can proceed to the Confusion Matrix step!