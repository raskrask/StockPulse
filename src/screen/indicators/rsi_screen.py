from screen.base_screen import BaseScreen
from screen.screen_record import  ScreenRecord
from data.yf_fetcher import fetch_yf_daily
from datetime import datetime, timedelta
import pandas as pd
import talib

class RsiScreen(BaseScreen):

    def __init__(self, key, value: list[int]):
        super().__init__(key)
        self.min_value = value[0]
        self.max_value = value[1]

    def apply(self, record: ScreenRecord) -> bool:
        df = record.recent_yf_monthly()
        df.sort_index(inplace=True)
        target = datetime.today() - timedelta(days=14*2)
        period = len(df[df["date"] >= target]) # 休場日レコードを除いた期間

        df_calendar = pd.DataFrame({"date": pd.date_range(target.date(), datetime.today().date(), freq="D")})
        df_merged = df_calendar.merge(df[["date", "close"]], on="date", how="left")

        df_merged['close'] = df_merged['close'].ffill()  # 前日終値で埋める

        close = df_merged["close"].astype(float).values
        rsi = talib.RSI(close, timeperiod=14)[-1]
        record.values[self.key] = [rsi, self.min_value, self.max_value]

        return True or self.min_value <= rsi <= self.max_value

    def batch_apply(self, record: ScreenRecord, days: int) -> list[bool]:
        df = record.recent_yf_yearly(days)
        if df.empty:
            return False

        close = df["close"].astype(float).values
        rsi = talib.RSI(close, timeperiod=14)
        flags = [self.min_value <= v <= self.max_value for v in rsi]

        return flags