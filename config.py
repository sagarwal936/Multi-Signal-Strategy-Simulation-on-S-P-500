"""Centralized constants and default parameters for backtesting and strategies."""
from MovingAverageStrategy import MovingAverageStrategy
from VolatilityBreakoutStrategy import VolatilityBreakoutStrategy
from MACDStrategy import MACDStrategy
from RSIStrategy import RSIStrategy

class Config:

    STRATEGY_MAP = {
        "MovingAverageStrategy": MovingAverageStrategy,
        "VolatilityBreakoutStrategy": VolatilityBreakoutStrategy,
        "MACDStrategy": MACDStrategy,
        "RSIStrategy": RSIStrategy,
    }
    Close_Col = 'Close'