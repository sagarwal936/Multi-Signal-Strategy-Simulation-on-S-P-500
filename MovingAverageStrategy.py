# Strategy Name : Moving Average Strategy
# Signal Logic  : Buy if 20-day MA > 50-day MA
# Category      : Price Average

import pandas as pd
from Strategy import Strategy
from constants import Close_Col

class MovingAverageStrategy(Strategy):
    """
    Implements a SMA crossover strategy.
    BUY: When the short-term SMA (20-day) > the long-term SMA (50-day).
    """

    def generate_signals(self):
        """
        Generates trading signals based on the SMA_20 > SMA_50 logic.
        """
        signals_df = self.data.copy()
        short_window = 20
        long_window = 50

        # Calculate the SMAs using pandas rolling mean
        signals_df['SMA_20'] = signals_df[Close_Col].rolling(window=short_window, min_periods=1).mean()
        signals_df['SMA_50'] = signals_df[Close_Col].rolling(window=long_window, min_periods=1).mean()

        # Init signals as 0
        signals_df['signal'] = 0

        # Create a 'position' column: 1 if short MA > long MA, else 0
        signals_df.loc[signals_df['SMA_20'] > signals_df['SMA_50'], 'signal'] = 1

        signals_df['signal'] = signals_df['signal'].shift(1)
        signals_df.dropna(inplace=True)

        return signals_df