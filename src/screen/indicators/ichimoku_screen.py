
from analysis.technical.ichimoku_indicator import IchimokuIndicator
from screen.base_screen import BaseScreen
from screen.screen_record import  ScreenRecord

class IchimokuScreen(BaseScreen):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        flags = self.batch_apply(record, days=52+10)
        record.values[self.key] = flags[-1]

        return flags[-1]

    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        if not self.is_active:
            return [True] * days

        df = record.recent_yf_yearly(days)
        df = IchimokuIndicator.add_3yakukoten(df)

        return df["ichiyaku_3yakukoten"].tolist()