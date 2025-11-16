from .screening_filter import ScreeningFilter
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import talib

class RsiFilter(ScreeningFilter):

    def __init__(self, value: list[int]):
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, sheet, candidates: list[int]) -> list[int]:
        rows = []
        start = datetime.today() - timedelta(days=30)
        for row_idx in candidates:
            symbol = str(sheet.cell_value(row_idx, 1)).split(".")[0]+".T"  # 銘柄コード
            df = fetch_yf_daily(symbol, start)
            close = df["close"].astype(float).values
            rsi = talib.RSI(close, timeperiod=14)[-1]
            if rsi >= self.min_value and rsi <= self.max_value:
                rows.append(row_idx)

        return rows