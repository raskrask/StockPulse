import xlrd
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd

class ListedStockIndicator(BaseIndicator):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]
    US_MARKETS = ["NASDAQ", "NYSE", "NYSE American", "NYSE Arca", "BATS", "IEX", "US"]
    IGNORE_STOKS = ["9023.T"]

    def __init__(self, params: dict = {}, market: list[str] = []):
        super().__init__("listed_stock")
        self.stockNumbers = params.get('stockNumbers', '').strip().split(' ')
        self.target_market = params.get("target_market")
        self.market = market + self.TARGET_MARKETS

    def apply(self, record: StockRecord) -> bool:
        if self.stockNumbers and record.symbol not in self.stockNumbers:
            return False
        if record.symbol in self.IGNORE_STOKS:
            return False

        if self.target_market == "US":
            return record.market_type == "US"
        if record.market_type != "JP":
            return False
        return record.market in self.market

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        return [self.apply(record)] * days
