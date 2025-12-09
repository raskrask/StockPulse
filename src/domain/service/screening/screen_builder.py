from domain.model.indicator import *

class ScreenBuilder:
    def build_indicators(self, params: dict) -> list:
        # デフォルトインジゲーターの設定
        result = [ListedStockIndicator(params), TrendIndicator(params)]

        indicators = {
            "marketCap": lambda key, v: MarketCapIndicator(key, [x * 1_000_000 for x in v]),
            "avgTradingValue": lambda key, v: AvgTradingValueIndicator(key, [x * 1_000 for x in v]),
            "rsi": lambda key, v: RsiIndicator(key, v),
            "price_change_20d_ago": lambda key, v: PriceChangeIndicator(key, v, 20),
            "sma_25_divergence":   lambda key, v: SmaIndicator(key, v, 25),
            "sma_75_divergence":  lambda key, v: SmaIndicator(key, v, 75),
            "sma_200_divergence": lambda key, v: SmaIndicator(key, v, 200),
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