import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from ui.streamlit.components import render_sidemenu
from infrastructure.yahoo.yf_fetcher import fetch_yf_daily_by_month, fetch_yf_weekly, fetch_yf_monthly, fetch_yf_info
from infrastructure.jpx.jpx_fetcher import JPXListingFetcher
from infrastructure.persistence.indicator_cache import load_cached_indicator_df
from domain.repository.stock_repository import StockRepository

render_sidemenu(current="22_stock_insight")

st.set_page_config(page_title="Stock Insight", layout="wide")
st.title("🔍 銘柄詳細 - Stock Insight")

params = st.query_params

symbol = st.text_input("銘柄コードを入力 (例: 7203.T)", params.get("symbol", "7203.T"))

repo = StockRepository()
record = repo.get_stock_by_symbol(symbol)

if record is None:
    st.error("指定した銘柄が見つかりませんでした。")
    st.stop()

st.write("銘柄名:", record.name)
st.write("市場:", record.market)
st.write("業種:", record.get_industry())
st.write("規模:", record.get_scale())

start = datetime.today() - timedelta(days=365)
info = record.get_stock_info()
st.write("時価総額", "{:,}".format(info['marketCap']))
st.write("初回取引日時", pd.to_datetime(info['firstTradeDateMilliseconds'], unit="ms"))

st.write("PER", info['trailingPE'])
st.write("PBR", info['priceToBook'])

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
df_daily = fetch_yf_cache("daily", record.symbol, start)

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

candle = go.Candlestick(x=df_daily["date"], open=df_daily["open"], high=df_daily["high"], low=df_daily["low"], close=df_daily["close"], name="ローソク足")
bar = go.Bar(x=df_daily["date"], y=df_daily["volume"], name="出来高")

fig.add_trace(candle, row=1, col=1)
fig.add_trace(bar, row=2, col=1)
fig.update_layout(title="日足", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)


# 週足
df_weekly = fetch_yf_cache("weekly", record.symbol, start)
st.subheader("週足")
st.write(df_weekly.tail())
st.line_chart(df_weekly.set_index("date")["close"])

# 月足
df_monthly = fetch_yf_cache("monthly", record.symbol, start)
st.subheader("月足")
st.write(df_monthly.tail())
st.line_chart(df_monthly.set_index("date")["close"])

st.write("====== テスト用 ======")
from domain.model.analysis.technical.ueno_theory import UenoTheory

ueno_theory = UenoTheory()
df = record.get_daily_chart_by_days(ueno_theory.window_size+20)
df = ueno_theory.add_ueno_theory_signal(df)

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

st.write("---")
st.subheader("📰 関連ニュース")

try:
    from infrastructure.google.google_news_fetcher import fetch_google_news_rss
    
    # Use stock name for searching
    search_query = f"{record.name}"
    news_items = fetch_google_news_rss(search_query)

    if not news_items:
        st.info("関連ニュースが見つかりませんでした。")
    else:
        # Create 2 columns for card layout
        n_cols = 2
        cols = st.columns(n_cols)
        
        for i, item in enumerate(news_items):
            col = cols[i % n_cols]
            with col:
                # Using HTML for card styling
                st.markdown(f"""
                <div style="border: 1px solid #bbb; padding: 15px; border-radius: 8px; margin-bottom: 20px; height: 100%;">
                    <h5 style="margin-bottom: 5px; font-size: 16px;"><a href="{item['link']}" target="_blank" style="text-decoration: none;">{item['title']}</a></h5>
                    <div style="font-size: 12px; color: gray; margin-bottom: 10px;">{item['published']} | {item['source']}</div>
                    <div style="font-size: 13px; line-height: 1.4; margin-bottom: 10px;">{item['summary']}</div>
                    <a href="{item['link']}" target="_blank" style="
                        display: inline-block; 
                        padding: 5px 12px; 
                        background-color: #4CAF50; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        font-size: 12px;">元記事へ</a>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"ニュースの取得に失敗しました: {e}")



st.write(df)

df_indicator = load_cached_indicator_df(record.symbol)
if df_indicator is not None:
    st.write(df_indicator.tail())
