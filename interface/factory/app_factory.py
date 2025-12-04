from application.screening_usecase import ScreeningUseCase
from application.backtest_usecase import BacktestUseCase

from infrastructure.jpx.jpx_stock_repository import JPXStockRepository
from domain.service.screening.screen_builder import ScreenBuilder
from domain.service.screening.screen_executor import ScreenExecutor
from domain.service.trigger_generator import TriggerGenerator
from domain.service.strategy_simulator import StrategySimulator
from domain.service.metrics_calculator import MetricsCalculator


# Screening 用 DI 構築
def create_screening_usecase() -> ScreeningUseCase:
    repo = JPXStockRepository()
    builder = ScreenBuilder()
    executor = ScreenExecutor()

    return ScreeningUseCase(
        stock_repo=repo,
        screen_builder=builder,
        screen_executor=executor
    )


# Backtest 用 DI 構築
def create_backtest_usecase() -> BacktestUseCase:
    repo = JPXStockRepository()
    builder = ScreenBuilder()
    trigger = TriggerGenerator()
    strategy = StrategySimulator()
    metrics = MetricsCalculator()

    return BacktestUseCase(
        stock_repo=repo,
        screen_builder=builder,
        trigger_gen=trigger,
        strategy_sim=strategy,
        metrics_calc=metrics,
    )

