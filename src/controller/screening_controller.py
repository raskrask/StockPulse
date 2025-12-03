
from data.yf_fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from data.jpx_fetcher import JPXListingFetcher
from screen.screen_factory import ScreenFactory
from screen.screen_record import  ScreenRecord
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
        candidates = candidates[1040:1140]  # テスト用に最初の300行だけ処理
        filters = ScreenFactory.build_screens(params)

        with progress_container:
            st.progress(0, text=f"Start screening...{nrows} stocks")

        result = []
        for i, x in enumerate(candidates):
            record = ScreenRecord(sheet.row(x))
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

        return result

