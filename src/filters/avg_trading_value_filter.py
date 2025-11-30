import xlrd
from .screening_filter import ScreeningFilter, StockRecord
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import pandas as pd

class AvgTradingValueFilter(ScreeningFilter):
    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, record: StockRecord) -> bool:
        df = record.recent_yf_monthly()
        if df.empty:
            return False
        trading_value = (df['close'].rolling(20).mean() * df['volume'].rolling(20).mean()).iloc[-1]
        record.values[self.key] = [trading_value, self.min_value, self.max_value]

        return self.min_value <= trading_value <= self.max_value