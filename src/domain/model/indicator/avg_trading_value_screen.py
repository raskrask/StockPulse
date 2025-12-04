import xlrd
from domain.model.base_screen import BaseScreen
from domain.model.screen_record import  ScreenRecord
from infrastructure.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import pandas as pd

class AvgTradingValueScreen(BaseScreen):
    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, record: ScreenRecord) -> bool:
        df = record.recent_yf_monthly()
        if df.empty:
            return False
        trading_value = (df['close'].rolling(20).mean() * df['volume'].rolling(20).mean()).iloc[-1]
        record.values[self.key] = [trading_value, self.min_value, self.max_value]

        return self.min_value <= trading_value <= self.max_value

    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        df = record.recent_yf_yearly(days)
        if df.empty:
            return False
        trading_value = (df['close'].rolling(20).mean() * df['volume'].rolling(20).mean())
        flags = [self.min_value <= v <= self.max_value for v in trading_value]

        return flags