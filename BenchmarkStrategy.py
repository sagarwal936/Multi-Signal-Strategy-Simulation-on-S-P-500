from Strategy import Strategy
from constants import Static_X

class BenchmarkStrategy(Strategy):
    """
    Implements a benchmark strategy.
    """
    def generate_signals(self):
        """
        Generates trading signals based on the benchmark logic.
        """
        signals_df = self.data.copy()
        signals_df['signal'] = 0
        signals_df.at[signals_df.index[0], 'signal'] = Static_X
        return signals_df