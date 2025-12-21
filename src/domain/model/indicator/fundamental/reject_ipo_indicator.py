from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import StockRecord
import pandas as pd
from datetime import timedelta

class RejectIpoIndicator(BaseIndicator):

    def __init__(self, params: dict = {}):
        super().__init__("reject_ipo")

    def apply(self, record: StockRecord) -> bool:
        return not self._reject_ipo_stock(record)

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        result = self._reject_firstTradeDate(record, days)
        return [not result] * days

    def _reject_ipo_stock(self, record: StockRecord):
        '''新規公開銘柄については１年以上の取引履歴がないため対象外とする'''
        firstTradeDate = record.get_stock_first_trade_date()

        today = pd.Timestamp.today()
        years_ago = today - timedelta(260*2)

        if firstTradeDate is None or firstTradeDate > years_ago:
            return True
        return False

    def _reject_firstTradeDate(self, record: StockRecord, days):
        '''株式公開日が集計範囲に満たないため対象外とする'''
        firstTradeDate = record.get_stock_first_trade_date()

        today = pd.Timestamp.today()
        bdays_ago = today - pd.offsets.BDay(260+int(days*1.1)) # 営業日ベースで比較

        if firstTradeDate is None or firstTradeDate > bdays_ago:
            return True
        return False