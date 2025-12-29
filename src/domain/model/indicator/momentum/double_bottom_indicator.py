
from domain.model.analysis.technical.double_bottom import DoubleBottom
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord

class DoubleBottomIndicator(BaseIndicator):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def screen_now(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        signal = DoubleBottom.compute_double_bottom_signal(df)
        record.values[self.key] = signal

        return signal["signal"]

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        if not self.is_active:
            return [True] * days
        values = self._screen_range_with_cache(record, days)
        return [bool(v) for v in values]

    def calc_series(self, record: StockRecord, days):
        if not self.is_active:
            return [True] * days
        df = record.recent_yf_yearly(days+26+5) # 追加の期間を確保
        result = []
        for i in range(days):
            sub_df = df.iloc[i:i+26+5]
            signal = DoubleBottom.compute_double_bottom_signal(sub_df)
            result.append(signal["signal"])
        return result
