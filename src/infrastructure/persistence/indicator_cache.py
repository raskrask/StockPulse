import hashlib
import json
from datetime import datetime
from pathlib import Path

import infrastructure.util.io_utils as io_utils


def get_indicator_cache_path(symbol: str, from_year: int, to_year: int) -> str:
    return f"{symbol}/backtest/indicators/batch/{from_year}_{to_year}.parquet"


def save_indicator_batch(symbol: str, df, from_year: int, to_year: int) -> str:
    path = get_indicator_cache_path(symbol, from_year, to_year)
    io_utils.save_parquet(path, df)
    return path


def load_indicator_batch(symbol: str, from_year: int, to_year: int):
    path = get_indicator_cache_path(symbol, from_year, to_year)
    return io_utils.load_parquet(path)


def save_indicator_cache_range(from_year: int, to_year: int):
    payload = {
        "from_year": from_year,
        "to_year": to_year,
        "generated_at": datetime.utcnow().isoformat(),
    }
    io_utils.save_json("indicator_cache_range.json", payload)


def load_indicator_cache_range() -> dict | None:
    return io_utils.load_json("indicator_cache_range.json")


def clear_indicator_cache() -> int:
    if io_utils.STORAGE_BACKEND.startswith("s3"):
        return 0

    base_dir = Path(io_utils.BASE_DIR)
    deleted = 0
    for path in base_dir.glob("*/backtest/indicators/batch/*.parquet"):
        if path.is_file():
            path.unlink()
            deleted += 1

    summary_path = base_dir / "indicator_cache_range.json"
    if summary_path.exists():
        summary_path.unlink()
        deleted += 1

    return deleted
