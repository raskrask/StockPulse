from datetime import datetime, time, timedelta, timezone
import jpholiday
from infrastructure.persistence.run_state_repository import RunStateRepository


class MarketTimer:
    JST = timezone(timedelta(hours=9))
    YORI_END   = (9, 10)
    HIKE_END   = (15, 15)

    def __init__(self):
        self.run_state_repo = RunStateRepository()
        self.now = datetime.now(timezone.utc)

    def next_business_day(self, target_date: datetime) -> datetime:
        """土日祝を考慮した翌営業日を返す"""
        d = target_date.date()
        while True:
            d = d + timedelta(days=1)
            if d.weekday() < 5 and not jpholiday.is_holiday(d):
                return datetime.combine(d, time(self.YORI_END[0], self.YORI_END[1]), tzinfo=self.JST)

    def baseline_time(self, last_run_at: datetime) -> datetime:
        baseline = last_run_at.astimezone(self.JST)
        yori_end_dt = baseline.replace(hour=self.YORI_END[0], minute=self.YORI_END[1], second=0, microsecond=0)
        hike_end_dt = baseline.replace(hour=self.HIKE_END[0], minute=self.HIKE_END[1], second=0, microsecond=0)

        # 休日 → 翌営業日 寄り後
        if baseline.weekday() >= 5 or jpholiday.is_holiday(baseline.date()):
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
        now_jst = self.now.astimezone(self.JST)

        # 基準日より前の実行であれば → 未実行として実行
        return now_jst > baseline


    def mark_executed(self):
        state = self.run_state_repo.load()

        state[f"last_run_at"] = self.now
        self.run_state_repo.save(state)