from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta
import talib

class SmaIndicator(BaseIndicator):

    def __init__(self, key, value: list[int], period1: int, period2: int = None):
        """ SMAフィルター SMAtoSMA比率またはSMAto現在値比率 """
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]
        self.period1 = period1
        self.period2 = period2

    def screen_now(self, record: StockRecord) -> bool:

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

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        period = max(self.period1 or 0, self.period2 or 0)
        df = record.get_daily_chart_by_days(days + period)
        if df.empty:
            return False

        sma1 = talib.SMA(df["close"].astype(float).values, timeperiod=self.period1)
        if self.period2:
            sma2 = talib.SMA(df["close"].astype(float).values, timeperiod=self.period2)
        else:
            sma2 = df["close"].astype(float).values
        ratio = (sma1 - sma2) / sma2 * 100

        flags = [self.min_value <= v <= self.max_value for v in ratio]

        return flags[-days:]