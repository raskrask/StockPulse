from .screening_filter import ScreeningFilter , StockRecord
from data.yf_fetcher import fetch_yf_info

class MarketCapFilter(ScreeningFilter):

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
