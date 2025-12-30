import streamlit as st
from ui.streamlit.components import screening_filters, set_screening_params, backtest_results, render_sidemenu, StreamlitProgressReporter
from application.screening_usecase import ScreeningUsecase
from application.backtest_usecase import BacktestUsecase
from application.screening_profile_usecase import ScreeningProfileUsecase

st.sidebar.title("バックテスト条件 - Backtest Runner")

st.sidebar.caption(
    "条件を設定し、バックテストを実行します。該当する銘柄リストが表示されます。"
)

service = ScreeningProfileUsecase()
profiles = service.list_profiles()

selected = st.sidebar.selectbox("プロファイルを選択", [""] + profiles)
if st.sidebar.button("読込"):
    data = service.load_profile(selected)
    set_screening_params(data["filters"])

filters = screening_filters(st.sidebar)

if st.sidebar.button("バックテストを実行"):
    st.success("バックテストが実行されました。")

    progress_reporter = StreamlitProgressReporter()
    profile_name = selected if selected else "custom"
    results = BacktestUsecase(progress=progress_reporter).execute_backtest(params=filters, profile_name=profile_name)
    if results:
        backtest_results(results)

st.sidebar.write("---")
render_sidemenu(current="11_backtest_runner")
