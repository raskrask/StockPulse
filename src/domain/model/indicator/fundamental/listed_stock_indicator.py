import xlrd
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd

class ListedStockIndicator(BaseIndicator):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]
    IGNORE_STOKS = ["9023.T"]

    def __init__(self, params: dict, market: list[str] = []):
        super().__init__("listed_stock")
        self.stockNumbers = params.get('stockNumbers', '').strip()
        self.market = market + self.TARGET_MARKETS

    def apply(self, record: StockRecord) -> bool:
        if self.stockNumbers and record.symbol not in self.stockNumbers:
            return False
        if record.symbol in self.IGNORE_STOKS:
            return False

        return record.market in self.market

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        return [self.apply(record)] * days
