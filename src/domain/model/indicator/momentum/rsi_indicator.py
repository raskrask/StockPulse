from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta
import pandas as pd
import talib

class RsiIndicator(BaseIndicator):

    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]

    def screen_now(self, record: StockRecord) -> bool:
        df = record.get_daily_chart_by_days(14*2)
        df.sort_index(inplace=True)
        target = datetime.today() - timedelta(days=14*2)
        period = len(df[df["date"] >= target]) # 休場日レコードを除いた期間

        df_calendar = pd.DataFrame({"date": pd.date_range(target.date(), datetime.today().date(), freq="D")})
        df_merged = df_calendar.merge(df[["date", "close"]], on="date", how="left")

        df_merged['close'] = df_merged['close'].ffill()  # 前日終値で埋める

        close = df_merged["close"].astype(float).values
        rsi = talib.RSI(close, timeperiod=14)[-1]
        record.values[self.key] = [rsi, self.min_value, self.max_value]

        return self.min_value <= rsi <= self.max_value

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        values = self._screen_range_with_cache(record, days)
        return [self.min_value <= v <= self.max_value for v in values]

    def calc_series(self, record: StockRecord, days):
        df = record.get_daily_chart_by_days(days + 14)
        if df.empty:
            return []
        close = df["close"].astype(float).values
        rsi = talib.RSI(close, timeperiod=14)
        return list(rsi)[-days:]
