"""
fetcher.py
Yahoo Finance + S3/ローカルキャッシュを使ったデータ取得モジュール
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from .util.io_utils import (
    BASE_DIR,
    load_parquet,
    load_json,
    save_parquet,
    save_json,
    exists_file,
    get_daily_cache_path,
    get_weekly_cache_path,
    get_monthly_cache_path,
)


# ------------------------------------------------------------
# 共通: Yahooデータの整形
# ------------------------------------------------------------
def _normalize_yf(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns
        ]
    else:
        df.columns = [str(c).lower() for c in df.columns]

    if "date" not in df.columns and "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    if "date" not in df.columns and "Date" in df.columns:
        df = df.rename(columns={"Date": "date"})

    return df


# ------------------------------------------------------------
# get_info
# ------------------------------------------------------------
def fetch_yf_info(symbol: str) -> dict:
    """
    銘柄情報を取得
    """
    month = datetime.today().strftime("%Y%m")
    filename = f"{BASE_DIR}/{symbol}/info/{month}.json"
    if exists_file(filename):
        return load_json(filename)

    ticker = yf.Ticker(symbol)
    info = ticker.info
    save_json(info, filename)
    return info


# ------------------------------------------------------------
# get_calendar
# ------------------------------------------------------------
def fetch_yf_calendar(symbol: str) -> dict:
    """
    銘柄情報を取得
    """
    month = datetime.today().strftime("%Y%m")
    filename = f"{BASE_DIR}/{symbol}/calendar/{month}.json"
    if exists_file(filename):
        return load_json(filename)

    ticker = yf.Ticker(symbol)
    calendar = ticker.get_calendar()
    #save_json(calendar, filename)

    return calendar


# ------------------------------------------------------------
# get_earnings_dates
# ------------------------------------------------------------
def fetch_yf_earnings(symbol: str) -> dict:
    """
    銘柄情報を取得
    """
    month = datetime.today().strftime("%Y%m")
    filename = f"{BASE_DIR}/{symbol}/earnings/{month}.parquet"
    if exists_file(filename):
        return load_parquet(filename)

    try:
        ticker = yf.Ticker(symbol)
        earnings = ticker.get_earnings_dates(limit=60)
        earnings = earnings.reset_index().rename(columns={"Earnings Date": "date"})
        save_parquet(earnings, filename)
    except Exception:
        earnings = pd.DataFrame()
    return earnings


# ------------------------------------------------------------
# 日足
# ------------------------------------------------------------
def fetch_yf_daily(
    symbol: str, start: datetime, end: datetime | None = None, recently_cached: bool = True
) -> pd.DataFrame:
    """
    日足データを取得
    - 先月までのデータはキャッシュ利用
    - 今月分はYahooから取得（保存しない）
    - キャッシュが無ければフル取得し、先月までを保存
    """
    if end is None:
        end = datetime.today()

    dfs = []

    # 先月までのキャッシュをロード
    for month in pd.date_range(start=start, end=end, freq="ME"):
        if month.month == end.month and month.year == end.year:
            continue
        path = get_daily_cache_path(symbol, month, False)
        df_cached = load_parquet(path)
        if df_cached is None:
            dfs = None
            break
        dfs.append(df_cached)

    if dfs:
        start_of_month = end.replace(day=1)
        path = get_daily_cache_path(symbol, end, True)
        df_cached = None
        if recently_cached: 
            df_cached = load_parquet(path)

        if df_cached is not None:
            dfs.append(df_cached)
        else:
            # 今月分をYahooから取得
            df_yahoo = yf.download(
                symbol,
                start=start_of_month,
                end=end + timedelta(days=1),
                progress=False,
                auto_adjust=True,
            )
            if not df_yahoo.empty:
                df_yahoo = _normalize_yf(df_yahoo)
                dfs.append(df_yahoo)
                save_parquet(df_yahoo, path)

        df = pd.concat(dfs, ignore_index=True)
        df = df.drop_duplicates(subset="date").sort_values("date")
        return df

    # 初回フル取得
    df_yahoo = yf.download(
        symbol,
        start=start,
        end=end + timedelta(days=1),
        progress=False,
        auto_adjust=True,
    )
    if df_yahoo.empty:
        return pd.DataFrame()

    df_yahoo = _normalize_yf(df_yahoo)

    # 先月まで保存
    last_month = end.replace(day=1) - timedelta(days=1)
    df_past = df_yahoo[df_yahoo["date"] <= last_month]
    for ym, df_month in df_past.groupby(df_past["date"].dt.to_period("M")):
        path = get_daily_cache_path(symbol, df_month["date"].iloc[0])
        save_parquet(df_month, path)

    return df_yahoo


# ------------------------------------------------------------
# 週足
# ------------------------------------------------------------
def fetch_yf_weekly(
    symbol: str, start: datetime, end: datetime | None = None
) -> pd.DataFrame:
    """
    週足データを取得
    - キャッシュがあれば利用
    - 今週分は毎回Yahoo（日足から変換）、保存しない
    - 初回は先週まで保存
    """
    path = get_weekly_cache_path(symbol)
    df_cached = load_parquet(path)

    df_daily = fetch_yf_daily(symbol, start, end)
    if df_daily.empty:
        return pd.DataFrame()

    df_weekly = (
        df_daily.resample("W-FRI", on="date")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna()
        .reset_index()
    )

    last_friday = df_weekly["date"].max() - timedelta(days=7)

    if df_cached is None:
        # 初回保存 → 先週まで
        df_past = df_weekly[df_weekly["date"] <= last_friday]
        save_parquet(df_past, path)
        return df_weekly

    # 2回目以降 → キャッシュを先週まで更新
    df_past = df_weekly[df_weekly["date"] <= last_friday]
    save_parquet(df_past, path)

    return df_weekly


# ------------------------------------------------------------
# 月足
# ------------------------------------------------------------
def fetch_yf_monthly(
    symbol: str, start: datetime, end: datetime | None = None
) -> pd.DataFrame:
    """
    月足データを取得
    - キャッシュがあれば利用
    - 今月分は毎回Yahoo（日足から変換）、保存しない
    - 初回は先月まで保存
    """
    path = get_monthly_cache_path(symbol)
    df_cached = load_parquet(path)

    df_daily = fetch_yf_daily(symbol, start, end)
    if df_daily.empty:
        return pd.DataFrame()

    df_monthly = (
        df_daily.resample("ME", on="date")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna()
        .reset_index()
    )

    last_month = df_monthly["date"].max().replace(day=1) - timedelta(days=1)

    if df_cached is None:
        df_past = df_monthly[df_monthly["date"] <= last_month]
        save_parquet(df_past, path)
        return df_monthly

    df_past = df_monthly[df_monthly["date"] <= last_month]
    save_parquet(df_past, path)

    return df_monthly
