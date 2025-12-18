
from domain.model.analysis.technical.ichimoku_kintohyo import IchimokuKintohyo
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord

class IchimokuIndicator(BaseIndicator):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        df = IchimokuKintohyo.add_3yakukoten(df)

        record.values[self.key] = df["ichimoku_3yakukoten"].iloc[-1]

        return record.values[self.key]

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        if not self.is_active:
            return [True] * days

        df = record.get_daily_chart_by_days(days+52+10)
        df = IchimokuKintohyo.add_3yakukoten(df)

        return df["ichimoku_3yakukoten"].tolist()[-days:]