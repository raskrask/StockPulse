from abc import ABC, abstractmethod
import domain.repository.chart_repository as chart_repo
import domain.repository.stock_repository as stock_repo
import pandas as pd
from datetime import datetime, timedelta
import xlrd

class StockRecord:
    def __init__(self, row: list[xlrd.sheet.Cell], stock_repo, chart_repo):
        self.rawdata = row
        self.stock_repo = stock_repo
        self.chart_repo = chart_repo

        if isinstance(row, dict):
            self.symbol = row.get("symbol", "")
            self.name = row.get("name", "")
            self.market = row.get("market", "")
            self.market_type = "US"
        else:
            self.symbol = str(row[1].value).split(".")[0] + ".T"  # 銘柄コード
            self.name = row[2].value  # 銘柄名
            self.market = row[3].value  # 市場
            self.market_type = "JP"

        self.info = None  # 銘柄情報キャッシュ
        self.values = {}

        self._memory_cache = None
        self._memory_range = None

        self._memory_cache_days = None
        self._memory_days = -1
        self._memory_days_forced = False

    def get_values(self):
        return {
            "symbol": self.symbol, 
            "name": self.name,
            "market": self.market,
            "close": self._memory_cache["close"].iloc[-1] if self._memory_cache is not None and not self._memory_cache.empty else None,
            "rsi": self.values.get("rsi"),
            **self.values
        }

    # Yahoo Finance から銘柄情報を取得する
    def get_stock_info(self):
        if self.info is None:
            self.info = self.stock_repo.get_stock_info(self.symbol)
        return self.info

    def get_stock_market_cap(self):
        info = self.get_stock_info()
        if not info or 'marketCap' not in info:
            return None
        return info['marketCap']

    def get_industry(self):
        if self.market_type == "JP":
            return self.rawdata[7].value
        info = self.get_stock_info()
        return info.get("industry", "-") if info else "-"

    def get_scale(self):
        if self.market_type == "JP":
            return self.rawdata[9].value
        return "-"
    
    def get_stock_first_trade_date(self):
        info = self.get_stock_info()
        if not info or 'firstTradeDateMilliseconds' not in info:
            return None
        return pd.to_datetime(info['firstTradeDateMilliseconds'], unit="ms")

    # 日足チャートを指定営業日数分取得する
    def get_daily_chart_by_days(self, days):
        # 期間範囲ならメモリから返す
        if self._memory_cache_days is not None and self._memory_days_forced:
            return self._memory_cache_days[-days:]
        if self._memory_days >= days:
            return self._memory_cache_days[-days:]

        # Repositoryから取得（キャッシュ or Yahoo ）
        today = datetime.today()
        approx_days = max(days,31) * 1.5 # 休日を考慮したバッファ

        from_date = today - timedelta(days=approx_days)
        from_date = max(from_date, self.get_stock_first_trade_date())
        df = self.chart_repo.load_daily_range(self.symbol, from_date, today)

        # 完全一致キャッシュを更新
        self._memory_cache_days = df
        self._memory_days = len(df)

        return self._memory_cache_days[-days:]

    def get_daily_chart(self, from_date, to_date):
        # 期間完全一致ならメモリから返す
        if self._memory_range == (from_date, to_date):
            return self._memory_cache

        first_trade_date = self.get_stock_first_trade_date()
        if first_trade_date is not None:
            from_date = max(from_date, first_trade_date)

        # Repositoryから取得（キャッシュ or Yahoo ）
        df = self.chart_repo.load_daily_range(self.symbol, from_date, to_date)

        # 完全一致キャッシュを更新
        self._memory_cache = df
        self._memory_range = (from_date, to_date)

        return df

    def set_daily_chart_days_cache(self, df, force: bool = False):
        if df is None:
            self._memory_cache_days = None
            self._memory_days = -1
            self._memory_days_forced = False
            return
        self._memory_cache_days = df
        self._memory_days = len(df)
        self._memory_days_forced = force

    def get_cached_daily_chart(self):
        return self._memory_cache_days
