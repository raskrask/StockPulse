import csv
import requests

import infrastructure.util.io_utils as io_utils


class USListingFetcher:
    SP500_URL = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    CACHE_PATH = "us_list/us_listings.json"

    def fetch_listings(self, force_refresh: bool = False) -> list[dict]:
        cached = io_utils.load_json(self.CACHE_PATH)
        if cached:
            return cached

        listings = self._fetch_sp500_listings()

        io_utils.save_json(self.CACHE_PATH, listings)
        return listings

    def _normalize_symbol(self, symbol: str) -> str:
        return symbol.replace(".", "-")

    def _fetch_sp500_listings(self) -> list[dict]:
        res = requests.get(self.SP500_URL, timeout=30)
        res.raise_for_status()
        reader = csv.DictReader(res.text.splitlines())
        listings = []

        for row in reader:
            symbol = row.get("Symbol")
            name = row.get("Security")
            if not symbol or not name:
                continue
            listings.append({
                "symbol": self._normalize_symbol(symbol),
                "name": name,
                "market": "S&P 500",
            })
        return listings
