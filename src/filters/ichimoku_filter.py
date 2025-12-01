
from analysis.technical.ichimoku_indicator import IchimokuIndicator
from .screening_filter import ScreeningFilter, StockRecord

class IchimokuFilter(ScreeningFilter):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        df = IchimokuIndicator.add_3yakukoten(df)
        record.values[self.key] = df["ichiyaku_3yakukoten"].iloc[-1]

        return record.values[self.key]
