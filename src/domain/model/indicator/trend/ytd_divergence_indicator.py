from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from datetime import datetime, timedelta
import numpy as np

class YtdDivergenceIndicator(BaseIndicator):
    """
    年初来（YTD）の高値・安値に対する上昇率／下落率フィルター
    (1月から3月までは前年末からの乖離率を使用)
    """

    def __init__(self, key, divergence_range: list[float], type: str):
        super().__init__(key)
        # UIからの [min%, max%] （例：[-10, +20]）
        self.min_value = divergence_range[0]
        self.max_value = divergence_range[1]
        self.type = type

    def screen_now(self, record: StockRecord) -> bool:
        # 暫定決算発表日取得(未来の場合には四半期強制的に戻す)
        #info = fetch_yf_info(record.symbol)
        #target = datetime.fromtimestamp( info['earningsTimestampEnd'] )
        #if target >= datetime.today():
        #    target = datetime.fromtimestamp( info['earningsTimestampStart'] )
        #    if target >= datetime.today():
        #        target = target - timedelta(days=90)


        target = datetime.today().replace(month=1, day=1)
        if datetime.today().month <= 3:
            target = target.replace(year=target.year - 1)

        df = record.get_daily_chart_by_days((datetime.today() - target).days)
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

        record.values[self.key] = [ytd_div, ytd, last, self.min_value, self.max_value]

        # 乖離率（%）
        return self.min_value <= ytd_div <= self.max_value

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        values = self._screen_range_with_cache(record, days)
        return [self.min_value <= v <= self.max_value for v in values]

    def calc_series(self, record: StockRecord, days):
        df = record.get_daily_chart_by_days(days)
        if df is None or df.empty:
            return []
        close = df["close"].astype(float).values
        values = []
        for i in range(len(df)):
            date = df.iloc[i]["date"]
            year_start = date.replace(month=1, day=1)
            if date.month <= 3:
                year_start = year_start.replace(year=year_start.year - 1)
            df_ytd = df[(df["date"] >= year_start) & (df["date"] <= date)]
            if self.type == "high":
                ytd = np.max(df_ytd["high"].astype(float).values)
                ytd_div = (close[i] - ytd) / ytd * 100
            else:
                ytd = np.min(df_ytd["low"].astype(float).values)
                ytd_div = (close[i] - ytd) / ytd * 100
            values.append(ytd_div)
        return values[-days:]
