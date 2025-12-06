from abc import ABC, abstractmethod
from domain.model.stock_record import  StockRecord
import datetime

# フィルターの共通インターフェース
class BaseIndicator(ABC):
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def apply(self, record: StockRecord) -> bool:
        pass        

    @abstractmethod
    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        pass        

