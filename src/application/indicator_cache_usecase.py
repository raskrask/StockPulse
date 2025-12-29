from datetime import datetime
from domain.repository.stock_repository import StockRepository
from domain.service.screening.screen_builder import ScreenBuilder
from domain.service.progress.progress_reporter import ProgressReporter, NullProgressReporter
from application.screening_profile_usecase import ScreeningProfileUsecase
from infrastructure.persistence.indicator_cache import clear_indicator_cache, save_indicator_batch, save_indicator_cache_range


class IndicatorCacheUsecase:
    def __init__(self, progress: ProgressReporter = NullProgressReporter()):
        self.progress_reporter = progress
        self.stock_repo = StockRepository()
        self.screen_builder = ScreenBuilder()

    def execute(self, profile_name: str, from_year: int, to_year: int) -> dict:
        # 1. キャッシュ対象のフィルターと銘柄の抽出
        filters = self._resolve_filters(profile_name)
        stocks = self.stock_repo.list_all_stocks(filters)
        indicators = self._build_indicators(filters)
        total = len(stocks)

        self.progress_reporter.report(0, text=f"Start indicator cache...{total} stocks")
        saved = 0
        for i, record in enumerate(stocks):
            self.progress_reporter.report((i + 1) / total, text=f"Caching {record.symbol}... ({i+1}/{total})")

            # 2. 対象期間の取引データ抽出
            df = self._load_record_df(record, from_year, to_year)
            if df is None:
                continue
            # 3. indicatorの計算
            df = self._apply_indicators(record, df, indicators)
            # 4. キャッシュの保存
            save_indicator_batch(record.symbol, df, from_year, to_year)
            saved += 1

        # 5. 保存ステータスの更新と対象期間以外の古いキャッシュの削除
        save_indicator_cache_range(from_year, to_year)
        self._clear_cache(from_year, to_year)

        return {
            "symbols": total,
            "indicators": len(indicators),
            "saved": saved,
        }

    def _resolve_filters(self, profile_name: str) -> dict:
        profile = ScreeningProfileUsecase().load_profile(profile_name)
        profile_filters = profile.get("filters", {}) if profile else {}
        return profile_filters

    def _clear_cache(self, from_year: int, to_year: int):
        deleted = clear_indicator_cache(from_year, to_year)
        if deleted:
            self.progress_reporter.report(0, text=f"Cleared {deleted} cached files.")

    def _build_indicators(self, filters: dict):
        return self.screen_builder.build_indicators(filters)

    def _load_record_df(self, record, from_year: int, to_year: int):
        from_date = datetime(from_year, 1, 1)
        to_date = datetime(to_year, 12, 31)
        df = record.get_daily_chart(from_date, to_date)
        if df is None or df.empty:
            return None
        record.set_daily_chart_days_cache(df, force=True)
        return df.copy()

    def _apply_indicators(self, record, df, indicators):
        effective_days = len(df)
        for indicator in indicators:
            values = indicator.apply_batch(record)
            values_list = [bool(v) for v in list(values)]
            if len(values_list) < effective_days:
                values_list = ([False] * (effective_days - len(values_list))) + values_list
            else:
                values_list = values_list[-effective_days:]
            df[indicator.key] = values_list
        return df
