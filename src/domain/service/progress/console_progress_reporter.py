import sys
from .progress_reporter import ProgressReporter

class ConsoleProgressReporter(ProgressReporter):
    def __init__(self):
        self.last_len = 0

    def report(self, progress, text: str = ""):
        i_progress = int(progress*100)
        msg = f"{i_progress:3d}% {text}"
        # 前回より短い表示が来た場合のために上書き消し込み
        padding = " " * max(0, self.last_len - len(msg))
        sys.stdout.write("\r" + msg + padding)
        sys.stdout.flush()
        self.last_len = len(msg)

        if progress >= 100:
            print()  # 完了時だけ改行