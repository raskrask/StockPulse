from domain.repository.stock_repository import StockRepository
from domain.service.screening.screen_builder import ScreenBuilder
from domain.service.screening.change_signal_detector import ChangeSignalDetector
from domain.service.progress.console_progress_reporter import ConsoleProgressReporter
from domain.service.daily_report.market_timer import MarketTimer
from infrastructure.persistence.screening_profile import ScreeningProfile
from datetime import datetime, timedelta

class DailyReportUsecase:
    def __init__(self):
        self.progress = ConsoleProgressReporter()
        self.stock_repo = StockRepository()
        self.profile_repo = ScreeningProfile()
        self.screen_builder = ScreenBuilder()
        self.market_timer = MarketTimer()
        self.change_signal_detector = ChangeSignalDetector(progress=self.progress)

    def generate_buy_signals(self, name=None) -> str:
        """買い時株レポートを生成する"""
        timer = MarketTimer()
        if not timer.should_run():
            print("Skip: not the right time or already executed.")
            return

        # ① 通知Screening条件を取得
        profiles = [self.profile_repo.load(p) for p in self.profile_repo.list_profiles()]
        profiles = [p for p in profiles if p["notify"]]
        if name is not None:
            profiles = [p for p in profiles if p["name"] == name]

        # ② repository から銘柄一覧を取得
        stocks = self.stock_repo.list_all_stocks()
        self.progress.report(0, text=f"Start screening...{len(stocks)} stocks")

        result = []
        for p in profiles:
            # ③ 買い時シグナルが変化した銘柄を抽出
            filters = self.screen_builder.build_indicators(p["filters"])
            triggers = self.change_signal_detector.run(stocks, filters)

            result.append({ "profile": p, "trigger": triggers })

        timer.mark_executed()
        return result
