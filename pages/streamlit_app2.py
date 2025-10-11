import streamlit as st
from datetime import datetime, timedelta

from lib.data.fetcher import fetch_yf_daily, fetch_yf_weekly, fetch_yf_monthly


# st.set_page_config(page_title="StockPulse Test", layout="wide")
# st.title("📊 StockPulse キャッシュテスト")

symbol = st.text_input("銘柄コードを入力 (例: 7203.T)", "7203.T")
start = datetime.today() - timedelta(days=365)


@st.cache_data(ttl=3600)
def fetch_yf_cache(mode: str, symbol: str, start: datetime):
    if mode == "weekly":
        df = fetch_yf_weekly(symbol, start)
    elif mode == "monthly":
        df = fetch_yf_monthly(symbol, start)
    else:
        df = fetch_yf_daily(symbol, start)
    return df


# 日足
df_daily = fetch_yf_cache("daily", symbol, start)
st.subheader("日足 (キャッシュ+最新)")
st.write(df_daily.tail())
st.line_chart(df_daily.set_index("date")["close"])

# 週足
df_weekly = fetch_yf_cache("weekly", symbol, start)
st.subheader("週足")
st.write(df_weekly.tail())
st.line_chart(df_weekly.set_index("date")["close"])

# 月足
df_monthly = fetch_yf_cache("monthly", symbol, start)
st.subheader("月足")
st.write(df_monthly.tail())
st.line_chart(df_monthly.set_index("date")["close"])
