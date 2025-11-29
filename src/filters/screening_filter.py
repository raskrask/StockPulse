from abc import ABC, abstractmethod
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import xlrd

class StockRecord:
    def __init__(self, jpx: list[xlrd.sheet.Cell]):
        self.jpx = jpx
        self.symbol = str(jpx[1].value).split(".")[0] + ".T"  # 銘柄コード
        self.name = jpx[2].value  # 銘柄名
        self.market = jpx[3].value  # 市場

        self.values = {}

        self.yf_daily = None  # キャッシュ用
        self.yf_yearly = None  # キャッシュ用
    
    def get_values(self):
        return {
            "symbol": self.symbol, 
            "name": self.name,
            "market": self.market,
            "close": self.yf_daily["close"].iloc[-1] if self.yf_daily is not None and not self.yf_daily.empty else None,
            "rsi": self.values.get("rsi"),
            **self.values
        }
    
    def recent_yf_monthly(self):
        if self.yf_daily is not None:
            return self.yf_daily

        start = datetime.today() - timedelta(days=32)
        self.yf_daily = fetch_yf_daily(self.symbol, start)
        return self.yf_daily

    def recent_yf_yearly(self):
        if self.yf_yearly is not None:
            return self.yf_yearly

        start = datetime.today() - timedelta(days=366)
        self.yf_yearly = fetch_yf_daily(self.symbol, start)
        return self.yf_yearly

# フィルターの共通インターフェース
class ScreeningFilter(ABC):
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def apply(self, record: StockRecord) -> bool:
        pass        

