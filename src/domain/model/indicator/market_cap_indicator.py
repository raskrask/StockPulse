from .base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd

class MarketCapIndicator(BaseIndicator):

    def __init__(self, key, cap: list[int]):
        super().__init__(key)
        self.min_cap = cap[0]
        self.max_cap = cap[1]

    def apply(self, record: StockRecord) -> bool:
        info = fetch_yf_info(record.symbol)
        if not info or 'marketCap' not in info:
            return False
        record.values[self.key] = info['marketCap']

        return self.min_cap <= info['marketCap'] <= self.max_cap

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        return [self.apply(record)] * days
