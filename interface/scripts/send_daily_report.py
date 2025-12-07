import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from infrastructure.util.line_notifier import LineNotifier
from application.daily_report_usecase import DailyReportUsecase

def main():

    # 1. 買い時株レポート作成
    signals = DailyReportUsecase().generate_buy_signals()

    if signals is None:
        return
    
    report = "個別株レポート\n"
    for s in signals:
        report += f"[ {s['profile']['name']} ]\n"
        for t in s['trigger']:
            report += f"  {t['symbol']} {t['name']}\n"
        if len(s['trigger']) == 0:
            report += "該当銘柄なし\n"
    print(report)

    # 2. LINEに送信
    notifier = LineNotifier()
    notifier.send(report)

if __name__ == "__main__":
    main()