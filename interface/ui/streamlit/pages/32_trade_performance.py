import streamlit as st
import streamlit as st
from ui.streamlit.components import render_sidemenu

render_sidemenu(current="32_trade_performance")

st.set_page_config(page_title="Trade Performance", layout="wide")
st.title("Trade Performance")
st.info("実運用の成績集計・分析ページは準備中です。")
