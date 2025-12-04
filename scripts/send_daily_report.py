import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from util.line_notifier import LineNotifier
from controller.daily_report_controller import DailyReportController

def main():

    # 1. 買い時株レポート作成
    report = DailyReportController().generate_buy_signals()

    # 2. LINEに送信
    notifier = LineNotifier()
    notifier.send(report)

if __name__ == "__main__":
    main()