import streamlit as st
import pandas as pd
from ui.streamlit.components import screening_filters, StreamlitProgressReporter
from application.screening_usecase import ScreeningUsecase

st.sidebar.title("スクリーニング条件")

st.sidebar.caption(
    "条件を設定し、スクリーニングを実行します。該当する銘柄リストが表示されます。"
)

filters = screening_filters()

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")

    progress_reporter = StreamlitProgressReporter()
    screen_stocks = ScreeningUsecase(progress=progress_reporter).screen_stocks(params=filters)
    if screen_stocks:
        symbols = " ".join(s['symbol'] for s in screen_stocks)
        st.markdown(f"検索結果({len(screen_stocks)})件：`{symbols}`")
        df = pd.DataFrame(screen_stocks).set_index('symbol')
        st.write(screen_stocks)