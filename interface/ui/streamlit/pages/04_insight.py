import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        df = record.get_daily_chart_by_days(100)
    return df


# 日足
df_daily = fetch_yf_cache("daily", symbol, start)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

candle = go.Candlestick(x=df_daily["date"], open=df_daily["open"], high=df_daily["high"], low=df_daily["low"], close=df_daily["close"], name="ローソク足")
bar = go.Bar(x=df_daily["date"], y=df_daily["volume"], name="出来高")

fig.add_trace(candle, row=1, col=1)
fig.add_trace(bar, row=2, col=1)
fig.update_layout(title="日足", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)


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

st.write("====== テスト用 ======")
from domain.model.analysis.technical.ueno_theory import UenoTheory

df = record.get_daily_chart_by_days(20*5*2)
result = UenoTheory().add_ueno_theory_signal(df)
st.write(result)

