import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

class MonteCarloPredictor:
    def __init__(self, ticker, data_folder='./finance_data'):
        self.ticker = ticker.upper()
        self.data_path = f'./finnance_data/{ticker}.csv'
        self.df = None
        self.returns = None
        
    def load_data(self):
        # """Load stock data from CSV file"""
        # csv_files = list(Path(self.data_path).glob('*.csv'))
        # if not csv_files:
        #     raise FileNotFoundError(f"No CSV files found in {self.data_path}")
        
        self.df = pd.read_csv(self.data_path, index_col=0)
        return self.df
    
    def calculate_returns(self):
        """Calculate daily returns"""
        self.returns = self.df['Close'].pct_change().dropna()
        return self.returns
    
    def simulate(self, num_simulations=1000, days=252):
        """Run Monte Carlo simulation"""
        last_price = self.df['Close'].iloc[-1]
        mu = self.returns.mean()
        sigma = self.returns.std()
        
        simulations = np.zeros((num_simulations, days))
        
        for i in range(num_simulations):
            price = last_price
            for j in range(days):
                random_return = np.random.normal(mu, sigma)
                price *= (1 + random_return)
                simulations[i, j] = price
        
        return simulations
    
    def plot_results(self, simulations, title=None):
        """Plot simulation results"""
        plt.figure(figsize=(12, 6))
        plt.plot(simulations.T, alpha=0.1, color='blue')
        plt.xlabel('Days')
        plt.ylabel('Price ($)')
        plt.title(title or f'{self.ticker} Monte Carlo Simulation (1000 runs)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def get_statistics(self, simulations):
        """Calculate prediction statistics"""
        final_prices = simulations[:, -1]
        return {
            'Mean': np.mean(final_prices),
            'Median': np.median(final_prices),
            'Std Dev': np.std(final_prices),
            'Min': np.min(final_prices),
            'Max': np.max(final_prices),
            '5th Percentile': np.percentile(final_prices, 5),
            '95th Percentile': np.percentile(final_prices, 95)
        }

# Example usage
if __name__ == "__main__":
    ticker = 'LUG.ST'
    
    predictor = MonteCarloPredictor(ticker)
    predictor.load_data()
    predictor.calculate_returns()
    
    simulations = predictor.simulate(num_simulations=10000, days=252)
    stats = predictor.get_statistics(simulations)
    
    print(f"\n{ticker} - 252 Day Forecast Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value:.2f} sek")
    
    # predictor.plot_results(simulations)
    # Calculate percentage of simulations with price up and down
    final_prices = simulations[:, -1]
    last_price = predictor.df['Close'].iloc[-1]

    up_count = np.sum(final_prices > last_price)
    down_count = np.sum(final_prices < last_price)

    up_percent = (up_count / len(final_prices)) * 100
    down_percent = (down_count / len(final_prices)) * 100

    print(f"\n{ticker} - 252 Day Price Movement Probability:")
    print(f"Price Up: {up_percent:.2f}%")
    print(f"Price Down: {down_percent:.2f}%")
    print(f"Current Price: {last_price:.2f} sek")