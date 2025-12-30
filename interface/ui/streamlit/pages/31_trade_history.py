import streamlit as st
from ui.streamlit.components import render_sidemenu

render_sidemenu(current="31_trade_history")

st.set_page_config(page_title="Trade History", layout="wide")
st.title("Trade History")
st.info("確定した売買履歴の一覧ページは準備中です。")
