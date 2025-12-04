import streamlit as st
import pandas as pd
from ui import screening_filters
from controller.screening_controller import ScreeningController

st.sidebar.title("スクリーニング条件")

st.sidebar.caption(
    "条件を設定し、スクリーニングを実行します。該当する銘柄リストが表示されます。"
)

filters = screening_filters()

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")

    progress_bar = st.progress(0.0, text="Ready")
    def progress_callback(p: float, text: str):
        progress_bar.progress(p, text=text)

    screen_stocks = ScreeningController().screen_stocks(params=filters, progress_callback=progress_callback)
    if screen_stocks:
        symbols = " ".join(s['symbol'] for s in screen_stocks)
        st.markdown(f"検索結果({len(screen_stocks)})件：`{symbols}`")
        df = pd.DataFrame(screen_stocks).set_index('symbol')
        st.write(screen_stocks)