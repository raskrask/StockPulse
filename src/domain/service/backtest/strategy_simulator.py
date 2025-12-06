import infrastructure.util.io_utils as io_utils

class StrategySimulator:
    def __init__(self, use_cache=True):
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

        df = record.recent_yf_yearly()

        # 購入以降の期間を切り出す
        buy_window = df[df["date"] >= trigger["date"]].copy()
        buy_prices = buy_window['close'][:90]  # 購入後90日間を対象

        # 利益・損失の閾値
        strategy_profit = buy_prices.iloc[0] * 1.07
        strategy_loss   = buy_prices.iloc[0] * 0.95

        # 利益・損失達成インデックス
        profit_idx = buy_prices[buy_prices >= strategy_profit].index
        loss_idx   = buy_prices[buy_prices <= strategy_loss].index

        # 判定
        strategy = None
        if len(profit_idx) == 0 and len(loss_idx) == 0:
            #return None
            strategy = {'result': 'draw', **df.iloc[90].to_dict()}  # 90日間で決着がつかなかった場合は引き分けとする

        elif len(profit_idx) == 0:
            strategy = {'result': 'lose', **df.iloc[loss_idx[0]].to_dict()}
        elif len(loss_idx) == 0:
            strategy = {'result': 'win', **df.iloc[profit_idx[0]].to_dict()}
        else:
            # 先に到達した方で勝敗を決定
            if profit_idx[0] < loss_idx[0]:
                strategy = {'result': 'win', **df.iloc[profit_idx[0]].to_dict()}
            else:
                strategy = {'result': 'lose', **df.iloc[loss_idx[0]].to_dict()}

        io_utils.save_json(filename, strategy)
        return {
                    "symbol": record.symbol,
                    "name": record.name,
                    "values": record.get_values(),
                    "buy_signal": trigger,
                    "sell_signal": strategy,
                }


