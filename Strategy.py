# Strategy.py

import pandas as pd

class Strategy:
    """
    Base classe for all trading strategies.
    """
    def __init__(self, data):
        """
        Initializes the Strategy with historical price data.

        Args:
        data (pd.DataFrame): Company DataFrame
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input 'data' must be a pandas DataFrame.")
        self.data = data
    
    def generate_signals(self):
        """
        Generates trading signals based on the strategy's logic.
        To be overrident by the 4 new subclasses.

        Returns:
        pd.DataFrame: The original data DataFrame with a new 'signal' column. Signal values: 1 for BUY, 0 for HODL.
        """
        # This will just create a column of zeros.
        signal_df = self.data.copy()
        signals_df['signal'] = 0
        return signals_df