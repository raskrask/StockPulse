from scipy.signal import find_peaks
import pandas as pd
import numpy as np
import infrastructure.util.debug as debug

class UenoTheory:
    def __init__(self):
        self.window_size = 20 * 3

    def add_ueno_theory_signal(self, df) -> dict:
        """
        上野理論の判定
        - 出来高が高値の位置を３ヶ月程度で抽出し、該当日の高値と安値の中間点より、上にあるかを判定
        - 現在位置から下回ったときに、足場となるヨコヨコ層があると直良
        """
        df = self.detect_high_volume_days(df)
        df = self.detect_signal(df)

        return df

        
    def detect_signal(self, df):
        df = df.copy()
        df["ueno_theory_signal"] = False

        for i in range(len(df)):

            # window_size 前を取得（i-window_size が 0 未満の場合も安全に扱う）
            start = max(0, i - self.window_size)
            hv_df = df.iloc[start:i]

            # 高出来高だけに絞る
            hv_df = hv_df[hv_df["is_high_volume"]]
            if hv_df.empty:
                continue

            close_now = df.iloc[i]["close"]
            centers = (hv_df["high"] + hv_df["low"]) / 2

            # 全て中央線 < 現在値 なら signal=True
            if (close_now > centers).all():
                df.at[df.index[i], "ueno_theory_signal"] = True

        return df

    # 出来高の多い陽線を検出（３ヶ月間で集計）
    def detect_high_volume_days(self, df, volume_ratio=1.5, cv_threshold=0.3, z_threshold=2.5):
        df = df.copy()

        # 2か月間の平均と標準偏差
        vol = df['volume']
        vol_mean = vol.rolling(window=self.window_size).mean()
        vol_std = vol.rolling(window=self.window_size).std(ddof=0)
        z = (vol - vol_mean) / vol_std
        cv = vol_std / vol_mean
        pos = df['open'] < df['close']

        # 平均 + 標準偏差1.5倍以上、z2.5以上を急増と判定
        threshold = vol_mean + volume_ratio * vol_std
        df['is_high_volume'] = (vol > threshold) & (cv > cv_threshold) & (z > z_threshold)# & pos

        return df