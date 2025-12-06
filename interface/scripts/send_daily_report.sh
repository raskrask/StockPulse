#/bin/zsh

cd "$(dirname "$0")/../../"

export PYTHONPATH=src:interface
python interface/scripts/send_daily_report.py
