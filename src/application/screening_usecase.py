
from domain.repository.stock_repository import StockRepository
from infrastructure.jpx.jpx_fetcher import JPXListingFetcher
from domain.service.screening.screen_builder import ScreenBuilder
from domain.service.screening.screen_executor import ScreenExecutor
from domain.service.progress.progress_reporter import ProgressReporter, NullProgressReporter
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta


class ScreeningUsecase:
    def __init__(self, progress: ProgressReporter = NullProgressReporter()):
        self.progress_reporter = progress
        self.stock_repo = StockRepository()
        self.screen_builder = ScreenBuilder()
        self.screen_executor = ScreenExecutor(progress=progress)

    def screen_stocks(self, params: dict) -> list:
        """
        指定されたフィルター条件に基づいて銘柄をスクリーニングする
        """
        start_time = datetime.now()

        # ① repository から銘柄一覧を取得
        stocks = self.stock_repo.list_all_stocks(params)
        self.progress_reporter.report(0, text=f"Start screening...{len(stocks)} stocks")

        # ② スクリーニング処理
        filters = self.screen_builder.build_indicators(params)
        screened_stocks = self.screen_executor.run(stocks, filters)
        self.progress_reporter.report(1.0, text=f"Screening completed. (time: {datetime.now() - start_time})")

        return [s.get_values() for s in screened_stocks]

