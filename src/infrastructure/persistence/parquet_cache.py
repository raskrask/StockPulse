import infrastructure.util.io_utils as io_utils
import pandas as pd

# 日足のキャッシュファイル有無
def exists_daily_by_month(symbol, month) -> bool:
    path = io_utils.get_daily_month_cache_path(symbol, month)
    return io_utils.exists_file(path)

# 日足のキャッシュをロード
def load_daily_by_month(symbol, month) -> list:
    path = io_utils.get_daily_month_cache_path(symbol, month)
    return io_utils.load_parquet(path)

# 日足のキャッシュを保存
def save_daily_by_month(symbol, month, df) -> list:
    if df.empty:
        return
    path = io_utils.get_daily_month_cache_path(symbol, month)
    io_utils.save_parquet(path, df)

def load_daily_month_between(symbol,from_date, to_date) -> list:
    results = []
    from_date = from_date.replace(day=1)
    monthly_ranges = pd.date_range(start=from_date, end=to_date, freq="MS")
    for ym in monthly_ranges:
        if exists_daily_by_month(symbol, ym):
            results.append(load_daily_by_month(symbol, ym))

    return results