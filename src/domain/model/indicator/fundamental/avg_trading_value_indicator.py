from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord

class AvgTradingValueIndicator(BaseIndicator):
    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]
        self.window = 20  # 20日移動平均

    def screen_now(self, record: StockRecord) -> bool:
        values = self._screen_range_with_cache(record, self.window)
        trading_value = values[-1]
        record.values[self.key] = [trading_value, self.min_value, self.max_value]

        return self.min_value <= trading_value <= self.max_value

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        values = self._screen_range_with_cache(record, days)
        return [self.min_value <= v <= self.max_value for v in values]

    def calc_series(self, record: StockRecord, days):
        df = record.get_daily_chart_by_days(days + self.window)
        if df is None or df.empty:
            return []
        trading_value = ((df['close'] * df['volume']).rolling(self.window).mean())
        return trading_value.tolist()[-days:]
