"""
io_utils.py
S3 / ローカルファイルを利用したキャッシュ入出力のユーティリティ
"""

import os
import pandas as pd
import json
from datetime import datetime
import boto3

STORAGE_BACKEND = os.getenv("STOCKPULSE_STORAGE", "local")
S3_BUCKET = os.getenv("STOCKPULSE_BUCKET", "stockpulse-cache")
S3_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
LOCAL_CACHE_DIR = os.getenv("STOCKPULSE_LOCAL_CACHE_DIR", "./cache")
BASE_DIR = f"s3://{S3_BUCKET}" if STORAGE_BACKEND.startswith("s3") else LOCAL_CACHE_DIR

s3 = boto3.client("s3", region_name=S3_REGION)


# ---------- 保存系 ----------
def save_contents(buffer: bytes, path: str):
    """
    バイト列をS3またはローカルに保存
    """
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer)
    else:
        path = os.path.join(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(buffer)

def save_parquet(path: str, df: pd.DataFrame):
    """
    DataFrameをS3またはローカルに保存
    """
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        buffer = df.to_parquet(index=False)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer)
    else:
        path = os.path.join(BASE_DIR, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_parquet(path, index=False)

def save_json(path: str, data: dict):
    """
    JsonデータをS3またはローカルに保存
    """
    for k, v in data.items():
        if isinstance(v, pd.Timestamp):
            data[k] = v.isoformat()     # "2025-12-02T09:30:00"

    json_str = json.dumps(data).encode("utf-8")
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        s3.put_object(Bucket=bucket, Key=key, Body=json_str)
    else:
        path = os.path.join(BASE_DIR, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))

# ---------- 読み込み系 ----------
def exists_file(path: str) -> bool:
    """
    S3またはローカルにファイルが存在するか
    """
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except s3.exceptions.ClientError:
            return False
    else:
        path = os.path.join(BASE_DIR, path)
        return os.path.exists(path)

def load_parquet(path: str) -> pd.DataFrame | None:
    """
    DataFrameをS3またはローカルから読み込み
    存在しない場合は None を返す
    """
    try:
        if STORAGE_BACKEND.startswith("s3"):
            bucket, key = _split_s3_path(path)
            obj = s3.get_object(Bucket=bucket, Key=key)
            return pd.read_parquet(obj["Body"])
        else:
            path = os.path.join(BASE_DIR, path)
            if os.path.exists(path):
                return pd.read_parquet(path)
    except Exception:
        return None
    return None


def load_json(path: str) -> dict | None:
    """
    JsonをS3またはローカルから読み込み
    存在しない場合は None を返す
    """
    try:
        if STORAGE_BACKEND.startswith("s3"):
            bucket, key = _split_s3_path(path)
            obj = s3.get_object(Bucket=bucket, Key=key)
            return json.load(obj["Body"])
        else:
            path = os.path.join(BASE_DIR, path)
            if os.path.exists(path):
                data = json.load(open(path, "r"))
                if 'date' in data:
                    #data['date'] = datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S")
                    data["date"] = datetime.fromisoformat(data["date"])

                return data

    except Exception:
        return None
    return None

# ---------- キャッシュ更新ロジック ----------
def get_daily_recently_cache_path(symbol: str, target_date: datetime) -> str:
    """
    日足キャッシュの保存先パスを返す
    """
    ymd = target_date.strftime("%Y-%m-%d")
    return f"{symbol}/daily/{ymd}.parquet"

def get_daily_month_cache_path(symbol: str, target_date: datetime) -> str:
    """
    日足キャッシュの保存先パスを返す（月単位）
    """
    today = datetime.today()
    current_month = (today.year == target_date.year) and (today.month == target_date.month)
    if current_month:
        return get_daily_recently_cache_path(symbol, today)
    else:
        ym = target_date.strftime("%Y-%m")
    return f"{symbol}/daily/{ym}.parquet"

def get_weekly_cache_path(symbol: str):
    return f"{symbol}/weekly.parquet"


def get_monthly_cache_path(symbol: str):
    return f"{symbol}/monthly.parquet"


def get_jpx_filename(_is_third_business_day_passed) -> str:

    target_day = datetime.today()

    # 第3営業日前なら前月
    if not _is_third_business_day_passed:
        target_day = target_day.replace(day=1) - datetime.timedelta(days=1)

    return os.path.join(
        BASE_DIR,
        'jpx_list',
        f"tse_list_{target_day.year}-{str(target_day.month).zfill(2)}.xls",
    )


# ---------- ヘルパー ----------
def _split_s3_path(path: str):
    assert path.startswith("s3://")
    no_scheme = path[5:]
    bucket, key = no_scheme.split("/", 1)
    return bucket, key
