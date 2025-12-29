
from domain.repository.stock_repository import StockRepository
from domain.service.screening.screen_builder import ScreenBuilder
from domain.service.backtest.trigger_generator import TriggerGenerator
from domain.service.backtest.strategy_simulator import StrategySimulator
from domain.service.backtest.backtest_evalutor import BacktestEvaluator
from domain.service.progress.progress_reporter import ProgressReporter, NullProgressReporter
from datetime import datetime, timedelta


class BacktestUsecase:
    def __init__(self, progress: ProgressReporter = NullProgressReporter(), use_cache=False):
        test_term = 2*365
        self.progress_reporter = progress
        self.use_cache = use_cache
        self.stock_repo = StockRepository()
        self.screen_builder = ScreenBuilder()
        self.trigger_generator = TriggerGenerator(test_term, use_cache=use_cache)
        self.strategy_simulator = StrategySimulator(test_term, use_cache=False)
        self.backtest_evaluator = BacktestEvaluator()

    def execute_backtest(self, params: dict) -> list:
        """
        指定されたフィルター条件に基づいて銘柄をバックテストする
        """
        start_time = datetime.now()

        # ① repository から銘柄一覧を取得（domain/repository）
        stocks = self.stock_repo.list_all_stocks(params)
        total = len(stocks)
        self.progress_reporter.report(0, text=f"Start backtest...{total} stocks")

        results = []
        filters = self.screen_builder.build_indicators(params)
        for i, record in enumerate(stocks):
            self.progress_reporter.report((i + 1) / total, text=f"Processing backtest {record.symbol}... ({i+1}/{total})")

            # ② 買い時トリガーを生成
            trigger = self.trigger_generator.run(record, filters)

            # ③ 取引戦略をシミュレーション
            results.append(self.strategy_simulator.run(record, trigger))

        # ④ バックテスト結果を評価
        metrics = self.backtest_evaluator.run(results, params=params)
        self.progress_reporter.report(1.0, text=f"Completed in {datetime.now() - start_time}")

        # 実行時間チェック
        for k, v in sorted(self.trigger_generator.timer_map.items(), key=lambda x: x[1], reverse=True):
            print(f"{k:20s} {v:.3f} sec")
        metrics["timer"] = { k: v for k, v in sorted(self.trigger_generator.timer_map.items(), key=lambda x: x[1], reverse=True) }
        
        return metrics
