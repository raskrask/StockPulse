import streamlit as st
import pandas as pd

from ui.streamlit.components import render_sidemenu
from infrastructure.persistence.backtest_result import list_backtest_profiles, load_backtest_summary

render_sidemenu(current="12_backtest_results")

st.set_page_config(page_title="Backtest Review", layout="wide")
st.title("バックテスト評価")

profiles = list_backtest_profiles()
if not profiles:
    st.info("保存済みのバックテスト結果がありません。")
    st.stop()

rows = []
for name in profiles:
    summary = load_backtest_summary(name)
    if summary:
        rows.append(summary)

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)
