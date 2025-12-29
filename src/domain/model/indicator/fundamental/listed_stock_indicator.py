import xlrd
from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
import pandas as pd

class ListedStockIndicator(BaseIndicator):
    JP_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]
    US_MARKETS = ["S&P 500", "NASDAQ", "NYSE", "NYSE American", "NYSE Arca", "BATS", "IEX", "US"]
    IGNORE_STOKS = ["9023.T"]

    def __init__(self, params: dict | None = None, market: list[str] | None = None):
        super().__init__("listed_stock")
        params = params or {}
        market = market or []
        self.stockNumbers = params.get("stockNumbers", "").strip().split()
        target_market = params.get("target_market", "ALL")
        target_market = [target_market] if isinstance(target_market, str) else target_market
        self.target_market = ["JP", "US"] if "ALL" in target_market else target_market
        self.market = list(market)
        if "JP" in self.target_market: self.market.extend(self.JP_MARKETS)
        if "US" in self.target_market: self.market.extend(self.US_MARKETS)

    def screen_now(self, record: StockRecord) -> bool:
        if len(self.stockNumbers) > 0 and record.symbol not in self.stockNumbers:
            return False
        if record.symbol in self.IGNORE_STOKS:
            return False
        if self._is_equity_like_security(record.name):
            return False

        if not record.market_type in self.target_market:
            return False

        return record.market in self.market

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        values = self._screen_range_with_cache(record, days)
        return [bool(v) for v in values]

    def calc_series(self, record: StockRecord, days):
        return [self.screen_now(record)] * days

    def _is_equity_like_security(self, name: str) -> bool:
        return (
            "社債型種類株式" in name
            or "優先株" in name
        )