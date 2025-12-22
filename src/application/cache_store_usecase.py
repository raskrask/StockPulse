from domain.service.progress.console_progress_reporter import ConsoleProgressReporter
from domain.service.progress.progress_reporter import ProgressReporter, NullProgressReporter
from domain.repository.stock_repository import StockRepository
import pandas as pd

class CacheStoreUsecase:
    def __init__(self, progress: ProgressReporter = NullProgressReporter()):
        self.progress_reporter = progress
        self.stock_repo = StockRepository()

    def get_cache_stats(self) -> list:
        """
        キャッシュ統計情報を取得する
        """
        self.progress_reporter.report(0, text="Fetching cache stats...")

        # ① repository から銘柄一覧を取得
        stocks = self.stock_repo.list_all_stocks()

        chart_days = 260 * 3  # 3年分のチャートを取得
        full_charts = 0

        # ② キャッシュ統計情報の取得ロジックを実装
        for i, stock in enumerate(stocks):
            #if stock.symbol != '130A.T':
            #    continue

            self.progress_reporter.report((i+1)/len(stocks), text=f"Processing {stock.symbol}...")
            if self._is_cached_chart(stock, chart_days):
                full_charts += 1
        
        self.progress_reporter.report(1.0, text="Cache stats fetched.")
        return {
            "total_stocks": len(stocks),
            "stocks_with_full_charts": full_charts,
        }

    
    def _is_cached_chart(self, stock, chart_days) -> bool:
        first_trade_date = stock.get_stock_first_trade_date()

        all_chart = stock.get_daily_chart_by_days(chart_days)
        if all_chart.iloc[0]["date"] > first_trade_date:
            if len(all_chart) >= chart_days:
                return True
        else:
            gap_days = 10
            if all_chart.iloc[0]["date"] <= first_trade_date + pd.Timedelta(days=gap_days):
                return True

        return False