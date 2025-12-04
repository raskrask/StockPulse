from infrastructure.jpx.jpx_fetcher import JPXListingFetcher

class StockRepository:
    def list_all_stocks(self) -> list:
        """
        すべての上場銘柄のリストを取得する
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)
        total = sheet.nrows
        candidates = list(range(total))[1:]
        #candidates = candidates[1040:1250]  # テスト用にだけ処理
        return candidates