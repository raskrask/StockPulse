from infrastructure.jpx.jpx_fetcher import JPXListingFetcher
from domain.model.stock_record import  StockRecord
from domain.model.indicator.listed_stock_indicator import ListedStockIndicator

class StockRepository:
    def list_all_stocks(self, params={}) -> list:
        """
        すべての上場銘柄のリストを取得する
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)
        total = sheet.nrows-1

        stocks = [StockRecord(sheet.row(i+1)) for i in range(total)]
        stocks = [s for s in stocks if ListedStockIndicator(params).apply(s)]
        #stocks = stocks[1040:1140]  # テスト用に行数を減らす

        return stocks
    
    def get_stock_by_symbol(self, symbol: str) -> StockRecord:
        """
        指定されたシンボルの銘柄情報を取得する
        """
        jpx = JPXListingFetcher()
        sheet = jpx.fetch_workbook().sheet_by_index(0)
        total = sheet.nrows-1

        for i in range(total):
            record = StockRecord(sheet.row(i+1))
            if record.symbol == symbol:
                return record

        return None
    