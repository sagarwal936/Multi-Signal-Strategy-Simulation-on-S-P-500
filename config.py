"""Centralized constants and default parameters for backtesting and strategies."""

from BenchmarkStrategy import BenchmarkStrategy
from MovingAverageStrategy import MovingAverageStrategy
from VolatilityBreakoutStrategy import VolatilityBreakoutStrategy
from MACDStrategy import MACDStrategy
from RSIStrategy import RSIStrategy
from constants import Close_Col

class Config:

    STRATEGY_MAP = {
        "BenchmarkStrategy": BenchmarkStrategy,
        "MovingAverageStrategy": MovingAverageStrategy,
        "VolatilityBreakoutStrategy": VolatilityBreakoutStrategy,
        "MACDStrategy": MACDStrategy,
        "RSIStrategy": RSIStrategy,
    }
    Close_Col = Close_Col