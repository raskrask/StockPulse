from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import jpholiday
from infrastructure.persistence.run_state_repository import RunStateRepository


class MarketTimer:
    MARKET_CONFIG = {
        "JP": {
            "tz": ZoneInfo("Asia/Tokyo"),
            "yori_end": (9, 10),
            "hike_end": (15, 15),
            "holiday_fn": lambda d: jpholiday.is_holiday(d),
        },
        "US": {
            "tz": ZoneInfo("America/New_York"),
            "yori_end": (9, 35),
            "hike_end": (16, 5),
            "holiday_fn": lambda d: False,
        },
    }

    def __init__(self, market: str = "JP"):
        config = self.MARKET_CONFIG.get(market, self.MARKET_CONFIG["JP"])
        self.market = market
        self.tz = config["tz"]
        self.yori_end = config["yori_end"]
        self.hike_end = config["hike_end"]
        self.is_holiday = config["holiday_fn"]
        self.run_state_repo = RunStateRepository()
        self.now = datetime.now(timezone.utc)

    def next_business_day(self, target_date: datetime) -> datetime:
        """土日祝を考慮した翌営業日を返す"""
        d = target_date.date()
        while True:
            d = d + timedelta(days=1)
            if d.weekday() < 5 and not self.is_holiday(d):
                return datetime.combine(d, time(self.yori_end[0], self.yori_end[1]), tzinfo=self.tz)

    def baseline_time(self, last_run_at: datetime) -> datetime:
        baseline = last_run_at.astimezone(self.tz)
        yori_end_dt = baseline.replace(hour=self.yori_end[0], minute=self.yori_end[1], second=0, microsecond=0)
        hike_end_dt = baseline.replace(hour=self.hike_end[0], minute=self.hike_end[1], second=0, microsecond=0)

        # 休日 → 翌営業日 寄り後
        if baseline.weekday() >= 5 or self.is_holiday(baseline.date()):
            return self.next_business_day(baseline)

        # 引け後
        if baseline >= hike_end_dt:
            return self.next_business_day(baseline)

        # 場中
        if hike_end_dt > baseline >= yori_end_dt:
            return hike_end_dt

        # 寄り前
        return yori_end_dt

    def should_run(self) -> bool:
        state = self.run_state_repo.load()

        last_run_at = state.get(f"last_run_at")
        if last_run_at is None:
            return True

        baseline = self.baseline_time(last_run_at)
        now_local = self.now.astimezone(self.tz)

        # 基準日より前の実行であれば → 未実行として実行
        return now_local > baseline


    @classmethod
    def mark_executed(cls):
        run_state_repo = RunStateRepository()
        state = run_state_repo.load()

        state[f"last_run_at"] = datetime.now(timezone.utc)
        run_state_repo.save(state)
