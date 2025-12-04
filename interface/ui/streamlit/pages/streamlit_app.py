import streamlit as st
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
from analysis.regimes.trend import add_trend, trend_status, overall_comment
from ui import metric_card
from data.yf_fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly

# st.set_page_config(page_title="StockPulse", layout="wide")
# st.title("🌍 StockPulse ダッシュボード")
st.header("市場動向")

start = datetime.today() - timedelta(days=180)


@st.cache_data(ttl=3600)
def fetch_yf(symbol: str, name: str):
    df = yf.download(symbol, start=start, progress=False)

    # マルチカラム対策: 列名を平坦化
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]

    df = df.reset_index().rename(columns=str.lower)
    df = add_trend(df)

    latest = df.iloc[-1]  # Series
    prev = df.iloc[-2]  # Series

    trend = trend_status(latest)
    change = (
        (float(latest["close"]) - float(prev["close"])) / float(prev["close"]) * 100
    )

    return {"name": name, "df": df, "latest": latest, "trend": trend, "change": change}


# 米国指数
sp500 = fetch_yf("^GSPC", "S&P500")
nasdaq = fetch_yf("^NDX", "NASDAQ100")

# 日本株
nikkei = fetch_yf("^N225", "日経平均")

# 米国10年債利回り (FRED)
us_rate_trend = "→ Neutral"
try:
    dgs10 = pdr.DataReader("DGS10", "fred", start=start)
    dgs10 = (
        dgs10.dropna().reset_index().rename(columns={"DATE": "date", "DGS10": "close"})
    )
    dgs10 = add_trend(dgs10)
    latest, prev = dgs10.iloc[-1], dgs10.iloc[-2]
    us_rate_trend = trend_status(latest)
    us_rate_change = latest["close"] - prev["close"]
    st.subheader("米国10年債利回り")
    st.metric(
        label=us_rate_trend,
        value=f"{latest['close']:.2f}%",
        delta=f"{us_rate_change:.2f}",
    )
    st.line_chart(dgs10.set_index("date")[["close", "ema20", "ema50", "ema200"]])
except Exception as e:
    st.warning(f"米国金利取得エラー: {e}")

# 日本国債 or 為替
jp_rate_trend = "→ Neutral"
try:
    jgb10 = yf.download("^JGB10Y", start=start, progress=False)
    jgb10 = jgb10.rename(columns=str.lower).reset_index()
    jgb10 = add_trend(jgb10)
    latest, prev = jgb10.iloc[-1], jgb10.iloc[-2]
    jp_rate_trend = trend_status(latest)
    change = latest["close"] - prev["close"]
    st.subheader("日本国債10年利回り")
    st.metric(
        label=jp_rate_trend, value=f"{latest['close']:.2f}%", delta=f"{change:.2f}"
    )
    st.line_chart(jgb10.set_index("date")[["close", "ema20", "ema50", "ema200"]])
except Exception:
    usd_jpy = fetch_yf("JPY=X", "USD/JPY")
    jp_rate_trend = usd_jpy["trend"]

# 指数カード
for idx in [sp500, nasdaq, nikkei]:
    st.subheader(idx["name"])
    st.metric(
        label=idx["trend"],
        value=f"{float(idx['latest']['close']):.2f}",
        delta=f"{idx['change']:.2f}%",
    )
    st.line_chart(idx["df"].set_index("date")[["close", "ema20", "ema50", "ema200"]])

# 総合コメント
summary, details = overall_comment(
    sp500["trend"], nikkei["trend"], us_rate_trend, jp_rate_trend
)
st.markdown(f"## {summary}")
st.caption(details)


# ------------------------------test
col1, col2, col3 = st.columns(3)

with col1:
    metric_card("S&P500", "6715.35", "+0.06%", "↑ Uptrend")

with col2:
    metric_card("NASDAQ100", "14785.22", "-0.12%", "↓ Downtrend")

with col3:
    metric_card("日経平均", "32345.67", "+0.21%", "↑ Uptrend")
