"""
fetcher.py
Yahoo Finance + S3/ローカルキャッシュを使ったデータ取得モジュール
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

import infrastructure.util.io_utils as io_util


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
    filename = f"{symbol}/info/{month}.json"
    if io_util.exists_file(filename):
        return io_util.load_json(filename)

    ticker = yf.Ticker(symbol)
    info = ticker.info
    io_util.save_json(filename, info)
    return info


# ------------------------------------------------------------
# get_calendar
# ------------------------------------------------------------
def fetch_yf_calendar(symbol: str) -> dict:
    """
    銘柄情報を取得
    """
    month = datetime.today().strftime("%Y%m")
    filename = f"{symbol}/calendar/{month}.json"
    if io_util.exists_file(filename):
        return io_util.load_json(filename)

    ticker = yf.Ticker(symbol)
    calendar = ticker.get_calendar()
    #save_json(filename, calendar)

    return calendar


# ------------------------------------------------------------
# get_earnings_dates
# ------------------------------------------------------------
def fetch_yf_earnings(symbol: str) -> dict:
    """
    銘柄情報を取得
    """
    month = datetime.today().strftime("%Y%m")
    filename = f"{symbol}/earnings/{month}.parquet"
    if io_util.exists_file(filename):
        return io_util.load_parquet(filename)

    try:
        ticker = yf.Ticker(symbol)
        earnings = ticker.get_earnings_dates(limit=60)
        earnings = earnings.reset_index().rename(columns={"Earnings Date": "date"})
        io_util.save_parquet(earnings, filename)
    except Exception:
        earnings = pd.DataFrame()
    return earnings


# ------------------------------------------------------------
# 日足
# ------------------------------------------------------------
def fetch_yf_daily_by_month(symbol: str, month: datetime) -> pd.DataFrame:
    start_of_month = month.replace(day=1)
    month_end = (month + pd.offsets.MonthEnd(1)).date()
    df_yahoo = yf.download(
        symbol,
        start=start_of_month,
        end=month_end + timedelta(days=1),
        progress=False,
        auto_adjust=True,
    )
    if not df_yahoo.empty:
        df_yahoo = _normalize_yf(df_yahoo)
    return df_yahoo

def fetch_yf_daily_OLD(
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
        path = io_util.get_daily_month_cache_path(symbol, month)
        df_cached = io_util.load_parquet(path)
        if df_cached is None:
            dfs = None
            break
        dfs.append(df_cached)

    if dfs:
        start_of_month = end.replace(day=1)
        path = io_util.get_daily_recently_cache_path(symbol, end)
        df_cached = None
        if recently_cached: 
            df_cached = io_util.load_parquet(path)

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
                io_util.save_parquet(path, df_yahoo)

        df = pd.concat(dfs, ignore_index=True)
        df = df.drop_duplicates(subset="date").sort_values("date")
        return df

    # # 初回フル取得
    # df_yahoo = yf.download(
    #     symbol,
    #     start=start,
    #     end=end + timedelta(days=1),
    #     progress=False,
    #     auto_adjust=True,
    # )
    # if df_yahoo.empty:
    #     return pd.DataFrame()

    # df_yahoo = _normalize_yf(df_yahoo)

    start = start.date() if isinstance(start, datetime) else start
    end   = end.date() if isinstance(end, datetime) else end

    monthly_ranges = pd.date_range(start=start, end=end, freq="MS")
    df_all = pd.DataFrame()

    for month_start in monthly_ranges:
        month_start_date = month_start.date()
        month_end = (month_start + pd.offsets.MonthEnd(1)).date()

        # 月内の実データ取得範囲
        s = max(start, month_start_date)
        e = min(end, month_end)

        if s > e:
            continue

        df_yahoo = yf.download(
            symbol,
            start=s,
            end=e + timedelta(days=1),
            progress=False,
            auto_adjust=True,
        )
        if df_yahoo.empty:
            continue

        path = io_util.get_daily_month_cache_path(symbol, df_yahoo["date"].iloc[0])
        io_util.save_parquet(path, df_yahoo)

        df_yahoo = _normalize_yf(df_yahoo)
        df_all = pd.concat([df_all, df_yahoo], ignore_index=True)

    # 先月まで保存
    last_month = end.replace(day=1) - timedelta(days=1)
    last_month = pd.Timestamp(last_month)
    df_past = df_yahoo[df_yahoo["date"] <= last_month]

    for ym, df_month in df_past.groupby(df_past["date"].dt.to_period("M")):
        path = io_util.get_daily_month_cache_path(symbol, df_month["date"].iloc[0])
        io_util.save_parquet(path, df_month)

    return df_all


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
    path = io_util.get_weekly_cache_path(symbol)
    df_cached = io_util.load_parquet(path)

    df_daily = fetch_yf_daily_OLD(symbol, start, end)
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
        io_util.save_parquet(path, df_past)
        return df_weekly

    # 2回目以降 → キャッシュを先週まで更新
    df_past = df_weekly[df_weekly["date"] <= last_friday]
    io_util.save_parquet(path, df_past)

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
    path = io_util.get_monthly_cache_path(symbol)
    df_cached = io_util.load_parquet(path)

    df_daily = fetch_yf_daily_OLD(symbol, start, end)
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
        io_util.save_parquet(path, df_past)
        return df_monthly

    df_past = df_monthly[df_monthly["date"] <= last_month]
    io_util.save_parquet(path, df_past)

    return df_monthly
