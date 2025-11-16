"""
trend.py
EMAベース・傾きベースのトレンド判定ロジック
"""

import pandas as pd
import talib
import numpy as np
from sklearn.linear_model import LinearRegression


# ------------------------------------------------------------
# EMAを用いたトレンド判定
# ------------------------------------------------------------
def add_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameにEMAを追加して返す。
    必須カラム: ['close']
    """
    close = df["close"].astype(float).values

    df["ema20"] = talib.EMA(close, timeperiod=20)
    df["ema50"] = talib.EMA(close, timeperiod=50)
    df["ema200"] = talib.EMA(close, timeperiod=200)

    return df


def trend_status(row: pd.Series) -> str:
    """
    直近1行のデータからトレンド状態を返す。
    - ema20 > ema50 > ema200 → Bullish
    - ema20 < ema50 < ema200 → Bearish
    - それ以外 → Neutral
    """
    if pd.isna(row["ema20"]) or pd.isna(row["ema50"]) or pd.isna(row["ema200"]):
        return "Neutral"

    if row["ema20"] > row["ema50"] > row["ema200"]:
        return "Bullish"
    elif row["ema20"] < row["ema50"] < row["ema200"]:
        return "Bearish"
    else:
        return "Neutral"


# ------------------------------------------------------------
# 傾き（slope）を使った右肩上がり判定
# ------------------------------------------------------------
def trend_slope(series: pd.Series, lookback: int) -> float:
    """
    線形回帰で直近 lookback 本の傾きを計算する
    - >0 → 上昇傾向
    - <0 → 下落傾向
    """
    y = series[-lookback:].values.reshape(-1, 1)
    x = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    return model.coef_[0][0]


def is_upward(series: pd.Series, lookback: int, threshold: float = 0) -> bool:
    """
    傾きが threshold より大きければ「右肩上がり」と判定
    - lookback=13 → 13週（週足）
    - lookback=12 → 12ヶ月（月足）
    """
    slope = trend_slope(series, lookback)
    return slope > threshold

def is_downward(series: pd.Series, lookback: int, threshold: float = 0) -> bool:
    """
    傾きが threshold より小さければ「右肩下がり」と判定
    - lookback=13 → 13週（週足）
    - lookback=12 → 12ヶ月（月足）
    """
    slope = trend_slope(series, lookback)
    return slope < threshold
