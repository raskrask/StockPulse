import streamlit as st
from ui.streamlit.components import render_sidemenu

render_sidemenu(current="10_strategy_profiles")

st.set_page_config(page_title="Strategy Profiles", layout="wide")
st.title("Strategy Profiles")
st.info("損切り・利確・保有期間のバックテスト戦略の定義ページは準備中です。")
