from infrastructure.persistence.json_cache import load_backend_trigger, save_backend_trigger
import pandas as pd
from datetime import datetime, timedelta
import time
from collections import defaultdict

class TriggerGenerator:
    def __init__(self, test_term, use_cache=False):
        self.test_term = test_term
        self.use_cache = use_cache
        self.timer_map = defaultdict(float)

    def run(self, record, filters) -> list:
        """
        フィルター条件に基づいて、売買トリガー（シグナル）を生成する
        test_range: バックテストする期間を指定
        """
        if self.use_cache and (cached := load_backend_trigger(record.symbol)) is not None:
            return cached

        flags = [True] * self.test_term

        for f in filters:
            start = time.perf_counter()
            current = f.screen_range(record, self.test_term)
            self.timer_map[f.key] += (time.perf_counter() - start)

            record.values[f.key] = current
            flags = [(a and b) for a, b in zip(flags, current)]
            if not any(flags):
                break

        if any(flags):
            first_trigger = next((i for i, x in enumerate(flags) if x), None)
            trigger = record.get_daily_chart_by_days(self.test_term).iloc[first_trigger].to_dict()
            save_backend_trigger(record.symbol, trigger)
            return trigger

        save_backend_trigger(record.symbol, {})
        return None