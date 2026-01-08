import argparse
import pathlib
import sys

from application.backtest_usecase import BacktestUsecase
from application.screening_profile_usecase import ScreeningProfileUsecase
from domain.service.progress.console_progress_reporter import ConsoleProgressReporter

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

def main():
    parser = argparse.ArgumentParser(description="Run backtest from CLI.")
    parser.add_argument("--profile", type=str, default="", help="Screening profile name.")
    parser.add_argument("--use-cache", action="store_true", help="Use cached indicator results.")
    args = parser.parse_args()

    profile_usecase = ScreeningProfileUsecase()
    profile_names = [args.profile] if args.profile else profile_usecase.list_profiles()
    if not profile_names:
        raise SystemExit("No screening profiles found.")

    for profile_name in profile_names:
        data = profile_usecase.load_profile(profile_name)
        filters = data.get("filters")
        if not filters:
            print(f"Skip '{profile_name}': no filters.")
            continue

        results = BacktestUsecase(
            progress=ConsoleProgressReporter(),
            use_cache=args.use_cache,
        ).execute_backtest(params=filters, profile_name=profile_name)

        print(f"Completed: {profile_name} {results['win_rate']*100:.1f}% / {results['trades']}回")

if __name__ == "__main__":
    main()
