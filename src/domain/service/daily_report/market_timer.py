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

    def previous_business_day(self) -> datetime:
        """土日祝を考慮した前営業日を返す"""
        d = self.now.date()
        while True:
            d = d - timedelta(days=1)
            if d.weekday() < 5 and not jpholiday.is_holiday(d):
                return datetime.combine(d, time())

    def baseline_time(self) -> datetime:
        now = self.now.astimezone(self.JST)

        # 休日 → 前営業日 00:00 JST
        if now.weekday() >= 5 or jpholiday.is_holiday(now.date()):
            return self.previous_business_day()

        yori_end_dt = now.replace(hour=self.YORI_END[0], minute=self.YORI_END[1], second=0, microsecond=0)
        hike_end_dt = now.replace(hour=self.HIKE_END[0], minute=self.HIKE_END[1], second=0, microsecond=0)

        # 引け後
        if now >= hike_end_dt:
            return hike_end_dt

        # 寄り前
        if now < yori_end_dt:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 場中
        return yori_end_dt

    def should_run(self) -> bool:
        state = self.run_state_repo.load()
        last_run_at = state.get(f"last_run_at")
        if last_run_at is None:
            return True

        baseline = self.baseline_time()

        # 基準日より前の実行であれば → 未実行として実行
        return last_run_at < baseline


    def mark_executed(self):
        state = self.run_state_repo.load()

        state[f"last_run_at"] = self.now
        self.run_state_repo.save(state)