from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd
from datetime import timedelta

class RejectIpoIndicator(BaseIndicator):

    def __init__(self, params: dict):
        super().__init__("reject_ipo")

    def apply(self, record: StockRecord) -> bool:
        return self._reject_ipo_stock(record)

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        result = self._reject_firstTradeDate(record, days)
        return [result] * days

    def _get_first_trade_date(self, record: StockRecord):
        info = fetch_yf_info(record.symbol)
        if not info or 'firstTradeDateMilliseconds' not in info:
            return None
        return pd.to_datetime(info['firstTradeDateMilliseconds'], unit="ms")

    def _reject_ipo_stock(self, record: StockRecord):
        '''新規公開銘柄については１年以上の取引履歴がないため対象外とする'''
        firstTradeDate = self._get_first_trade_date(record)

        today = pd.Timestamp.today()
        years_ago = today - timedelta(260*2)

        if firstTradeDate is None or firstTradeDate > years_ago:
            return True

    def _reject_firstTradeDate(self, record: StockRecord, days):
        '''株式公開日が集計範囲に満たないため対象外とする'''
        firstTradeDate = self._get_first_trade_date(record)

        today = pd.Timestamp.today()
        bdays_ago = today - pd.offsets.BDay(260+int(days*1.1)) # 営業日ベースで比較

        if firstTradeDate is None or firstTradeDate > bdays_ago:
            return True