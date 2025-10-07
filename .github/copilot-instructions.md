# StockPulse - Copilot Instructions

## プロジェクト概要
株式のテクニカル分析に基づき、毎日自動で銘柄をスクリーニングし、LINE Notifyで通知、投資成績をStreamlitで可視化する日本株・米国株対応のPythonプロジェクト。データ保存はローカルファイルとS3両対応。

## 主な機能
- スクリーニング（テクニカル指標・市場指数補正）
- LINE Notifyによる通知
- Streamlitダッシュボード
- ポジション管理（Trades→Positions自動計算）
- 利益集計・可視化

## 技術スタック
 Python
 yfinance, pandas, pandas-ta, streamlit, boto3, mplfinance, tensorflow
 データ保存：CSV/JSON（ローカル or S3）
 Docker対応（開発・デプロイ容易化）

## 開発ルール
- README.mdと本ファイルを最新化
- データ保存は S3 (boto3) またはローカルファイルを使用する。
- SQLite や MySQL などのRDBは使わない。
- `Trades` が唯一のマスター。人間が更新するのはこれだけ。
- `Positions` は `Trades` から自動計算し、キャッシュは JSON として日付ごとに保存する。
- テクニカル指標は TA-Lib を使用する。
- ダッシュボードは Streamlit + Plotly を使う。

## 使用技術

- **Python** 3.11
- **pandas / numpy / TA-Lib**
- **yfinance / mplfinance / pandas_datareader**
- **Plotly / Streamlit**
- **boto3**（S3保存用）
- **gspread**（GoogleスプレッドシートAPI）
