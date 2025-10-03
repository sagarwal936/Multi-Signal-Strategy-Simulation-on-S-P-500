# Strategy Name : Volatility Breakout Strategy
# Signal Logic  : Buy if daily return > rolling 20-day std dev
# Category      : Volatility

import pandas as pd
from Strategy import Strategy
from constants import Close_Col

class VolatilityBreakoutStrategy(Strategy):
    """
    Implements a volatility breakout strategy.
    BUY: When the daily return exceeds the rolling 20-day std of returns.
    """
    def generate_signals(self):
        """
        Generates trading signals based on the volatility breakout logic.
        """

        signals_df = self.data.copy()

        # Calculate daily returns
        signals_df['daily_return'] = signals_df[Close_Col].pct_change()
        
        # Calculate the rolling 20-day std of returns
        signals_df['volatility'] = signals_df['daily_return'].rolling(window=20).std()

        # Init the signal column
        signals_df['signal'] = 0

        # Generating the BUY signal
        signals_df.loc[signals_df['daily_return'] > signals_df['volatility'], 'signal'] = 1

        signals_df['signal'] = signals_df['signal'].shift(1)
        signals_df.dropna(inplace=True)
        
        return signals_df