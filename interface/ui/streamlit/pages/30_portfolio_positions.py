import streamlit as st
from ui.streamlit.components import render_sidemenu

render_sidemenu(current="30_portfolio_positions")

st.set_page_config(page_title="Portfolio – Positions", layout="wide")
st.title("Portfolio – Positions")
st.info("保有中銘柄の現在状況ページは準備中です。")
