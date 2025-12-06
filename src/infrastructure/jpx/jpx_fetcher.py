import requests
from bs4 import BeautifulSoup
import datetime
import os
from typing import Optional
import infrastructure.util.io_utils as io_utils
#import openpyxl
import xlrd

class JPXListingFetcher:
    """
    Fetches monthly JPX Tokyo Stock Exchange listing Excel files.
    JPX updates previous month's data on the 3rd business day of each month.
    """
    BASE_URL = "https://www.jpx.co.jp"
    PAGE_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"

    def __init__(self):
       pass

    def _is_third_business_day_passed(self) -> bool:
        """
        JPX 公開ルール：
        毎月第3営業日の朝9時以降に前月末データを掲載
        """

        today = datetime.date.today()

        # 祝日は考慮せず → 日本の祝日API入れたい場合は後ほど追加可能
        business_days = [
            today.replace(day=i)
            for i in range(1, 10)
            if datetime.date(today.year, today.month, i).weekday() < 5
            and datetime.date(today.year, today.month, i).month == today.month
        ]

        third_bd = business_days[2]  # 0-based index → 第3営業日

        return today >= third_bd

    def fetch_workbook(self) -> Optional[xlrd.book.Book] :
        """Download the latest JPX listing Excel if needed."""
        
        # 月ごとのファイル名
        filepath = io_utils.get_jpx_filename(self._is_third_business_day_passed())

        # すでに存在する場合
        if os.path.exists(filepath):
            return xlrd.open_workbook(filepath)

        print("[JPX] Fetch start...")

        # ページ取得
        r = requests.get(self.PAGE_URL)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # data_j.xls を探す
        a_tag = soup.find("a", href=lambda x: x and "data_j.xls" in x)
        if not a_tag:
            raise RuntimeError("data_j.xls link not found. JPX HTML structure changed?")

        excel_url = self.BASE_URL + a_tag["href"]
        print("[JPX] Excel URL:", excel_url)

        # ダウンロード
        er = requests.get(excel_url)

        if er.status_code == 404:
            print("[JPX] まだ Excel が公開されていません（404）。後で再実行してください。")
            return None

        er.raise_for_status()
        io_utils.save_contents(er.content, filepath)
        return xlrd.open_workbook(filepath)


# 使い方
if __name__ == "__main__":
    fetcher = JPXListingFetcher()
    fetcher.fetch()
