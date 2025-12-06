import numpy as np

class BacktestEvaluator:
    def __init__(self):
        pass
    def run(self, strategy: list, params: dict) -> dict:
        """
        バックテストの結果から評価指標（勝率、PF、最大ドローダウンなど）を計算する
        """
        strategy = [s for s in strategy if s is not None]
        if len(strategy) == 0:
            return {}

        # 勝率
        win_rate = sum(x["sell_signal"]["result"] == "win" for x in strategy) / len(strategy)
        lose_rate = sum(x["sell_signal"]["result"] == "lose" for x in strategy) / len(strategy)
        draw_rate = sum(x["sell_signal"]["result"] == "draw" for x in strategy) / len(strategy)
        # Profit Factor
        returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"])/x["buy_signal"]["close"] for x in strategy]
        #returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"])*100 for x in strategy]
        #returns = [(x["sell_signal"]["close"]-x["buy_signal"]["close"]) for x in strategy]
        trade_term = [x["sell_signal"]["date"]-x["buy_signal"]["date"] for x in strategy]
        gross_profit = sum([x for x in returns if x > 0])
        gross_loss = -sum([x for x in returns if x < 0])
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
        total_return = gross_profit - gross_loss

        # 最大ドローダウン
        total_return = sum([x for x in returns])
#        roll_max = total_return.cummax()
#        dd = (total_return - roll_max) / roll_max
#        max_drawdown = dd.min()

        return {
            "trades": len(strategy),
            "win_rate": win_rate,
            "lose_rate": lose_rate,
            "draw_rate": draw_rate,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "trade_term_avg": np.mean([t.days for t in trade_term]),
#            "max_drawdown": max_drawdown,
            "total_return": total_return,
            "strategy": strategy,
        }
        pass