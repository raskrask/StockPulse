
from analysis.technical.double_bottom_indicator import DoubleBottomIndicator
from .screening_filter import ScreeningFilter, StockRecord

class DoubleBottomFilter(ScreeningFilter):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        df = DoubleBottomIndicator.add_double_bottom_signal(df)
        record.values[self.key] = df["double_bottom_signal"].iloc[-1]

        return record.values[self.key]
