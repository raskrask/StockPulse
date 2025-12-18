
from domain.model.analysis.technical.ueno_theory import UenoTheory
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord

class UenoTheoryIndicator(BaseIndicator):
    def __init__(self, key, is_active: bool):
        super().__init__(key)
        self.logic = UenoTheory()
        self.is_active = is_active

    def apply(self, record) -> bool:
        if not self.is_active:
            return True

        df = record.recent_yf_yearly()
        df = self.logic.add_ueno_theory_signal(df)

        record.values[self.key] = df[["is_high_volume", "ueno_theory_signal"]].iloc[-1]

        return df["ueno_theory_signal"].iloc[-1]

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        if not self.is_active:
            return [True] * days

        df = record.get_daily_chart_by_days(days+self.logic.window_size+10)
        df = self.logic.add_ueno_theory_signal(df)

        return df["ueno_theory_signal"].tolist()[-days:]