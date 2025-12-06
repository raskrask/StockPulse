from domain.service.progress.progress_reporter import ProgressReporter

class ChangeSignalDetector:
    def __init__(self, progress: ProgressReporter):
        self.progress = progress

    def run(self, stocks, filters) -> list:
        results = []
        days = 2
        for record in stocks:
            flags = [True] * days
            for f in filters:
                current = f.batch_apply(record, days)
                record.values[f.key] = current
                flags = [a and b for a, b in zip(flags, current)]
                if not any(flags):
                    break

            # 昨日から今日にかけてステータス変更
            if not flags[0] and flags[1]:
                trigger = record.get_daily_chart_by_days(days).iloc[-1].to_dict()
                results.append({
                    "symbol": record.symbol,
                    "name": record.name,
                    "values": record.get_values(),
                    "buy_signal": trigger,
                } )

        return results
    

    def run_mulit_filter(self, record, filters_array) -> list:

        results = []
        for filters in filters_array:
            days = 2
            flags = [True] * days
            for f in filters:
                current = f.batch_apply(record, days)
                record.values[f.key] = current
                flags = [a and b for a, b in zip(flags, current)]
                if not any(flags):
                    break

            # 昨日から今日にかけてステータス変更
            results.append( not flags[0] and flags[1] )

        return results