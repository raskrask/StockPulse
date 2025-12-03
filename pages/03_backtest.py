import streamlit as st
from ui import screening_filters, backtest_results
from controller.backtest_controller import BacktestController

st.sidebar.title("バックテスト条件")

st.sidebar.caption(
    "条件を設定し、バックテストを実行します。該当する銘柄リストが表示されます。"
)
filters = screening_filters()

if st.sidebar.button("バックテストを実行"):
    st.success("バックテストが実行されました。")

    progress_container = st.empty()
    results = BacktestController().execute_backtest(params=filters, progress_container=progress_container)
    if results:
        backtest_results(results)