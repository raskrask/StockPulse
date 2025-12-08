import streamlit as st
import pandas as pd
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

#@st.cache_data(ttl=3600)
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

ueno_theory = UenoTheory()
df = record.get_daily_chart_by_days(ueno_theory.window_size+20)
result = ueno_theory.add_ueno_theory_signal(df)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

candle = go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="ローソク足")
fig.add_trace(candle, row=1, col=1)

high_volume = df[df['is_high_volume']]

colors = ["green" if c > o else "red" for c, o in zip(df["close"], df["open"])]
traces = [
    go.Bar(x=df["date"], y=df["volume"], name="出来高", marker=dict(color=colors)),
    go.Scatter(x=high_volume["date"], y=high_volume["volume"], mode="markers", name="high_volume", marker=dict(color="blue", size=8, symbol="circle"))
]
for t in traces:
    fig.add_trace(t, row=2, col=1)

fig.update_layout(title="日足", xaxis_rangeslider_visible=False)

for idx, row in high_volume.iterrows():
    start_date = row["date"]
    end_date = pd.to_datetime(start_date) + pd.Timedelta(days=90)  # 3か月後
    fig.add_shape(
        type="rect",
        x0=start_date,
        x1=end_date,
        y0=(row["low"]+row["high"])/2,   # 縦軸下限 = その日の安値
        y1=row["high"],  # 縦軸上限 = その日の高値
        line=dict(color="blue", width=1),
        fillcolor="blue",
        opacity=0.2,
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=start_date,
        x1=end_date,
        y0=row["low"],
        y1=(row["low"]+row["high"])/2,
        line=dict(color="orange", width=1),
        fillcolor="orange",
        opacity=0.2,
        layer="below"
    )


fig.update_layout(title="出来高", xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)


st.write(result)

