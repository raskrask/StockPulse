import xlrd
from .base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd

class ListedStockIndicator(BaseIndicator):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]

    def __init__(self, params: dict, market: list[str] = []):
        super().__init__("listed_stock")
        self.stockNumbers = params.get('stockNumbers', '').strip()
        self.market = market + self.TARGET_MARKETS

    def apply(self, record: StockRecord) -> bool:
        if self.stockNumbers and record.symbol not in self.stockNumbers:
            return False

        return record.market in self.market

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        if self._validate_firstTradeDate(record, days):
            return [False] * days

        return [self.apply(record)] * days
    
    def _validate_firstTradeDate(self, record: StockRecord, days):
        info = fetch_yf_info(record.symbol)
        if not info or 'firstTradeDateMilliseconds' not in info:
            return [False] * days
        firstTradeDate = pd.to_datetime(info['firstTradeDateMilliseconds'], unit="ms")
        today = pd.Timestamp.today()
        bdays_ago = today - pd.offsets.BDay(int(days*1.1)) # 営業日ベースで比較

        if firstTradeDate > bdays_ago:
            return [False] * days