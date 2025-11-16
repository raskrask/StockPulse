import xlrd
from .screening_filter import ScreeningFilter
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import pandas as pd

class AvgTradingValueFilter(ScreeningFilter):
    def __init__(self, value: list[int]):
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, sheet: xlrd.sheet.Sheet, candidates: list[int]) -> list[int]:
        rows = []
        start = datetime.today() - timedelta(days=20)
        for row_idx in candidates:
            symbol = str(sheet.cell_value(row_idx, 1)).split(".")[0]+".T"  # 銘柄コード

            df = fetch_yf_daily(symbol, start)
            trading_value = (df['close'].rolling(20).mean() * df['volume'].rolling(20).mean()).iloc[-1]
            if trading_value >= self.min_value and trading_value <= self.max_value:
                rows.append(row_idx)
        return rows