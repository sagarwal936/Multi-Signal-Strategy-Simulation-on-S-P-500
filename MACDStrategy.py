# Strategy Name : MACD Strategy
# Signal Logic  : Buy if MACD line crosses above signal line
# Category      : Price + momentum

import pandas as pd
from Strategy import Strategy
from constants import Close_Col

class MACDStrategy(Strategy):
    """
    Implements the MACD crossover strategy using only pandas.
    BUY: When the MACD line crosses above the MACD signal line.
    """
    def generate_signals(self):
        """
        Generates trading signals based on the MACD crossover logic.
        """
        signals_df = self.data.copy()
        short_ema_period = 12
        long_ema_period = 26
        signal_ema_period = 9

        # Calculate short-term and long-term EMAs
        short_ema = signals_df[Close_Col].ewm(span=short_ema_period, adjust=False).mean()
        long_ema = signals_df[Close_Col].ewm(span=long_ema_period, adjust=False).mean()

        # Calculate the MACD line
        signals_df['MACD_line'] = short_ema - long_ema
        
        # Calculate the Signal line (EMA of the MACD line)
        signals_df['MACD_signal_line'] = signals_df['MACD_line'].ewm(span=signal_ema_period, adjust=False).mean()
        
        # Create position column
        signals_df['position'] = 0
        signals_df.loc[signals_df['MACD_line'] > signals_df['MACD_signal_line'], 'position'] = 1
        
        # The buy signal is the day the position changes from 0 to 1
        signals_df['signal'] = signals_df['position'].diff().apply(lambda x: 1 if x == 1 else 0)

        signals_df['signal'] = signals_df['signal'].shift(1)
        signals_df.dropna(inplace=True)

        return signals_df.drop(columns=['position'])