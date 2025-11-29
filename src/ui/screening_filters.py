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
    filters["price_change_20d_ago"] = st.sidebar.slider(
        "株価騰落率(%)[20日間前]",
        min_value=-50,
        max_value=50,
        value=(-5, 5),
        step=1,
    )
    filters["sma_25_divergence"] = st.sidebar.slider(
        "25日移動平均線乖離率(%)",
        min_value=-50,
        max_value=50,
        value=(-5, 5),
        step=1,
    )
    filters["ytd_high_divergence"] = st.sidebar.slider(
        "年初来高値からの下落率(%)",
        min_value=-50,
        max_value=0,
        value=(-20, -5),
        step=1,
    )
    filters["ytd_low_divergence"] = st.sidebar.slider(
        "年初来安値からの上昇率(%)",
        min_value=0,
        max_value=9999,
        value=(25, 9999),
        step=1,
    )

    return filters