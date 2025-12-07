import infrastructure.util.io_utils as io_utils
from infrastructure.util.normalize_date import normalize_date 
import infrastructure.util.debug as debug


class StrategySimulator:
    def __init__(self, test_term, use_cache=True):
        self.test_term = test_term
        self.use_cache = use_cache

    def run(self, record, trigger) -> list:
        """
        トリガーに基づいて仮想取引をシミュレーションする
        """
        if trigger is None or len(trigger) == 0:
            return None

        filename = f"{record.symbol}/backtest/strategy.json"
        if io_utils.exists_file(filename) and self.use_cache:
            strategy = io_utils.load_json(filename)
            return {
                "symbol": record.symbol,
                "name": record.name,
                "values": record.get_values(),
                "buy_signal": trigger,
                "sell_signal": strategy,
            }

        df = record.get_daily_chart_by_days(self.test_term)

        # 購入以降の期間を切り出す
        buy_window = df[df["date"] > trigger["date"]].reset_index(drop=True)
        buy_window = buy_window[:90] # 購入後90日間を対象
        buy_prices = buy_window['close']

        # 利益・損失の閾値
        strategy_profit = buy_prices.iloc[0] * 1.07
        strategy_loss   = buy_prices.iloc[0] * 0.95

        # 利益・損失達成インデックス
        profit_idx = buy_window[buy_window["close"] >= strategy_profit]
        loss_idx = buy_window[buy_window["close"] <= strategy_loss]

        # 判定
        strategy = None
        if len(profit_idx) == 0 and len(loss_idx) == 0:
            strategy = {'result': 'draw', **buy_window.iloc[-1].to_dict()}  # 90日間で決着がつかなかった場合は引き分けとする

        elif len(profit_idx) == 0:
            strategy = {'result': 'lose', **loss_idx.iloc[0].to_dict()}
        elif len(loss_idx) == 0:
            strategy = {'result': 'win', **profit_idx.iloc[0].to_dict()}
        else:
            # 先に到達した方で勝敗を決定
            if profit_idx.iloc[0]["date"] < loss_idx.iloc[0]["date"]:
                strategy = {'result': 'win', **profit_idx.iloc[0].to_dict()}
            else:
                strategy = {'result': 'lose',**loss_idx.iloc[0].to_dict()}

        io_utils.save_json(filename, strategy)
        return {
                    "symbol": record.symbol,
                    "name": record.name,
                    "values": record.get_values(),
                    "buy_signal": normalize_date(trigger),
                    "sell_signal": normalize_date(strategy),
                }
