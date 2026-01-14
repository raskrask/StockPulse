from dataclasses import dataclass, field
import pandas as pd

LOOKBACK_DAYS = 60
WINDOW_DAYS = 20
MAX_ROUNDS = 5


@dataclass
class TradingGymState:
    gym_score: float = 0.0
    gym_count: int = 0
    gym_history: list = field(default_factory=list)
    current_question: dict | None = None
    show_result: bool = False
    current_round: int = 1
    score: float = 0.0
    multiplier: int = 1
    action: str | None = None

    def to_dict(self) -> dict:
        return {
            "gym_score": self.gym_score,
            "gym_count": self.gym_count,
            "gym_history": self.gym_history,
            "current_question": self.current_question,
            "show_result": self.show_result,
            "current_round": self.current_round,
            "score": self.score,
            "multiplier": self.multiplier,
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TradingGymState":
        return cls(
            gym_score=data.get("gym_score", 0.0),
            gym_count=data.get("gym_count", 0),
            gym_history=data.get("gym_history", []),
            current_question=data.get("current_question"),
            show_result=data.get("show_result", False),
            current_round=data.get("current_round", 1),
            score=data.get("score", 0.0),
            multiplier=data.get("multiplier", 1),
            action=data.get("action"),
        )


@dataclass
class TradingGymRoundData:
    entry_idx: int
    entry_date: pd.Timestamp
    entry_price: float
    future: pd.DataFrame
    max_ret: float
    min_ret: float
    base_score: float
    multiplier: int
    bonus_score: float
