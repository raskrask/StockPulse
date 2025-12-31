from abc import ABC, abstractmethod
from domain.model.stock_record import  StockRecord
import datetime

# フィルターの共通インターフェース
class BaseIndicator(ABC):
    def __init__(self, key):
        self.key = key

    def screen_now(self, record: StockRecord) -> bool:
        result = self.screen_range(record, 1)
        return bool(result[-1]) if result else False

    @abstractmethod
    def calc_series(self, record: StockRecord, days) -> list:
        pass        

    @abstractmethod
    def screen_range(self, record: StockRecord, days) -> list[bool]:
        pass        

    def apply_batch(self, record: StockRecord) -> list:
        df = record.get_cached_daily_chart()
        if df is None or df.empty:
            return []
        return self.calc_series(record, len(df))

    def _screen_range_with_cache(self, record: StockRecord, days):
        df_cached = record.get_cached_daily_chart()
        if df_cached is not None and self.key in df_cached:
            values = df_cached[self.key].tolist()[-days:]
        else:
            values = self.calc_series(record, days)
            if df_cached is not None and len(df_cached) >= len(values):
                df_cached[self.key] = ([None] * (len(df_cached) - len(values))) + values
        return values
