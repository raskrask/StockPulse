from scipy.signal import find_peaks
import pandas as pd

class DoubleBottomIndicator:

    @staticmethod
    def add_double_bottom_signal(df) -> pd.DataFrame:
        """
        ダブルボトムの判定
        - 一目均等表の核心周期の期間中にダブルボトムが形成されているかを判定
        - 価格が2回底を打ち、その間に一度ピークを形成するパターン
        - ネックラインを突破した場合に買いシグナルとする
        """
        period = 26 + 5  # 一目均等表の核心周期±5日のゆらぎ
        df_terms = df[-period:]

        # ダブルボトムの二つの谷を検出
        bottom_idx, _ = find_peaks(-df_terms["low"], distance=4, prominence=0.1)
        if len(bottom_idx) < 2:
            df["double_bottom_signal"] = False
            return df
        first_bottom_idx = bottom_idx[-2]
        first_bottom = df_terms["low"].iloc[first_bottom_idx]
        second_bottom_idx = bottom_idx[-1]
        second_bottom = df_terms["low"].iloc[second_bottom_idx]

        # ダブルの山を検出
        left_peak = df_terms["high"][:second_bottom_idx].max()
        middle_peak = df_terms["high"][first_bottom_idx:second_bottom_idx].max()
        right_peak = df_terms["high"][first_bottom_idx:].max()

        signal = first_bottom <= second_bottom and \
                right_peak >= middle_peak and \
                df_terms["close"].iloc[-1] > middle_peak

        df["double_bottom_signal"] = signal
        return df
