import xlrd
from .screening_filter import ScreeningFilter

class BasicMarketFilter(ScreeningFilter):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]

    def __init__(self, market: list[str] = None, min_cap: int = None):
        self.market = market
        self.min_cap = min_cap

    def apply(self, sheet: xlrd.sheet.Sheet, candidates: list[int]) -> list[int]:
        rows = []
        for row_idx in candidates:
            market = sheet.cell_value(row_idx, 3)  # 市場
            if market in self.TARGET_MARKETS:
                rows.append(row_idx)
        return rows
