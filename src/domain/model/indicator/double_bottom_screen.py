
from domain.model.analysis.technical.double_bottom_indicator import DoubleBottomIndicator
from domain.model.base_screen import BaseScreen
from domain.model.screen_record import  ScreenRecord

class DoubleBottomScreen(BaseScreen):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        signal = DoubleBottomIndicator.compute_double_bottom_signal(df)
        record.values[self.key] = signal

        return signal["signal"]

    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        if not self.is_active:
            return [True] * days

        df = record.recent_yf_yearly(days+26+5) # 追加の期間を確保
        result = []
        for i in range(days):
            sub_df = df.iloc[i:i+26+5]
            signal = DoubleBottomIndicator.compute_double_bottom_signal(sub_df)
            result.append(signal["signal"])

        return result