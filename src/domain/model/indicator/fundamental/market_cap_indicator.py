from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
import pandas as pd

class MarketCapIndicator(BaseIndicator):

    def __init__(self, key, cap: list[int]):
        super().__init__(key)
        self.min_cap = cap[0]
        self.max_cap = cap[1]

    def screen_now(self, record: StockRecord) -> bool:
        market_cap = record.get_stock_market_cap()

        if market_cap is None:
            return False

        return self.min_cap <= market_cap <= self.max_cap

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        return [self.screen_now(record)] * days
