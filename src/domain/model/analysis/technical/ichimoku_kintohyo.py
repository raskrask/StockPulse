import pandas as pd

class IchimokuKintohyo:
    @staticmethod
    def add_3yakukoten(df) -> pd.DataFrame:
        """
        三役好転＋ダブルボトムの判定
        1. 転換線 > 基準線（転換線が上）
        2. 遅行スパン > 終値（26日前の価格より上）
        3. 終値が雲の上（上方雲抜け）
        4. ダブルボトムで２番目の安値が１つ目より安い、且つ、ネックライン突破
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # 転換線 (9日)
        tenkan_sen = (high.rolling(window=9).max() + low.rolling(window=9).min()) / 2
        # 基準線 (26日)
        kijun_sen = (high.rolling(window=26).max() + low.rolling(window=26).min()) / 2
        # 先行スパン1
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        # 先行スパン2 (52日)
        senkou_span_b = ((high.rolling(window=52).max() + low.rolling(window=52).min()) / 2).shift(26)
        # 遅行スパン
        chikou_span = close.shift(-26)

        is_tenkan_above_kijun = tenkan_sen > kijun_sen
        is_chikou_above_price_26_periods_ago = (chikou_span > close).shift(26)
        is_above_kumo = (close > senkou_span_a) & (close > senkou_span_b)
        df["ichimoku_3yakukoten"] = is_tenkan_above_kijun & is_chikou_above_price_26_periods_ago & is_above_kumo

        return df
