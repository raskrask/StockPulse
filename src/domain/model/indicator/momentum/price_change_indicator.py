from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta
import numpy as np

class PriceChangeIndicator(BaseIndicator):
    """
    株価騰落率（N営業日前比）フィルター
    """

    def __init__(self, key, value_range: list[float], days: int):
        super().__init__(key)
        # UIからの [min%, max%] 例：[-5, 20]
        self.min_value = value_range[0]
        self.max_value = value_range[1]
        self.days = days

    def screen_now(self, record: StockRecord) -> bool:
        df = record.recent_yf_yearly()
        if df.empty:
            return False
        df = df.sort_index()
        close = df["close"].astype(float).values

        # 現在値と N営業日前の終値
        past = close[-self.days-1]
        last = close[-1]    

        # 騰落率（%）
        # (現在値 - 過去値) / 過去値 × 100
        change = (last - past) / past * 100
        record.values[self.key] = [change, last, past, self.min_value, self.max_value   ]

        return self.min_value <= change <= self.max_value

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        values = self._screen_range_with_cache(record, days)
        return [self.min_value <= v <= self.max_value for v in values]

    def calc_series(self, record: StockRecord, days):
        df = record.get_daily_chart_by_days(days + self.days)
        if df.empty:
            return []
        df = df.sort_index()
        close = df["close"].astype(float).values
        past = df["close"].shift(self.days).astype(float).values
        change = (close - past) / past * 100
        return list(change)[-days:]
