import streamlit as st
import pandas as pd
from ui import screening_filters
from controller.screening_controller import ScreeningController

filters = screening_filters()

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")

    progress_container = st.empty()
    screen_stocks = ScreeningController().screen_stocks(params=filters, progress_container=progress_container)
    if screen_stocks:
        symbols = " ".join(s['symbol'] for s in screen_stocks)
        st.markdown(f"検索結果({len(screen_stocks)})件：`{symbols}`")
        df = pd.DataFrame(screen_stocks).set_index('symbol')
        st.write(df)