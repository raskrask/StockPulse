from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord

class AvgTradingValueIndicator(BaseIndicator):
    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, record: StockRecord) -> bool:
        df = record.recent_yf_monthly()
        if df is None or df.empty:   
            return False
        trading_value = ((df['close'] * df['volume']).rolling(20).mean()).iloc[-1]
        record.values[self.key] = [trading_value, self.min_value, self.max_value]

        return self.min_value <= trading_value <= self.max_value

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        df = record.get_daily_chart_by_days(days+20)
        if df is None or df.empty:
            return False
        trading_value = ((df['close'] * df['volume']).rolling(20).mean())
        flags = trading_value.between(self.min_value, self.max_value)

        return flags[-days:]