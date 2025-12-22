import streamlit as st

DEFAULT_PARAMS ={
    "sma_75_200_divergence": (-5, 5),
    "sma_25_divergence": (-5, 5),
    "ytd_high_divergence": (-20, -5),
    "ytd_low_divergence": (25, 9999),
    "ichimoku_3yakukoten": False, 
    "high_breakout": (-1, -1),
    "RSI": (40, 60),
    "price_change_20d_ago": (-5, 5),
    "double_bottom_signal": False,
    "ueno_theory_signal": False,
    "marketCap": (50000, 60000000),
    "avgTradingValue": (500000, 600000000),
}

def screening_filters(component):

    tab_trend, tab_momentum, tab_volatility, tab_fundamental = component.tabs(["Trend", "Momentum", "Volatility", "Fundamental"])

    filters = {}

    # --- tab_trend
    filters["sma_75_200_divergence"] = tab_trend.slider(
        "75/200日移動平均線乖離率(%)", key="sma_75_200_divergence", value=DEFAULT_PARAMS["sma_75_200_divergence"],
        min_value=-50, max_value=50, step=1,
    )
    filters["sma_25_divergence"] = tab_trend.slider(
        "25日移動平均線乖離率(%)", key="sma_25_divergence", value=DEFAULT_PARAMS["sma_25_divergence"],
        min_value=-50, max_value=50, step=1,
    )
    filters["ytd_high_divergence"] = tab_trend.slider(
        "年初来高値からの下落率(%)", key="ytd_high_divergence", value=DEFAULT_PARAMS["ytd_high_divergence"],
        min_value=-50, max_value=0, step=1,
    )
    filters["ytd_low_divergence"] = tab_trend.slider(
        "年初来安値からの上昇率(%)", key="ytd_low_divergence", value=DEFAULT_PARAMS["ytd_low_divergence"],
        min_value=0, max_value=9999, step=1,
    )
    filters["ichimoku_3yakukoten"] = tab_trend.checkbox(
        "一目均衡表 三役好転シグナル", key="ichimoku_3yakukoten", value=DEFAULT_PARAMS["ichimoku_3yakukoten"], 
    )


    # --- tab_momentum
    filters["high_breakout"] = tab_momentum.slider(
        "高値ブレイクアウトが発生", key="high_breakout", value=DEFAULT_PARAMS["high_breakout"], 
        min_value=-1, max_value=75, step=1,
        help="直近75日を除いた過去100日間の高値を、N日以内に高値がブレイクアウト"
    )
    filters["rsi"] = tab_momentum.slider(
        "RSI", key="RSI", value=DEFAULT_PARAMS["RSI"], 
        min_value=0, max_value=100, step=10,
    )
    filters["price_change_20d_ago"] = tab_momentum.slider(
        "株価騰落率(%)[20日間前]", key="price_change_20d_ago", value=DEFAULT_PARAMS["price_change_20d_ago"],
        min_value=-50, max_value=50, step=1,
    )
    filters["double_bottom_signal"] = tab_momentum.checkbox(
        "ダブルボトムシグナル", key="double_bottom_signal", value=DEFAULT_PARAMS["double_bottom_signal"], 
    )
    filters["ueno_theory_signal"] = tab_momentum.checkbox(
        "上野理論シグナル", key="ueno_theory_signal", value=DEFAULT_PARAMS["ueno_theory_signal"], 
    )

    # --- tab_fundamental
    filters["stockNumbers"] = tab_fundamental.text_input("銘柄コード", key="stockNumbers")
    filters["marketCap"] = tab_fundamental.slider(
        "時価総額（百万円）", key="marketCap", value=DEFAULT_PARAMS["marketCap"], 
        min_value=0, max_value=60000000, step=10,
    )
    filters["avgTradingValue"] = tab_fundamental.slider(
        "平均売買価格[20日間]（千円）", key="avgTradingValue", value=DEFAULT_PARAMS["avgTradingValue"], 
        min_value=0, max_value=600000000, step=10000,
    )

    return filters


def set_screening_params(params):
    new_params = DEFAULT_PARAMS | params 
    st.session_state.stockNumbers = new_params.get("stockNumbers","")
    st.session_state.sma_75_200_divergence = new_params.get("sma_75_200_divergence")
    st.session_state.sma_25_divergence = new_params.get("sma_25_divergence")
    st.session_state.ytd_high_divergence = new_params.get("ytd_high_divergence")
    st.session_state.ytd_low_divergence = new_params.get("ytd_low_divergence")
    st.session_state.ichimoku_3yakukoten = new_params.get("ichimoku_3yakukoten")
    st.session_state.high_breakout = new_params.get("high_breakout")
    st.session_state.RSI = new_params.get("RSI")
    st.session_state.price_change_20d_ago = new_params.get("price_change_20d_ago")
    st.session_state.double_bottom_signal = new_params.get("double_bottom_signal")
    st.session_state.ueno_theory_signal = new_params.get("ueno_theory_signal")
    st.session_state.marketCap = new_params.get("marketCap")
    st.session_state.avgTradingValue = new_params.get("avgTradingValue")
