import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from infrastructure.util.line_notifier import LineNotifier
from application.daily_report_usecase import DailyReportUsecase

def main():

    # 1. 買い時株レポート作成
    report = DailyReportUsecase().generate_buy_signals()

    # 2. LINEに送信
    notifier = LineNotifier()
    notifier.send(report)

if __name__ == "__main__":
    main()