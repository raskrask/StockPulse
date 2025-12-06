import streamlit as st
from ui.streamlit.components import screening_filters, backtest_results, StreamlitProgressReporter
from application.screening_usecase import ScreeningUsecase
from application.backtest_usecase import BacktestUsecase

st.sidebar.title("バックテスト条件")

st.sidebar.caption(
    "条件を設定し、バックテストを実行します。該当する銘柄リストが表示されます。"
)
filters = screening_filters(st.sidebar)

if st.sidebar.button("バックテストを実行"):
    st.success("バックテストが実行されました。")

    progress_reporter = StreamlitProgressReporter()
    results = BacktestUsecase(progress=progress_reporter).execute_backtest(params=filters)
    if results:
        backtest_results(results)