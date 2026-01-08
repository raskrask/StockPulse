#/bin/zsh

cd "$(dirname "$0")/../"

export PYTHONPATH=src:interface
python interface/scripts/run_backtest.py "$@"
