import streamlit as st

DEFAULT_PARAMS ={
    "ichimoku_3yakukoten": False, 
    "double_bottom_signal": False,
    "ueno_theory_signal": False,
    "marketCap": (50000, 60000000),
    "avgTradingValue": (500000, 600000000),
    "RSI": (40, 60),
    "price_change_20d_ago": (-5, 5),
    "sma_25_divergence": (-5, 5),
    "ytd_high_divergence": (-20, -5),
    "ytd_low_divergence": (25, 9999),
}

def screening_filters(component):

    filters = {}
    filters["stockNumbers"] = component.text_input("銘柄コード", key="stockNumbers")


    filters["ichimoku_3yakukoten"] = component.checkbox(
        "一目均衡表 三役好転シグナル", key="ichimoku_3yakukoten", value=DEFAULT_PARAMS["ichimoku_3yakukoten"], 
    )
    filters["double_bottom_signal"] = component.checkbox(
        "ダブルボトムシグナル", key="double_bottom_signal", value=DEFAULT_PARAMS["double_bottom_signal"], 
    )
    filters["ueno_theory_signal"] = component.checkbox(
        "上野理論シグナル", key="ueno_theory_signal", value=DEFAULT_PARAMS["ueno_theory_signal"], 
    )

    filters["marketCap"] = component.slider(
        "時価総額（百万円）", key="marketCap", value=DEFAULT_PARAMS["marketCap"], 
        min_value=0, max_value=60000000, step=10,
    )

    filters["avgTradingValue"] = component.slider(
        "平均出来高[20日間]（千円）", key="avgTradingValue", value=DEFAULT_PARAMS["avgTradingValue"], 
        min_value=0, max_value=600000000, step=10000,
    )

    filters["rsi"] = component.slider(
        "RSI", key="RSI", value=DEFAULT_PARAMS["RSI"], 
        min_value=0, max_value=100, step=10,
    )

    filters["price_change_20d_ago"] = component.slider(
        "株価騰落率(%)[20日間前]", key="price_change_20d_ago", value=DEFAULT_PARAMS["price_change_20d_ago"],
        min_value=-50, max_value=50, step=1,
    )

    filters["sma_25_divergence"] = component.slider(
        "25日移動平均線乖離率(%)", key="sma_25_divergence", value=DEFAULT_PARAMS["sma_25_divergence"],
        min_value=-50, max_value=50, step=1,
    )

    filters["ytd_high_divergence"] = component.slider(
        "年初来高値からの下落率(%)", key="sma_25_divytd_high_divergenceergence", value=DEFAULT_PARAMS["ytd_high_divergence"],
        min_value=-50, max_value=0, step=1,
    )

    filters["ytd_low_divergence"] = component.slider(
        "年初来安値からの上昇率(%)", key="ytd_low_divergence", value=DEFAULT_PARAMS["ytd_low_divergence"],
        min_value=0, max_value=9999, step=1,
    )

    return filters


def set_screening_params(params):
    new_params = DEFAULT_PARAMS | params 
    st.session_state.stockNumbers = new_params.get("stockNumbers","")
    st.session_state.ichimoku_3yakukoten = new_params.get("ichimoku_3yakukoten")
    st.session_state.double_bottom_signal = new_params.get("double_bottom_signal")
    st.session_state.ueno_theory_signal = new_params.get("ueno_theory_signal")
    st.session_state.marketCap = new_params.get("marketCap")
    st.session_state.avgTradingValue = new_params.get("avgTradingValue")
    st.session_state.RSI = new_params.get("RSI")
    st.session_state.price_change_20d_ago = new_params.get("price_change_20d_ago")
    st.session_state.sma_25_divergence = new_params.get("sma_25_divergence")
    st.session_state.ytd_high_divergence = new_params.get("ytd_high_divergence")
    st.session_state.ytd_low_divergence = new_params.get("ytd_low_divergence")

