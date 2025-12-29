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


def load_cached_indicator_df(symbol: str):
    cache_range = load_indicator_cache_range()
    if not cache_range:
        return None
    df = load_indicator_batch(symbol, cache_range["from_year"], cache_range["to_year"])
    if df is None or df.empty:
        return None
    return df


def clear_indicator_cache(keep_from_year: int, keep_to_year: int):
    if io_utils.STORAGE_BACKEND.startswith("s3"):
        return

    base_dir = Path(io_utils.BASE_DIR)
    keep_name = f"{keep_from_year}_{keep_to_year}.parquet"
    for path in base_dir.glob("*/backtest/indicators/batch/*.parquet"):
        if path.is_file():
            if path.name == keep_name:
                continue
            path.unlink()
