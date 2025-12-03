from abc import ABC, abstractmethod
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
from .indicators import *

class ScreenFactory:
    @staticmethod
    def build_screens(config: dict) -> list:
        result = [ListedStockScreen()]

        Factory = {
            "marketCap": lambda key, v: MarketCapScreen(key, [x * 1_000_000 for x in v]),
            "avgTradingValue": lambda key, v: AvgTradingValueScreen(key, [x * 1_000 for x in v]),
            "rsi": lambda key, v: RsiScreen(key, v),
            "price_change_20d_ago": lambda key, v: PriceChangeScreen(key, v, 20),
            "sma_25_divergence":   lambda key, v: SmaScreen(key, v, 25),
            "sma_75_divergence":  lambda key, v: SmaScreen(key, v, 75),
            "sma_200_divergence": lambda key, v: SmaScreen(key, v, 200),
            "ytd_high_divergence": lambda key, v: YtdDivergenceScreen(key, v, "high"),
            "ytd_low_divergence": lambda key, v: YtdDivergenceScreen(key, v, "low"),
            "ichimoku_3yakukoten": lambda key, v: IchimokuScreen(key, v),
            "double_bottom_signal": lambda key, v: DoubleBottomScreen(key, v),
        }

        for key, builder in Factory.items():
            if key in config:
                result.append(builder(key, config[key]))

        return result