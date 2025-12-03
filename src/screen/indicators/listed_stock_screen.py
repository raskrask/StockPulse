import xlrd
from screen.base_screen import BaseScreen
from screen.screen_record import  ScreenRecord

class ListedStockScreen(BaseScreen):
    TARGET_MARKETS = ["プライム（内国株式）", "スタンダード（内国株式）", "グロース（内国株式）"]

    def __init__(self, market: list[str] = []):
        super().__init__("listed_stock")
        self.market = market + self.TARGET_MARKETS

    def apply(self, record: ScreenRecord) -> bool:
        return record.market in self.market

    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        return [self.apply(record)] * days
