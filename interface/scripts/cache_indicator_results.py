import argparse
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from application.indicator_cache_usecase import IndicatorCacheUsecase
from domain.service.progress.progress_reporter import ProgressReporter


class ConsoleProgressReporter(ProgressReporter):
    def report(self, progress, text: str = ""):
        if text:
            print(text)


def main():
    parser = argparse.ArgumentParser(description="Cache indicator batch results for backtests.")
    parser.add_argument("--from-year", type=int, required=True, help="Start year for range cache (inclusive).")
    parser.add_argument("--to-year", type=int, required=True, help="End year for range cache (inclusive).")
    parser.add_argument("--profile", type=str, default="default", help="Screening profile name.")
    args = parser.parse_args()

    results = IndicatorCacheUsecase(progress=ConsoleProgressReporter()).execute(
        profile_name=args.profile,
        from_year=args.from_year,
        to_year=args.to_year,
    )
    print(f"Completed: {results}")


if __name__ == "__main__":
    main()
