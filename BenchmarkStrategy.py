from Strategy import Strategy

class BenchmarkStrategy(Strategy):
    """
    Implements a benchmark strategy.
    """
    def generate_signals(self, x):
        """
        Generates trading signals based on the benchmark logic.
        """
        signals_df = self.data.copy()
        signals_df['signal'] = 0
        signals_df.iloc[0]['signal'] = x
        return signals_df