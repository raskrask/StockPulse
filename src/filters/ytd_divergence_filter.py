from .screening_filter import ScreeningFilter , StockRecord
from data.yf_fetcher import fetch_yf_daily, fetch_yf_info
from datetime import datetime, timedelta
import numpy as np

class YtdDivergenceFilter(ScreeningFilter):
    """
    年初来（YTD）の高値・安値に対する上昇率／下落率フィルター
    """

    def __init__(self, key, divergence_range: list[float], type: str):
        super().__init__(key)
        # UIからの [min%, max%] （例：[-10, +20]）
        self.min_value = divergence_range[0]
        self.max_value = divergence_range[1]
        self.type = type

    def apply(self, record: StockRecord) -> bool:
        # 暫定決算発表日取得(未来の場合には四半期強制的に戻す)
        #info = fetch_yf_info(record.symbol)
        #target = datetime.fromtimestamp( info['earningsTimestampEnd'] )
        #if target >= datetime.today():
        #    target = datetime.fromtimestamp( info['earningsTimestampStart'] )
        #    if target >= datetime.today():
        #        target = target - timedelta(days=90)
        target = datetime.today().replace(month=1, day=1)

        df = fetch_yf_daily(record.symbol, target)
        if df.empty:
            return False
        df = df[df["date"] >= target]

        close = df["close"].astype(float).values

        last = close[-1]
        if self.type == "high":
            # 高値乖離率： (終値 - 年初来高値) / 年初来高値 × 100
            ytd = np.max(df["high"].astype(float).values)
            #ytd = df.iloc[0]["high"]
            ytd_div = (last - ytd) / ytd * 100
        else:
            # 安値乖離率： (終値 - 年初来安値) / 年初来安値 × 100
            ytd = np.min(df["low"].astype(float).values)
            #ytd = df.iloc[0]["low"]
            ytd_div = (last - ytd) / ytd * 100

        record.values[self.key] = [ytd_div, ytd, last, target, self.min_value, self.max_value]

        # 乖離率（%）
        return self.min_value <= ytd_div <= self.max_value
