from abc import ABC, abstractmethod
from domain.repository.chart_repository import ChartRepository
from datetime import datetime, timedelta
import xlrd

class StockRecord:
    def __init__(self, row: list[xlrd.sheet.Cell]):
        self.rawdata = row
        self.symbol = str(row[1].value).split(".")[0] + ".T"  # 銘柄コード
        self.name = row[2].value  # 銘柄名
        self.market = row[3].value  # 市場

        self.values = {}

        self.yf_daily = None  # キャッシュ用
        self.yf_yearly = None  # キャッシュ用

        self.repo = ChartRepository()
        self._memory_cache = None
        self._memory_range = None

        self._memory_cache_days = None
        self._memory_days = -1

    def get_values(self):
        return {
            "symbol": self.symbol, 
            "name": self.name,
            "market": self.market,
            "close": self.yf_daily["close"].iloc[-1] if self.yf_daily is not None and not self.yf_daily.empty else None,
            "rsi": self.values.get("rsi"),
            **self.values
        }
    
    def get_daily_chart_by_days(self, days):
        # 期間範囲ならメモリから返す
        if self._memory_days >= days:
            return self._memory_cache_days[-days:]

        # Repositoryから取得（キャッシュ or Yahoo ）
        today = datetime.today()
        approx_days = days * 2  # 休日を考慮したバッファ

        from_date = today - timedelta(days=approx_days)
        df = self.repo.load_daily_range(self.symbol, from_date, today)

        # 完全一致キャッシュを更新
        self._memory_cache_days = df
        self._memory_days = len(df)

        return self._memory_cache_days

    def get_daily_chart(self, from_date, to_date):
        # 期間完全一致ならメモリから返す
        if self._memory_range == (from_date, to_date):
            return self._memory_cache

        # Repositoryから取得（キャッシュ or Yahoo ）
        df = self.repo.load_daily_range(self.symbol, from_date, to_date)

        # 完全一致キャッシュを更新
        self._memory_cache = df
        self._memory_range = (from_date, to_date)

        return df

    def recent_yf_monthly(self):
        if self.yf_daily is not None:
            return self.yf_daily

        start = datetime.today() - timedelta(days=31*2)
        self.yf_daily = self.repo.load_daily_by_month(self.symbol, start)

        return self.yf_daily

    def recent_yf_yearly(self, days=366):
        if self.yf_yearly is not None and len(self.yf_yearly) >= days:
            return self.yf_yearly[-days:]

        start = datetime.today() - timedelta(days=days)
        self.yf_yearly = self.repo.load_daily_range(self.symbol, start, datetime.today())
        return self.yf_yearly[-days:]


