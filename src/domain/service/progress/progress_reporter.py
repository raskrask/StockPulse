from abc import ABC, abstractmethod


class ProgressReporter(ABC):
    @abstractmethod
    def report(self, progress, text: str =""):
        pass


class NullProgressReporter(ProgressReporter):
    def report(self, progress, text: str =""):
        pass  # 何もしない