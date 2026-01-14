import pandas as pd

from domain.model.trading_gym.trading_gym_models import (
    MAX_ROUNDS,
    TradingGymRoundData,
    TradingGymState,
)


class TradingGymService:
    def apply_action(
        self,
        state: TradingGymState,
        action: str,
        round_data: TradingGymRoundData,
        symbol: str,
        entry_date,
        entry_price: float,
    ) -> dict:
        state.score = round_data.bonus_score
        state.multiplier = round_data.multiplier
        state.gym_count += 1
        state.show_result = True
        state.action = action

        applied_score = state.score if action == "buy" else -state.score
        state.gym_score += applied_score

        log = self.build_log(
            state=state,
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
            round_data=round_data,
            decision=action,
            applied_score=applied_score,
        )
        state.gym_history.append(log)
        return log

    def build_log(
        self,
        state: TradingGymState,
        symbol: str,
        entry_date,
        entry_price: float,
        round_data: TradingGymRoundData,
        decision: str,
        applied_score: float,
    ) -> dict:
        return {
            "timestamp": pd.Timestamp.now(),
            "symbol": symbol,
            "date": entry_date,
            "round": state.current_round,
            "multiplier": round_data.multiplier,
            "decision": decision,
            "entry_price": entry_price,
            "max": round_data.future["close"].max(),
            "min": round_data.future["close"].min(),
            "max_return_20d": round_data.max_ret,
            "min_return_20d": round_data.min_ret,
            "score": applied_score,
            "base_score": round_data.base_score,
        }

    def advance_round(self, state: TradingGymState, generate_question, universe):
        if state.current_round < MAX_ROUNDS:
            state.current_round += 1
            state.show_result = False
        else:
            state.current_question = generate_question(universe)
            state.current_round = 1
            state.show_result = False

    def next_question(self, state: TradingGymState, generate_question, universe):
        state.current_question = generate_question(universe)
        state.current_round = 1
        state.show_result = False
