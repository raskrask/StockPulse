from .screening_filter import ScreeningFilter , StockRecord
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import talib

class SmaFilter(ScreeningFilter):

    def __init__(self, key, value: list[int], period1: int, period2: int = None):
        """ SMAフィルター SMAtoSMA比率またはSMAto現在値比率 """
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]
        self.period1 = period1
        self.period2 = period2

    def apply(self, record: StockRecord) -> bool:

        df = record.recent_yf_yearly()
        if df.empty:
            return False

        sma1 = talib.SMA(df["close"].astype(float).values, timeperiod=self.period1)[-1]
        if self.period2:
            sma2 = talib.SMA(df["close"].astype(float).values, timeperiod=self.period2)[-1]
        else:
            sma2 = df["close"].iloc[-1]
        ratio = (sma1 - sma2) / sma2 * 100

        record.values[self.key] = [ratio, sma1, sma2, self.min_value, self.max_value]

        return self.min_value <= ratio <= self.max_value
