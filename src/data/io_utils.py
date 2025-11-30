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
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(buffer)

def save_parquet(df: pd.DataFrame, path: str):
    """
    DataFrameをS3またはローカルに保存
    """
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        buffer = df.to_parquet(index=False)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_parquet(path, index=False)

def save_json(data: dict, path: str):
    """
    JsonデータをS3またはローカルに保存
    """
    json_str = json.dumps(data).encode("utf-8")
    if STORAGE_BACKEND.startswith("s3"):
        bucket, key = _split_s3_path(path)
        s3.put_object(Bucket=bucket, Key=key, Body=json_str)
    else:
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
            if os.path.exists(path):
                return json.load(open(path, "r"))
    except Exception:
        return None
    return None

# ---------- キャッシュ更新ロジック ----------
def get_daily_cache_path(symbol: str, date: datetime, recently_cached: bool = True) -> str:
    """
    日足キャッシュの保存先パスを返す（月単位）
    """
    ym = date.strftime("%Y-%m")
    if recently_cached:
        ym = date.strftime("%Y-%m-%d")
    return f"{BASE_DIR}/{symbol}/daily/{ym}.parquet"


def get_weekly_cache_path(symbol: str):
    return f"{BASE_DIR}/{symbol}/weekly.parquet"


def get_monthly_cache_path(symbol: str):
    return f"{BASE_DIR}/{symbol}/monthly.parquet"


# ---------- ヘルパー ----------
def _split_s3_path(path: str):
    assert path.startswith("s3://")
    no_scheme = path[5:]
    bucket, key = no_scheme.split("/", 1)
    return bucket, key
