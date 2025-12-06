from domain.repository.stock_repository import StockRepository

class DailyReportUsecase:
    def __init__(self):
        self.stock_repo = StockRepository()

    def generate_buy_signals(self) -> str:
        """買い時株レポートを生成する"""

        # ① repository から銘柄一覧を取得（domain/repository）
        stocks = self.stock_repo.list_all_stocks()
        return "report"