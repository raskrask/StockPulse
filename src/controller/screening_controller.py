
from data.yf_fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from data.jpx_fetcher import JPXListingFetcher
from filters import *
import streamlit as st

class ScreeningController:
    def screen_stocks(self, params: dict, progress_container = None) -> list:
        """
        指定されたフィルター条件に基づいて銘柄をスクリーニングする
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)

        nrows = sheet.nrows
        candidates = list(range(nrows))[1:]
        params['stockNumbers'] = params.get('stockNumbers', '').strip()
        #candidates = candidates[1040:2040]  # テスト用に最初の300行だけ処理
        filters = self._build_filters(params)

        with progress_container:
            st.progress(0, text=f"Start screening...{nrows} stocks")

        result = []
        for i, x in enumerate(candidates):
            record = StockRecord(sheet.row(x))
            progress = (i + 1) / nrows
            with progress_container:
                st.progress(progress, text=f"Processing {record.symbol}... ({i+1}/{nrows})")

            if params['stockNumbers'] and record.symbol not in params['stockNumbers']:
                continue

            combined_filter = lambda record: all(filter.apply(record) for filter in filters)
            if combined_filter(record):
                result.append(record.get_values())

            #for filter in filters:
            #    if not filter.apply(record):
            #        st.write(f"{filter.key} passed for {record.symbol}")
            #        continue
            #result.append(record.get_values())



        with progress_container:
            st.progress(100, text=f"Finish Screening... {len(result)} stocks found.")
            if result:
                symbols = " ".join(s['symbol'] for s in result)
                st.markdown(f"検索結果({len(result)})件：`{symbols}`")
        return result


    def _build_filters(self, config: dict) -> list:
        result = [BasicMarketFilter()]

        filterFactory = {
            "marketCap": lambda key, v: MarketCapFilter(key, [x * 1_000_000 for x in v]),
            "avgTradingValue": lambda key, v: AvgTradingValueFilter(key, [x * 1_000 for x in v]),
            "rsi": lambda key, v: RsiFilter(key, v),
            "price_change_20d_ago": lambda key, v: PriceChangeFilter(key, v, 20),
            "sma_25_divergence":   lambda key, v: SmaFilter(key, v, 25),
            "sma_75_divergence":  lambda key, v: SmaFilter(key, v, 75),
            "sma_200_divergence": lambda key, v: SmaFilter(key, v, 200),
            "ytd_high_divergence": lambda key, v: YtdDivergenceFilter(key, v, "high"),
            "ytd_low_divergence": lambda key, v: YtdDivergenceFilter(key, v, "low"),
            "ichimoku_3yakukoten": lambda key, v: IchimokuFilter(key, v),
        }

        for key, builder in filterFactory.items():
            if key in config:
                result.append(builder(key, config[key]))

        return result