import streamlit as st
from datetime import datetime, timedelta

from infrastructure.yf_fetcher import fetch_yf_daily
from domain.model.analysis.regimes.trend import add_trend, trend_status, is_upward, is_downward
from ui.streamlit.components import market_card


st.title("🌏 市場概要 - Market Overview")

st.caption(
    "S&P500、NASDAQ、日経平均、米国債利回り、ドル円など主要インデックスの動向を表示します。\n"
    "短期（日足）、中期（週足13週）、長期（月足12ヶ月）のトレンドを自動判定し、"
    "リスクオン/リスクオフ環境を把握するための基準を提供します。"
)

# 対象インデックス
indices = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "日経平均": "^N225",
    "米10年国債利回り": "^TNX",
    "ドル円": "JPY=X",
}

start = datetime.today() - timedelta(days=365 * 2)

cols = st.columns(2)

for i, (name, symbol) in enumerate(indices.items()):
    col = cols[i % 2]
    with col:
        df = fetch_yf_daily(symbol, start)
        df = add_trend(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        change = (latest["close"] - prev["close"]) / prev["close"] * 100

        # EMAトレンド
        trend = trend_status(latest)

        # 週足13週・月足12ヶ月の傾きチェック
        upward_13w = is_upward(
            df["close"], lookback=65, threshold=0.2
        )  # 日足65営業日 ≒ 13週
        upward_12m = is_upward(
            df["close"], lookback=252, threshold=0.2
        )  # 日足252営業日 ≒ 12ヶ月
        downward_13w = is_downward(
            df["close"], lookback=65, threshold=-0.001
        )  # 日足65営業日 ≒ 13週

        # 状態コメント
        if upward_13w and upward_12m:
            comment = "長期・中期ともに右肩上がり ✅"
        elif upward_13w:
            comment = "中期は右肩上がり、長期は不明 ⚠️"
        elif upward_12m:
            comment = "長期は右肩上がり、中期は不明 ⚠️"
        elif downward_13w:
            comment = "長期・中期ともに右肩下がり ❌"
        else:
            comment = "方向感なし ➖"

        market_card(
            title=name,
            value=f"{latest['close']:.2f}",
            trend=trend,
            comment=comment,
            delta=change,
            df=df[["date", "close", "ema20", "ema50", "ema200"]].iloc[-60:],
        )
