from .base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from domain.repository.chart_repository import ChartRepository
import pandas as pd
from datetime import datetime, timedelta

class TrendIndicator(BaseIndicator):

    VIX_SIMBOL = "^VIX"
    VIX_RISK_ON = 25

    def __init__(self, key):
        super().__init__("trend")
        self.repo = ChartRepository()

    def apply(self, record: StockRecord) -> bool:
        df = self.repo.load_daily_by_month(self.VIX_SIMBOL, datetime.today())

        return df['close'].iloc[-1] <= self.VIX_RISK_ON

    def batch_apply(self, record: StockRecord, days) -> list[bool]:
        today = datetime.today()
        start = today - timedelta(days=days+1) # 当日のVIXは取得できない場合あり

        df = self.repo.load_daily_range(self.VIX_SIMBOL, start, today)
        return df[df["close"] < self.VIX_RISK_ON].iloc[-2:]
