import streamlit as st

def screening_filters():
    st.sidebar.title("スクリーニング条件")

    st.sidebar.caption(
        "条件を設定し、スクリーニングを実行します。該当する銘柄リストが表示されます。"
    )

    filters = {}
    filters["marketCap"] = st.sidebar.slider(
        "時価総額（百万円）",
        min_value=0,
        max_value=60000000,
        value=(50000, 60000000),
        step=10,
    )

    filters["avgTradingValue"] = st.sidebar.slider(
        "平均出来高[20日間]（千円）",
        min_value=0,
        max_value=600000000,
        value=(500000, 600000000),
        step=10000,
    )

    filters["rsi"] = st.sidebar.slider(
        "RSI",
        min_value=0,
        max_value=100,
        value=(40, 60),
        step=10,
    )
    return filters