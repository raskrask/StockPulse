from .screening_filter import ScreeningFilter , StockRecord
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import numpy as np

class PriceChangeFilter(ScreeningFilter):
    """
    株価騰落率（N営業日前比）フィルター
    """

    def __init__(self, key, value_range: list[float], days: int):
        super().__init__(key)
        # UIからの [min%, max%] 例：[-5, 20]
        self.min_value = value_range[0]
        self.max_value = value_range[1]
        self.days = days

    def apply(self, record: StockRecord) -> bool:

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
