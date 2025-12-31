#/bin/zsh

cd "$(dirname "$0")/../"

export PYTHONPATH=src:interface
python interface/scripts/cache_indicator_results.py "$@"
