import xlrd
from .screening_filter import ScreeningFilter, StockRecord

class BasicMarketFilter(ScreeningFilter):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]

    def __init__(self, market: list[str] = None, min_cap: int = None):
        super().__init__("basic_market_filter")
        self.market = market
        self.min_cap = min_cap

    def apply(self, record: StockRecord) -> bool:
        return record.market in self.TARGET_MARKETS

