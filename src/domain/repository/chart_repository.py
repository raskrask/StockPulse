import infrastructure.yahoo.yf_fetcher as yahoo
import infrastructure.persistence.parquet_cache as cache_store
import pandas as pd
from datetime import datetime

class ChartRepository:
    def __init__(self):
        pass


    def load_daily_by_month(self, symbol, month):
        """
        指定された銘柄の指定期間の日足チャートデータを取得する
        """

        df = cache_store.load_daily_by_month(symbol, month)

        if df is None or df.empty:
            yahoo_df = yahoo.fetch_yf_daily_by_month(symbol, month)
            cache_store.save_daily_by_month(symbol, month, yahoo_df)

        return df
           
    def load_daily_range(self, symbol, from_date, to_date):
        """
        指定された銘柄の指定期間の日足チャートデータを取得する
        """

        # Step1: 月次キャッシュの取得
        dfs = cache_store.load_daily_month_between(symbol, from_date, to_date)

        # Step2: キャッシュで不足している範囲を検出
        df_cached = pd.concat(dfs).sort_index() if dfs else pd.DataFrame()

        missing_months = self._detect_missing_ranges(df_cached, from_date, to_date)

        # Step3: 不足分だけ Yahooから取得
        for month in missing_months:
            yahoo_df = yahoo.fetch_yf_daily_by_month(symbol, month)
            dfs.append(yahoo_df)
            cache_store.save_daily_by_month(symbol, month, yahoo_df)

        # Step4: すべて結合して期間を切り取って返す
        final = pd.concat(dfs).sort_index()
        final = final.drop_duplicates(subset="date").sort_values("date")
        mask = (final["date"] >= from_date) & (final["date"] <= to_date)
        return final.loc[mask]
    
    def _detect_missing_ranges(self, df_cached, from_date, to_date):
        all_months = pd.date_range(start=from_date, end=to_date, freq="MS")
        if df_cached is None or df_cached.empty:
            return all_months

        results = []
        for month in all_months:
            month_end = pd.Timestamp(month + pd.offsets.MonthEnd(1))
            mask = (df_cached["date"] >= month) & (df_cached["date"] <= month_end)

            if df_cached.loc[mask].empty:
                results.append(month)

        return results