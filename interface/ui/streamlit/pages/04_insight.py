import streamlit as st
from datetime import datetime, timedelta

from infrastructure.yahoo.yf_fetcher import fetch_yf_daily_by_month, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from infrastructure.jpx.jpx_fetcher import JPXListingFetcher
from domain.repository.stock_repository import StockRepository

st.set_page_config(page_title="StockPulse Insight", layout="wide")
st.title("🔍 銘柄詳細")

symbol = st.text_input("銘柄コードを入力 (例: 7203.T)", "7203.T")

repo = StockRepository()
record = repo.get_stock_by_symbol(symbol)

st.write("銘柄名:", record.rawdata[2].value)
st.write("市場:", record.rawdata[3].value)
st.write("業種:", record.rawdata[7].value)
st.write("規模:", record.rawdata[9].value)

start = datetime.today() - timedelta(days=365)
info = fetch_yf_info(symbol)
st.write("時価総額", "{:,}".format(info['marketCap']))

@st.cache_data(ttl=3600)
def fetch_yf_cache(mode: str, symbol: str, start: datetime):
    if mode == "weekly":
        df = fetch_yf_weekly(symbol, start)
    elif mode == "monthly":
        df = fetch_yf_monthly(symbol, start)
    else:
        df = fetch_yf_daily_by_month(symbol, start)
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
