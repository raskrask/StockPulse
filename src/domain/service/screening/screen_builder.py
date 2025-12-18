
from domain.model.indicator.trend.trend_indicator import TrendIndicator
from domain.model.indicator.trend.sma_indicator import SmaIndicator
from domain.model.indicator.trend.ichimoku_indicator import IchimokuIndicator
from domain.model.indicator.trend.ytd_divergence_indicator import YtdDivergenceIndicator
from domain.model.indicator.momentum.rsi_indicator import RsiIndicator
from domain.model.indicator.momentum.high_breakout_indicator import HighBreakoutIndicator
from domain.model.indicator.momentum.price_change_indicator import PriceChangeIndicator
from domain.model.indicator.momentum.double_bottom_indicator import DoubleBottomIndicator
from domain.model.indicator.momentum.ueno_theory_indicator import UenoTheoryIndicator
from domain.model.indicator.fundamental.avg_trading_value_indicator import AvgTradingValueIndicator
from domain.model.indicator.fundamental.listed_stock_indicator import ListedStockIndicator
from domain.model.indicator.fundamental.market_cap_indicator import MarketCapIndicator
from domain.model.indicator.fundamental.reject_ipo_indicator import RejectIpoIndicator

class ScreenBuilder:
    """
    「売買判断の観測軸」を定義する Indicatorのファクトリークラス
    Indicator は以下の判断軸ごとにサブフォルダで分類する。

    ------------------------------------------------
    ① Trend（方向）
    - 相場・銘柄が上向きか下向きか
    - 例：MA乖離率, 高値/安値からの距離, Ichimoku, Trend 判定

    ② Momentum（勢い）
    - 価格変化の勢い・反転兆候
    - 例：RSI, Price Change、Double Bottom, 上野理論

    ③ Volatility（荒さ）
    - 値動きの大きさ・不安定さ
    - 例：ATR, Bollinger Band 幅

    ④ Fundamental（属性制限）
    - 取引対象を絞るための条件
    - 例：時価総額, 上場区分, 平均売買代金

    """
    def build_indicators(self, params: dict) -> list:
        # デフォルトインジゲーターの設定
        result = [
            ListedStockIndicator(params), 
            TrendIndicator(params), 
            RejectIpoIndicator(params)
        ]

        indicators = {
            "marketCap": lambda key, v: MarketCapIndicator(key, [x * 1_000_000 for x in v]),
            "avgTradingValue": lambda key, v: AvgTradingValueIndicator(key, [x * 1_000 for x in v]),
            "rsi": lambda key, v: RsiIndicator(key, v),
            "high_breakout": lambda key, v: HighBreakoutIndicator(key, v),
            "price_change_20d_ago": lambda key, v: PriceChangeIndicator(key, v, 20),
            "sma_25_divergence":   lambda key, v: SmaIndicator(key, v, 25),
            "sma_75_divergence":  lambda key, v: SmaIndicator(key, v, 75),
            "sma_200_divergence": lambda key, v: SmaIndicator(key, v, 200),
            "sma_75_200_divergence": lambda key, v: SmaIndicator(key, v, 75, 200),
            "ytd_high_divergence": lambda key, v: YtdDivergenceIndicator(key, v, "high"),
            "ytd_low_divergence": lambda key, v: YtdDivergenceIndicator(key, v, "low"),
            "ichimoku_3yakukoten": lambda key, v: IchimokuIndicator(key, v),
            "double_bottom_signal": lambda key, v: DoubleBottomIndicator(key, v),
            "ueno_theory_signal": lambda key, v: UenoTheoryIndicator(key, v),
        }

        for key, builder in indicators.items():
            if key in params:
                result.append(builder(key, params[key]))

        return result