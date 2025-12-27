from domain.model.indicator.base_indicator import BaseIndicator
from domain.model.stock_record import  StockRecord
from domain.repository.chart_repository import ChartRepository
import pandas as pd
from datetime import datetime, timedelta

class TrendIndicator(BaseIndicator):

    VIX_SIMBOL = "^VIX"
    VIX_RISK_ON = 40
    vix_risk = None # 呼び出し結果が同一のためキャッシュ

    def __init__(self, params: dict = {}):
        super().__init__("trend")
        self.repo = ChartRepository()

    def screen_now(self, record: StockRecord) -> bool:
        if self.vix_risk is None:
            today = datetime.today()
            start = today - timedelta(days=7) # 休日のVIXは取得できない場合あり
            df = self.repo.load_daily_range(self.VIX_SIMBOL, start, today)
            self.vix_risk = df['close'] <= self.VIX_RISK_ON

        return self.vix_risk.iloc[-1]

    def screen_range(self, record: StockRecord, days) -> list[bool]:
        if self.vix_risk is None:
            today = datetime.today()
            start = today - timedelta(days=days*1.5+7) # 休日のVIXは取得できない場合あり

            df = self.repo.load_daily_range(self.VIX_SIMBOL, start, today)
            self.vix_risk = (df["close"] < self.VIX_RISK_ON).iloc[-days:]
        return self.vix_risk.iloc[-days:]
