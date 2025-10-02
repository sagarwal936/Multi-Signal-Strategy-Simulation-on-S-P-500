# Simulation.py

import pandas as pd
from pathlib import Path
from MovingAverageStrategy import MovingAverageStrategy
from VolatilityBreakoutStrategy import VolatilityBreakoutStrategy
from MACDStrategy import MACDStrategy
from RSIStrategy import RSIStrategy
from data_generator import PriceLoader
from collections import defaultdict

class Simluation:
    """
    Run the simulation with a list of stocks and strats.
    Args: stock_list, (e.g. ['AAPL']); strat_list (e.g. ['MovingAverage'])
    """

    def __init__(self, strat: str, file_path="sp500_prices/", tickers="all"):
        # strategy
        self._strat=strat
        # file_path
        self._file_path=file_path
        # stock
        self._tickers=tickers
        # if stock == None, then:
        if self._tickers=="all":           
            folder = Path(self._file_path)
            self._ticker_list = [p.stem for p in folder.glob("*.parquet")]
            self._ticker_list.sort()
            self._loader=PriceLoader(tickers=self._ticker_list, data_dir=self._file_path)
        else:
            self._ticker_list=self._tickers


    def run(self):
        def simulation(stock: str, strategy_name: 'str', initial_cash=0):
            stock_loader = self._loader.load(stock)
            if strategy_name=="MovingAverageStrategy":
                x= MovingAverageStrategy(stock_loader)
                z = x.generate_signals()
                date_list = list(z.index)
            elif strategy_name=="VolatilityBreakoutStrategy":
                x= VolatilityBreakoutStrategy(stock_loader)
                z = x.generate_signals()
                date_list = list(z.index)
            elif strategy_name=="MACDStrategy":
                x= MACDStrategy(stock_loader)
                z = x.generate_signals()
                date_list = list(z.index)
            elif strategy_name=="RSIStrategy":
                x= RSIStrategy(stock_loader)
                z = x.generate_signals()
                date_list = list(z.index)
            gross_holdings = {val: defaultdict() for val in date_list} # {2001/01/01: {'Cash':500K, 'Holdings':700K, 'Total Assets':1.2M}}
            total_cash=defaultdict(float)
            total_holdings=defaultdict(float)
            total_assets=defaultdict(float)
            company_holdings=0 # {'MSFT':305}
            cash=initial_cash
            for key in date_list:
                adj_close=z.loc[key]['AdjClose']
                signal=int(z.loc[key]['signal'])
                cash -= adj_close*signal
                company_holdings += signal
                holdings = company_holdings*adj_close
                gross_holdings[key]['Cash']=cash
                gross_holdings[key]['Holdings']=holdings
                gross_holdings[key]['Total Assets']=cash+holdings
            return gross_holdings

        output_dictionary=None
        # TODO: Add 1M to the final cash and cash+holdings calc
        for ticker in self._ticker_list:
            if output_dictionary==None:
                output_dictionary=simulation(stock=ticker, strategy_name=self._strat)
                continue
            holdings=simulation(stock=ticker, strategy_name=self._strat)
            for key in holdings.keys():
                output_dictionary[key]['Cash']+=holdings[key]['Cash']
                output_dictionary[key]['Holdings']+=holdings[key]['Holdings']
                output_dictionary[key]['Total Assets']+=holdings[key]['Total Assets']
        
        return_dataset={'Date':[], 'Cash':[], 'Holdings':[], 'Total Assets':[]}
        for date in output_dictionary.keys():
            return_dataset['Date'].append(date)
            return_dataset['Cash'].append(output_dictionary[date]['Cash'])
            return_dataset['Holdings'].append(output_dictionary[date]['Holdings'])
            return_dataset['Total Assets'].append(output_dictionary[date]['Total Assets'])
        
        return return_dataset

if __name__ == "__main__":
    strats = ["MovingAverageStrategy", "VolatilityBreakoutStrategy", "MACDStrategy", "RSIStrategy"]
    for strat in strats:
        obj = Simluation("MovingAverageStrategy")
        obj.run()
        df=pd.DataFrame.from_dict(obj)
        df['Cash']+=1000000
        df['Total Assets']+=1000000
        df.to_csv(f'output/{strat}.csv', index=False)