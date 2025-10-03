# StockPulse

株式のテクニカル分析による自動スクリーニング・通知・投資成績可視化システム

## 機能
- 毎日自動で日本株・米国株をスクリーニング
- LINE Notifyで候補銘柄・売りシグナル通知
- Streamlitダッシュボードで投資成績・保有銘柄・損益曲線を可視化
- ポジション管理（Trades履歴から自動計算）
- データ保存はローカルCSV/JSONまたはS3

## セットアップ
1. `requirements.txt`のパッケージをインストール
2. `streamlit run dashboard/app.py` でダッシュボード起動

## ディレクトリ構成（例）
- src/ : データ取得・分析・通知ロジック
- dashboard/ : Streamlitアプリ
- data/ : ローカルデータ保存
- trades.csv : 売買履歴

## 必要パッケージ
- yfinance
- pandas
- pandas-ta
- streamlit
- boto3

---
詳細はcopilot-instructions.md参照
