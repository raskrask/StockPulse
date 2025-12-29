from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta
import numpy as np

class HighBreakoutIndicator(BaseIndicator):
    """
    高値ブレイクアウト判定
    bottom_max期間に、high_term日間の高値をブレイクアウトが存在せず
    break_term期間に、high_term日間の高値をブレイクアウトが発生
    """
    def __init__(self, key, value: list[int], high_term: int = 100,):
        super().__init__(key)
        self.break_term = value[0]
        self.bottom_term = value[1]
        self.is_active = self.bottom_term != -1
        self.high_term = high_term

    def screen_now(self, record: StockRecord) -> bool:
        if not self.is_active:
            return True

        df = record.get_daily_chart_by_days(self.high_term + 1)
        if df is None or df.empty:   
            return False

        highs = df["high"]
        past_max = highs.iloc[-(self.high_term + 1):-(self.bottom_term + 1)].max()
        if self.break_term == -1:
            bottom_max = highs.iloc[-(self.bottom_term + 1):].max()
            break_max = max(past_max, bottom_max) + 1
        elif self.break_term == self.bottom_term:
            bottom_max = -1
            break_max = highs.iloc[-(self.break_term + 1):].max()
        else:
            bottom_max = highs.iloc[-(self.bottom_term + 1):-(self.break_term + 1)].max()
            break_max = highs.iloc[-(self.break_term + 1):].max()

        record.values[self.key] = [break_max, past_max, bottom_max]

        return (break_max > past_max) and (past_max > bottom_max)


    def screen_range(self, record, days: int) -> list[bool]:
        if not self.is_active:
            return [True] * days
        values = self._screen_range_with_cache(record, days)
        return [bool(v) for v in values]

    def calc_series(self, record, days: int):
        if not self.is_active:
            return [True] * days
        df = record.get_daily_chart_by_days(days + self.high_term)
        if df is None or df.empty:
            return [False] * days
        highs = df["high"]
        past_max = highs.shift(self.bottom_term + 1).rolling(self.high_term - self.bottom_term + 1).max()
        if self.break_term == -1:
            bottom_max = highs.rolling(self.bottom_term + 1).max()
            flags = (past_max > bottom_max)
        elif self.break_term == self.bottom_term:
            break_max = highs.rolling(self.break_term + 1).max()
            flags = (break_max > past_max)
        else:
            bottom_max = highs.shift(self.break_term + 1).rolling(self.bottom_term - self.break_term + 1).max()
            break_max = highs.rolling(self.break_term + 1).max()
            flags = (break_max > past_max) & (past_max > bottom_max)
        return flags.iloc[-days:].fillna(False).to_list()
