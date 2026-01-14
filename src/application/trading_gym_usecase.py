import random
import pandas as pd

from domain.repository.stock_repository import StockRepository
from domain.model.trading_gym.trading_gym_models import (
    LOOKBACK_DAYS,
    WINDOW_DAYS,
    MAX_ROUNDS,
    TradingGymRoundData,
)
from domain.service.trading_gym.trading_gym_service import TradingGymService


class TradingGymUsecase:
    def __init__(self, stock_repo: StockRepository | None = None, service: TradingGymService | None = None):
        self.stock_repo = stock_repo or StockRepository()
        self.service = service or TradingGymService()

    def get_universe(self):
        return self.stock_repo.list_all_stocks()

    def load_daily(self, record) -> pd.DataFrame:
        """
        必須カラム:
          index: DatetimeIndex
          open, high, low, close, volume
        """
        df = record.get_daily_chart_by_days(365 * 3)

        # ===== 日付を datetime に =====
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # ===== 移動平均 =====
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma25"] = df["close"].rolling(25).mean()
        df["ma75"] = df["close"].rolling(75).mean()

        return df

    def generate_question(self, universe) -> dict:
        min_length = LOOKBACK_DAYS + (WINDOW_DAYS * MAX_ROUNDS) + 1

        while True:
            stock = random.choice(universe)
            df = self.load_daily(stock)

            if len(df) < min_length:
                continue

            max_start = len(df) - (WINDOW_DAYS * MAX_ROUNDS) - 1
            idx = random.randint(LOOKBACK_DAYS, max_start)

            return {
                "symbol": stock.symbol,
                "name": stock.name,
                "df": df,
                "idx": idx,
                "date": df["date"].iloc[idx],
            }

    def get_round_data(self, df: pd.DataFrame, base_idx: int, round_index: int) -> TradingGymRoundData:
        entry_idx = base_idx + WINDOW_DAYS * (round_index - 1)
        entry_price = df.iloc[entry_idx]["close"]
        entry_date = df["date"].iloc[entry_idx]
        future = df.iloc[entry_idx + 1: entry_idx + WINDOW_DAYS + 1]

        max_ret = (future["close"].max() - entry_price) / entry_price
        min_ret = (future["close"].min() - entry_price) / entry_price
        base_score = max_ret if max_ret > abs(min_ret) else min_ret
        base_score = round(base_score * 100, 2)
        multiplier = round_index
        bonus_score = round(base_score * multiplier, 2)

        return TradingGymRoundData(
            entry_idx=entry_idx,
            entry_date=entry_date,
            entry_price=entry_price,
            future=future,
            max_ret=max_ret,
            min_ret=min_ret,
            base_score=base_score,
            multiplier=multiplier,
            bonus_score=bonus_score,
        )

    def get_window(self, df: pd.DataFrame, base_idx: int, entry_idx: int, show_result: bool) -> pd.DataFrame:
        start_idx = max(base_idx - LOOKBACK_DAYS, 0)
        end_idx = entry_idx + (WINDOW_DAYS if show_result else 0)
        return df.iloc[start_idx:end_idx + 1]

    def apply_action(self, *args, **kwargs):
        return self.service.apply_action(*args, **kwargs)

    def advance_round(self, state, universe):
        return self.service.advance_round(state, self.generate_question, universe)

    def next_question(self, state, universe):
        return self.service.next_question(state, self.generate_question, universe)
