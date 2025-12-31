from datetime import datetime
from pathlib import Path

import pandas as pd

import infrastructure.util.io_utils as io_utils


def _base_dir() -> Path:
    return Path(io_utils.BASE_DIR) / "backtest_results"


def _summary_path(profile_name: str) -> str:
    return f"backtest_results/{profile_name}/summary.json"


def _strategy_path(profile_name: str) -> str:
    return f"backtest_results/{profile_name}/strategy.parquet"


def list_backtest_profiles() -> list[str]:
    base_dir = _base_dir()
    if not base_dir.exists():
        return []
    return sorted([p.name for p in base_dir.iterdir() if p.is_dir()])


def save_backtest_result(profile_name: str, results: dict):
    summary = {
        "profile": profile_name,
        "trades": results.get("trades"),
        "win_rate": results.get("win_rate"),
        "lose_rate": results.get("lose_rate"),
        "draw_rate": results.get("draw_rate"),
        "gross_profit": results.get("gross_profit"),
        "gross_loss": results.get("gross_loss"),
        "profit_factor": results.get("profit_factor"),
        "trade_term_avg": results.get("trade_term_avg"),
        "total_return": results.get("total_return"),
        "generated_at": datetime.utcnow().isoformat(),
    }
    io_utils.save_json(_summary_path(profile_name), summary)

    strategy = results.get("strategy") or []
    rows = []
    for s in strategy:
        buy = s.get("buy_signal", {})
        sell = s.get("sell_signal", {})
        rows.append({
            "symbol": s.get("symbol"),
            "name": s.get("name"),
            "result": sell.get("result"),
            "buy_date": buy.get("date"),
            "buy_close": buy.get("close"),
            "sell_date": sell.get("date"),
            "sell_close": sell.get("close"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["return_pct"] = (df["sell_close"] - df["buy_close"]) / df["buy_close"] * 100
    io_utils.save_parquet(_strategy_path(profile_name), df)


def load_backtest_summary(profile_name: str) -> dict | None:
    return io_utils.load_json(_summary_path(profile_name))


def load_backtest_strategy(profile_name: str) -> pd.DataFrame | None:
    return io_utils.load_parquet(_strategy_path(profile_name))
