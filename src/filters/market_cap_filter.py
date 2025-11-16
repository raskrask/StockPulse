from .screening_filter import ScreeningFilter
from data.yf_fetcher import fetch_yf_info

class MarketCapFilter(ScreeningFilter):

    def __init__(self, cap: list[int]):
        self.min_cap = cap[0]
        self.max_cap = cap[1]

    def apply(self, sheet, candidates: list[int]) -> list[int]:
        rows = []
        for row_idx in candidates:
            symbol = str(sheet.cell_value(row_idx, 1)).split(".")[0]+".T"  # 銘柄コード
            info = fetch_yf_info(symbol)
            if info['marketCap'] >= self.min_cap and info['marketCap'] <= self.max_cap:
                rows.append(row_idx)
        return rows