from abc import ABC, abstractmethod
from infrastructure.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
from .screen_record import  ScreenRecord
import xlrd

# フィルターの共通インターフェース
class BaseScreen(ABC):
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def apply(self, record: ScreenRecord) -> bool:
        pass        

    @abstractmethod
    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        pass        

