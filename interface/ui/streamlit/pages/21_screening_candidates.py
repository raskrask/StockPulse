import streamlit as st
from streamlit.column_config import LinkColumn
import pandas as pd
from ui.streamlit.components import screening_filters, set_screening_params, render_sidemenu, StreamlitProgressReporter
from application.screening_usecase import ScreeningUsecase
from application.screening_profile_usecase import ScreeningProfileUsecase

st.sidebar.title("スクリーニング条件")

st.sidebar.caption(
    "条件を設定し、スクリーニングを実行します。該当する銘柄リストが表示されます。"
)

service = ScreeningProfileUsecase()
profiles = service.list_profiles()

selected = st.sidebar.selectbox("プロファイルを選択", [""] + profiles)
if st.sidebar.button("読込"):
    data = service.load_profile(selected)
    set_screening_params(data["filters"])

filters = screening_filters(st.sidebar)

if st.sidebar.button("スクリーニングを実行"):
    st.success("スクリーニングが実行されました。該当する銘柄リストを表示します。")

    progress_reporter = StreamlitProgressReporter()
    screen_stocks = ScreeningUsecase(progress=progress_reporter).screen_stocks(params=filters)
    if screen_stocks:
        symbols = " ".join(s['symbol'] for s in screen_stocks)
        st.markdown(f"検索結果({len(screen_stocks)})件：`{symbols}`")
        df = pd.DataFrame(screen_stocks).set_index('symbol', drop=False)
        df["symbol_url"] = df["symbol"].apply(
            lambda x: f"insight?symbol={x}"
        )
        column_config = {
            "symbol_url": LinkColumn(
                label="銘柄詳細",
                display_text="銘柄を見る"
            )
        }
        st.dataframe( df, column_config=column_config )
        st.write(screen_stocks)

st.sidebar.write("---")
render_sidemenu(current="21_screening_candidates")
