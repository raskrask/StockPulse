import streamlit as st
from ui import screening_filters
from controller.screening_controller import ScreeningController

filters = screening_filters()

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")

    progress_container = st.empty()
    screen_stocks = ScreeningController().screen_stocks(params=filters, progress_container=progress_container)
    st.write(screen_stocks)