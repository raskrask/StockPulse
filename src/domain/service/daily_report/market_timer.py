from datetime import datetime, time, timedelta, timezone
import jpholiday
from infrastructure.persistence.run_state_repository import RunStateRepository


class MarketTimer:
    JST = timezone(timedelta(hours=9))
    YORI_END   = time(9, 10, tzinfo=JST)
    HIKE_END   = time(15, 15, tzinfo=JST)

    def __init__(self):
        self.run_state_repo = RunStateRepository()
        self.now = datetime.now(self.JST)

    def current_session(self) -> str | None:
        if self.HIKE_END <= self.now.timetz():
            return "hike"
        if self.YORI_END <= self.now.timetz():
            return "yori"
        return None

    def previous_business_day(self) -> datetime:
        """土日祝を考慮した前営業日を返す"""
        d = self.now.date()
        while True:
            d = d - timedelta(days=1)
            if d.weekday() < 5 and not jpholiday.is_holiday(d):
                return datetime.combine(d, time())

    def baseline_time(self) -> datetime:
        """ '実行すべき基準日' を返す"""

        # 休日の場合 → 前営業日を基準にする
        if self.now.weekday() >= 5 or jpholiday.is_holiday(self.now):
            return self.previous_business_day()
        
        # 当日の場合には現在時刻から寄り引き時間に応じて実行
        session = self.current_session()
        if session == "hike":
            return datetime.combine(self.now, self.HIKE_END)

        if session == "yori":
            return datetime.combine(self.now, self.YORI_END)

        return self.now

    def should_run(self) -> bool:
        state = self.run_state_repo.load()
        last_run_at = state.get(f"last_run_at")
        if last_run_at is None:
            return True
        last_run_at = last_run_at.replace(tzinfo=self.JST)

        baseline = self.baseline_time()

        # 基準日より前の実行であれば → 未実行として実行
        return last_run_at < baseline


    def mark_executed(self):
        state = self.run_state_repo.load()

        state[f"last_run_at"] = self.now
        self.run_state_repo.save(state)