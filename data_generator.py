import yfinance as yf
import pandas as pd
import os
import time
import wrds
import pandas as pd
from datetime import date, timedelta
from pathlib import Path


# Getting the list of S&P 500 tickers from WRDS
def get_sp500_tickers():
    sp500 = db.raw_sql("""
                            select a.*, b.date, b.ret
                            from crsp.msp500list as a,
                            crsp.msf as b
                            where a.permno=b.permno
                            and b.date >= a.start and b.date<= a.ending
                            and b.date>='01/01/2024'
                            order by date;
                            """, date_cols=['start', 'ending', 'date'])

    mse = db.raw_sql("""
                            select comnam, ncusip, namedt, nameendt, 
                            permno, shrcd, exchcd, hsiccd, ticker
                            from crsp.msenames
                            """, date_cols=['namedt', 'nameendt'])

    mse['nameendt']=mse['nameendt'].fillna(pd.to_datetime('today'))
    sp500_full = pd.merge(sp500, mse, how = 'left', on = 'permno')
    sp500_full = sp500_full.loc[(sp500_full.date>=sp500_full.namedt) \
                                & (sp500_full.date<=sp500_full.nameendt)]
    ticker_list = list(sp500_full['ticker'].unique())
    return ticker_list



class PriceLoader:
    def __init__(self, tickers, data_dir="data", start="2005-01-01", end="2025-01-01", fmt="parquet"):
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data_dir = Path(data_dir)
        self.fmt = fmt
        self.data_dir.mkdir(exist_ok=True, parents=True)

    def _save_path(self, ticker):
        return self.data_dir / f"{ticker}.{self.fmt}"

    def download_and_store(self, batch_size=50, pause=5):
        """
        Download all tickers in batches and store locally.
        """
        db = wrds.Connection()
        for i in range(0, len(self.tickers), batch_size):
            batch = self.tickers[i:i+batch_size]
            print(f"Fetching batch {i//batch_size + 1}: {batch}")
            data = yf.download(batch, start=self.start, end=self.end, auto_adjust=True, progress=False)["Close"]
            
            # Save each ticker separately
            for ticker in batch:
                if ticker not in data.columns:
                    continue  # skip missing tickers
                series = data[ticker].dropna()
                if len(series) < 2500:  # drop sparse tickers
                    continue
                df = series.to_frame(name="AdjClose")
                if self.fmt == "parquet":
                    df.to_parquet(self._save_path(ticker))
                else:
                    df.to_csv(self._save_path(ticker))
            time.sleep(pause)

    def load(self, ticker):
        file = self._save_path(ticker)
        if not file.exists():
            raise FileNotFoundError(f"No local file for {ticker}")
        if self.fmt == "parquet":
            return pd.read_parquet(file)
        else:
            return pd.read_csv(file, index_col=0, parse_dates=True)


if __name__ == "__main__":
    tickers = get_sp500_tickers()
    loader = PriceLoader(tickers, data_dir="sp500_prices", fmt="parquet")
    loader.download_and_store(batch_size=50, pause=5)
    
    ##  Load a ticker
    #df = loader.load("AAPL")

