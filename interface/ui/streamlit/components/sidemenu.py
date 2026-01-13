import streamlit as st


def render_sidemenu(current: str | None = None):
    """
    current: 現在のフェーズ識別子
      - dashboard
      - backtest
      - analysis
      - portfolio
      - admin
    """

    with st.sidebar:
        st.markdown("## 📊 StockPulse")
        st.caption("投資判断フロー")

        # =========================
        # 市場・前提確認
        # =========================
        st.markdown("### 📈 市場・前提確認")
        st.page_link(
            "pages/00_market_overview.py",
            label="市場ダッシュボード",
            icon="🏠",
            disabled=(current == "00_market_overview"),
        )

        # =========================
        # バックテスト
        # =========================
        st.markdown("### 🔬 バックテスト")
        st.page_link(
            "pages/10_strategy_profiles.py",
            label="ストラテジープロファイル",
            disabled=(current == "10_strategy_profiles"),
        )
        st.page_link(
            "pages/11_backtest_runner.py",
            label="バックテスト実行",
            disabled=(current == "11_backtest_runner"),
        )
        st.page_link(
            "pages/12_backtest_results.py",
            label="バックテスト結果",
            disabled=(current == "12_backtest_results"),
        )

        # =========================
        # 分析・スクリーニング
        # =========================
        st.markdown("### 📊 分析・スクリーニング")
        st.page_link(
            "pages/20_screening_profiles.py",
            label="スクリーニングプロファイル",
            disabled=(current == "20_screening_profiles"),
        )
        st.page_link(
            "pages/21_screening_candidates.py",
            label="スクリーニング候補",
            disabled=(current == "21_screening_candidates"),
        )
        st.page_link(
            "pages/22_stock_insight.py",
            label="銘柄詳細分析",
            disabled=(current == "22_stock_insight"),
        )

        # =========================
        # 実運用（ポートフォリオ）
        # =========================
        st.markdown("### 💼 ポートフォリオ")
        st.page_link(
            "pages/30_portfolio_positions.py",
            label="保有中ポジション",
            disabled=(current == "30_portfolio_positions"),
        )
        st.page_link(
            "pages/31_trade_history.py",
            label="売買履歴",
            disabled=(current == "31_trade_history"),
        )
        st.page_link(
            "pages/32_trade_performance.py",
            label="投資成績・集計",
            disabled=(current == "32_trade_performance"),
        )

        # =========================
        # 管理
        # =========================
        st.markdown("---")
        st.markdown("### ⚙ 管理")
        st.page_link(
            "pages/90_cache_store.py",
            label="キャッシュ管理",
            disabled=(current == "90_cache_store"),
        )
        st.page_link(
            "pages/91_trading_gym.py",
            label="トレーディングジム",
            disabled=(current == "91_trading_gym"),
        )