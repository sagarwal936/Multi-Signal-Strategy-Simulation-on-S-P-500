# Simulation.py

import time
import pandas as pd
from pathlib import Path
from collections import defaultdict

from config import Config
from data_generator import PriceLoader

#Had to add this to solve ciruclar imports from config in RSIStrategy
CLOSE_COL = "AdjClose"



class Simulation:
    """
    Run the simulation with a list of stocks and ONE strategy.
    Args:
        strat: str  (e.g., 'MovingAverage')
        file_path: directory with parquet files (default: 'sp500_prices/')
        tickers: 'all' or list of tickers
    """

    def __init__(self, strat: str, file_path="sp500_prices/", tickers="all"):
        self._strat = strat
        self._file_path = file_path
        self._tickers = tickers

        folder = Path(self._file_path)
        if self._tickers == "all":
            self._ticker_list = sorted([p.stem for p in folder.glob("*.parquet")])
        else:
            self._ticker_list = list(self._tickers)

        # loader for whatever tickers we are using
        self._loader = PriceLoader(tickers=self._ticker_list, data_dir=self._file_path)

        # outputs
        self._out_dir = Path("output")
        self._signals_dir = self._out_dir / "signals"
        self._out_dir.mkdir(parents=True, exist_ok=True)
        self._signals_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Returns:
            return_dataset: dict with portfolio series
            timing_df: per-ticker timing dataframe
        """
        def simulation(stock: str, strategy_name: str, initial_cash=0):
            # timing: load
            t_load0 = time.perf_counter()
            px = self._loader.load(stock)           # DataFrame with AdjClose and DatetimeIndex
            t_load1 = time.perf_counter()

            # build strategy
            if strategy_name not in Config.STRATEGY_MAP:
                raise ValueError(f"Unknown strategy: {strategy_name}")
            StrategyClass = Config.STRATEGY_MAP[strategy_name]
            Strat = StrategyClass(px)

            # timing: signal gen
            t_sig0 = time.perf_counter()
            z = Strat.generate_signals()            # expects columns: signal + AdjClose (Config.Close_Col), index=Date
            t_sig1 = time.perf_counter()

            # write per-ticker signal CSV for overlay chart
            sig_out = z.reset_index().rename(columns={"index": "Date"})
            # Ensure required columns exist
            assert Config.Close_Col in sig_out.columns, \
                f"'{Config.Close_Col}' not in signals for {stock} ({strategy_name})"
            assert "signal" in sig_out.columns, \
                f"'signal' not in signals for {stock} ({strategy_name})"
            sig_out = sig_out[["Date", Config.Close_Col, "signal"]].copy()
            sig_out.to_csv(self._signals_dir / f"{strategy_name}_{stock}.csv", index=False)

            # simulate (no shared cash here; mirrors your original approach)
            date_list = list(z.index)
            gross_holdings = {val: defaultdict() for val in date_list}
            company_holdings = 0
            cash = initial_cash

            t_sim0 = time.perf_counter()
            trade_count = 0
            for key in date_list:
                adj_close = z.loc[key][Config.Close_Col]
                signal = int(z.loc[key]["signal"])
                # buy 'signal' shares (can be >1 for benchmark day-1; 0/1 for tech strats)
                if signal > 0:
                    cash -= adj_close * signal
                    company_holdings += signal
                    trade_count += signal
                holdings = company_holdings * adj_close
                gross_holdings[key]["Cash"] = cash
                gross_holdings[key]["Holdings"] = holdings
                gross_holdings[key]["Total Assets"] = cash + holdings
            t_sim1 = time.perf_counter()

            timing_row = {
                "ticker": stock,
                "rows": len(date_list),
                "trades": int(trade_count),
                "load_s": t_load1 - t_load0,
                "signal_s": t_sig1 - t_sig0,
                "sim_s": t_sim1 - t_sim0,
                "total_s": (t_load1 - t_load0) + (t_sig1 - t_sig0) + (t_sim1 - t_sim0),
            }
            return gross_holdings, timing_row

        # run across all tickers, summing series
        output_dictionary = None
        timing_rows = []

        for i, ticker in enumerate(self._ticker_list, 1):
            holdings, tstats = simulation(stock=ticker, strategy_name=self._strat)
            timing_rows.append(tstats)

            if output_dictionary is None:
                output_dictionary = holdings
            else:
                # sum per-date
                for key in holdings.keys():
                    output_dictionary[key]["Cash"] += holdings[key]["Cash"]
                    output_dictionary[key]["Holdings"] += holdings[key]["Holdings"]
                    output_dictionary[key]["Total Assets"] += holdings[key]["Total Assets"]

            if i % 50 == 0:
                print(f"[{self._strat}] processed {i}/{len(self._ticker_list)} tickers")

        # build portfolio dataframe (sorted by date)
        dates_sorted = sorted(output_dictionary.keys())
        return_dataset = {"Date": [], "Cash": [], "Holdings": [], "Total Assets": []}
        for dt in dates_sorted:
            return_dataset["Date"].append(dt)
            return_dataset["Cash"].append(output_dictionary[dt]["Cash"])
            return_dataset["Holdings"].append(output_dictionary[dt]["Holdings"])
            return_dataset["Total Assets"].append(output_dictionary[dt]["Total Assets"])

        timing_df = pd.DataFrame(timing_rows)
        return return_dataset, timing_df


if __name__ == "__main__":
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)

    strat_summaries = []

    strats = list(Config.STRATEGY_MAP.keys())   # e.g., ['Benchmark','MA_20_50','VolBreak','MACD','RSI_14']
    for strat in strats:
        sim = Simulation(strat)
        result, timing_df = sim.run()

        # write per-ticker timing
        timing_path = out_dir / f"{strat}_timing.csv"
        timing_df.to_csv(timing_path, index=False)

        # portfolio series (+$1,000,000 baseline) and PnL
        df = pd.DataFrame.from_dict(result)
        df = df.sort_values("Date").reset_index(drop=True)
        df["Cash"] += 1_000_000
        df["Total Assets"] += 1_000_000
        df["PnL"] = df["Total Assets"] - df["Total Assets"].iloc[0]
        df.to_csv(out_dir / f"{strat}.csv", index=False)

        # aggregate timing for summary
        agg = timing_df[["load_s", "signal_s", "sim_s", "total_s"]].sum().to_dict()
        agg.update({
            "strategy": strat,
            "tickers": int(timing_df.shape[0]),
            "rows_total": int(timing_df["rows"].sum()),
            "trades_total": int(timing_df["trades"].sum()),
        })
        strat_summaries.append(agg)

    # cross-strategy timing summary
    summary_df = (
        pd.DataFrame(strat_summaries)
          .set_index("strategy")[["tickers","rows_total","trades_total","load_s","signal_s","sim_s","total_s"]]
          .sort_values("total_s", ascending=False)
    )
    summary_df.to_csv(out_dir / "timing_summary.csv")
    print("\nTiming summary (seconds):")
    print(summary_df.round(3))
