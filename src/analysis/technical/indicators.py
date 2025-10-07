"""
indicators.py
一般的に利用されるテクニカル指標を計算する関数群

各関数は DataFrame に新しいカラムを追加して返す形式。
必須カラム: ['close'] （一部は 'high', 'low', 'volume' も利用）
"""

import pandas as pd
import talib


# ------------------------------------------------------------
# 移動平均線
# ------------------------------------------------------------
def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    移動平均線 (Moving Averages)
    - 短期・中期・長期のトレンドを滑らかに表現する
    - 代表的な使い方:
        * 20日線 … 短期トレンド
        * 50日線 … 中期トレンド
        * 200日線 … 長期トレンド
    - ゴールデンクロス/デッドクロスでトレンド転換を判断するのが一般的
    """
    close = df["close"].astype(float).values
    df["sma20"] = talib.SMA(close, timeperiod=20)
    df["sma50"] = talib.SMA(close, timeperiod=50)
    df["sma200"] = talib.SMA(close, timeperiod=200)
    return df


# ------------------------------------------------------------
# RSI
# ------------------------------------------------------------
def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    RSI (Relative Strength Index)
    - 一定期間の「上げ幅」と「下げ幅」の強さを比較するオシレーター
    - 値の範囲: 0〜100
        * 70以上 → 買われすぎ（調整の可能性）
        * 30以下 → 売られすぎ（反発の可能性）
    - 典型的には 14日RSI が利用される
    """
    close = df["close"].astype(float).values
    df[f"rsi{period}"] = talib.RSI(close, timeperiod=period)
    return df


# ------------------------------------------------------------
# MACD
# ------------------------------------------------------------
def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    MACD (Moving Average Convergence Divergence)
    - 短期EMAと長期EMAの差分を使ってトレンドの強さと転換を測る
    - 一般的な設定: EMA12, EMA26, Signal9
        * MACDライン > シグナルライン → 上昇トレンドの強まり
        * MACDライン < シグナルライン → 下落トレンドの強まり
    - ヒストグラム（macdhist）が正→強気、負→弱気と見る
    """
    close = df["close"].astype(float).values
    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    df["macd"] = macd
    df["macdsignal"] = macdsignal
    df["macdhist"] = macdhist
    return df


# ------------------------------------------------------------
# ボリンジャーバンド
# ------------------------------------------------------------
def add_bbands(df: pd.DataFrame, period: int = 20, nbdev: float = 2.0) -> pd.DataFrame:
    """
    ボリンジャーバンド (Bollinger Bands)
    - 移動平均線の上下に標準偏差のバンドを描き、価格の振れ幅を示す
    - 一般的な設定: 20日移動平均 ± 2σ
        * 上限バンドに接近 → 買われすぎ（反落 or 強い上昇トレンド）
        * 下限バンドに接近 → 売られすぎ（反発 or 強い下落トレンド）
    - バンドの幅が狭い（スクイーズ）ときは、その後のトレンド発生の予兆とされる
    """
    close = df["close"].astype(float).values
    upper, middle, lower = talib.BBANDS(close, timeperiod=period, nbdevup=nbdev, nbdevdn=nbdev)
    df["bb_upper"] = upper
    df["bb_middle"] = middle
    df["bb_lower"] = lower
    return df


# ------------------------------------------------------------
# 出来高系
# ------------------------------------------------------------
def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    OBV (On Balance Volume)
    - 出来高を累積して「資金の流入出」を表す
    - 価格が上昇した日 → 出来高を加算
    - 価格が下落した日 → 出来高を減算
    - トレンドの強弱を出来高で裏付けるために使われる
    """
    close = df["close"].astype(float).values
    volume = df["volume"].astype(float).values
    df["obv"] = talib.OBV(close, volume)
    return df

