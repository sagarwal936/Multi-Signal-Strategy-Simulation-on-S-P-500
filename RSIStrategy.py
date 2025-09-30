# Strategy Name : RSI Strategy
# Signal Logic  : Buy if RSI < 30 (oversold)
# Category      : Oscillator

import pandas as pd
from Strategy import Strategy

class RSIStrategy(Strategy):
    """
    Implements an RSI (Relative Strength Index) strategy using only pandas.
    Buy signal: When the RSI drops below 30 (indicating an oversold condition).
    """
    def generate_signals(self):
        """
        Generates trading signals based on the RSI oversold condition.
        """
        signals_df = self.data.copy()
        rsi_period = 14

        # Calculate price changes
        delta = signals_df['AdjClose'].diff()

        # Separate gains (positive changes) and losses (- changes)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calculate the average gain and average loss using a smoothed average (EMA)
        avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        
        # Calculate the Relative Strength (RS)
        rs = avg_gain / avg_loss
        
        # Calculate the RSI
        signals_df['RSI'] = 100 - (100 / (1 + rs))
        
        # Initialize signal column
        signals_df['signal'] = 0
        
        # Generate buy signal (1)
        # Condition: RSI is less than 30
        signals_df.loc[signals_df['RSI'] < 30, 'signal'] = 1
        
        signals_df['signal'] = signals_df['signal'].shift(1)
        signals_df.dropna(inplace=True)
        
        return signals_df