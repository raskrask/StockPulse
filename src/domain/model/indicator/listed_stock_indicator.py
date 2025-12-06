import xlrd
from .base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
from datetime import timedelta
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
        if self._reject_ipo_stock(record):
            return False

        return record.market in self.market

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        if self._reject_firstTradeDate(record, days):
            return [False] * days

        return [self.apply(record)] * days

    def _get_first_trade_date(self, record: StockRecord):
        info = fetch_yf_info(record.symbol)
        if not info or 'firstTradeDateMilliseconds' not in info:
            return None
        return pd.to_datetime(info['firstTradeDateMilliseconds'], unit="ms")

    def _reject_ipo_stock(self, record: StockRecord):
        '''新規公開銘柄については１年以上の取引履歴がないため対象外とする'''
        firstTradeDate = self._get_first_trade_date(record)

        today = pd.Timestamp.today()
        years_ago = today - timedelta(365)

        if firstTradeDate is None or firstTradeDate > years_ago:
            return True

    def _reject_firstTradeDate(self, record: StockRecord, days):
        '''株式公開日が集計範囲に満たないため対象外とする'''
        firstTradeDate = self._get_first_trade_date(record)

        today = pd.Timestamp.today()
        bdays_ago = today - pd.offsets.BDay(260+int(days*1.1)) # 営業日ベースで比較

        if firstTradeDate is None or firstTradeDate > bdays_ago:
            return True