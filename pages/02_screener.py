import streamlit as st
from ui import screening_filters
from controller.screening_controller import ScreeningController

filters = screening_filters()

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")
    # ここにスクリーニングロジックを実装し、結果を表示するコードを追加します。
    ###

    screen_stocks = ScreeningController().screen_stocks(filters=filters)
    st.write(screen_stocks)