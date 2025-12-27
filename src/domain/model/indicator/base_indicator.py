from abc import ABC, abstractmethod
from domain.model.stock_record import  StockRecord
import datetime

# フィルターの共通インターフェース
class BaseIndicator(ABC):
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def screen_now(self, record: StockRecord) -> bool:
        pass        

    @abstractmethod
    def screen_range(self, record: StockRecord, days) -> list[bool]:
        pass        

    def batch_apply_for_df(self, record: StockRecord, df) -> list[bool]:
        record.set_daily_chart_days_cache(df, force=True)
        #df = record.get_cached_daily_chart()
        if df is None or df.empty:
            return []
        return self.screen_range(record, len(df))
