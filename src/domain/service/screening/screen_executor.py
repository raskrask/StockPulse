from domain.service.progress.progress_reporter import ProgressReporter

class ScreenExecutor:
    def __init__(self, progress: ProgressReporter):
        self.progress = progress

    def run(self, stocks: list[any], filters : list[any]) -> list[any]:

        result = []
        total = len(stocks)

        for i, record in enumerate(stocks):
            self.progress.report((i + 1) / total, f"Screening {record.symbol}")
            if all(f.apply(record) for f in filters):
                result.append(record)

        return result