from infrastructure.jpx.jpx_fetcher import JPXListingFetcher
from infrastructure.us.us_listing_fetcher import USListingFetcher
from infrastructure.yahoo.yf_fetcher import fetch_yf_info
from domain.model.stock_record import  StockRecord
from domain.service.screening.screen_builder import ScreenBuilder
from domain.repository.chart_repository import ChartRepository


class StockRepository:
    def list_all_stocks(self, params={}) -> list:
        """
        すべての上場銘柄のリストを取得する
        """
        chart_repo = ChartRepository()
        target_market = params.get("target_market")

        if target_market == "US":
            us_listings = USListingFetcher().fetch_listings()
            stocks = [StockRecord(row, self, chart_repo) for row in us_listings]
            import infrastructure.util.debug as debug

        else:
            jpx = JPXListingFetcher()
            sheet = jpx.fetch_workbook().sheet_by_index(0)
            total = sheet.nrows-1
            stocks = [StockRecord(sheet.row(i+1), self, chart_repo) for i in range(total)]

        #stocks = stocks[1040:1140]  # テスト用に行数を減らす
        fitlers = ScreenBuilder().build_default_indicators(params)
        for f in fitlers:
            stocks = [s for s in stocks if f.apply(s)]

        return stocks
    
    def get_stock_by_symbol(self, symbol: str) -> StockRecord:
        """
        指定されたシンボルの銘柄情報を取得する
        """
        record = self.get_stock_by_symbol_jp(symbol)
        if record is not None:
            return record
        return self.get_stock_by_symbol_us(symbol)

    def get_stock_by_symbol_jp(self, symbol: str) -> StockRecord:
        """
        指定されたシンボルの日本株銘柄情報を取得する
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)
        total = sheet.nrows-1
        chart_repo = ChartRepository()

        for i in range(total):
            record = StockRecord(sheet.row(i+1), self, chart_repo)
            if record.symbol == symbol:
                return record

        return None

    def get_stock_by_symbol_us(self, symbol: str) -> StockRecord:
        """
        指定されたシンボルの米国株銘柄情報を取得する
        """
        chart_repo = ChartRepository()
        us_listings = USListingFetcher().fetch_listings()
        for row in us_listings:
            if row.get("symbol") == symbol:
                return StockRecord(row, self, chart_repo)

        return None

    def get_stock_info(self, symbol: str) -> dict:
        """
        指定されたシンボルの銘柄情報を取得する
        """
        return fetch_yf_info(symbol)
