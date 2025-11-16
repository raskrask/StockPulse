
from data.yf_fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from data.jpx_fetcher import JPXListingFetcher
from filters import *

class ScreeningController:
    def screen_stocks(self, filters: dict) -> list:
        """
        指定されたフィルター条件に基づいて銘柄をスクリーニングする
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)

        filters = [
            BasicMarketFilter(),
            MarketCapFilter([x * 1_000_000 for x in filters["marketCap"]]), # 100万円単位
            AvgTradingValueFilter([x * 1_000 for x in filters["avgTradingValue"]]), # 千円単位
            RsiFilter(filters["rsi"]),
        ]
        
        candidates = list(range(sheet.nrows))
        candidates = candidates[200:220]  # テスト用に最初の300行だけ処理
        for f in filters:
            candidates = [r for r in candidates if r in f.apply(sheet, candidates)]

        return [sheet.row_values(r) for r in candidates]


        # 銘柄リストの取得
        # 例: sheet = workbook.sheet_by_index(0)
        # 例: symbols = [row[1] for row in sheet.get_rows() if 条件] 

        # ここにスクリーニングロジックを実装
        results = []
        # 例: filters = {"market_cap_min": 1_000_000_000, "sector": "Technology"}
        for symbol in self.get_all_symbols():
            info = fetch_yf_info(symbol)
            if self.apply_filters(info, filters):
                results.append(symbol)
        return results