# lib/ui/components.py
import streamlit as st
import plotly.graph_objects as go


def market_card(title: str, value: float, trend: str, delta: float, comment: str, df):
    st.metric(
        label=title,
        value=value,
        delta=f"{delta:.2f}%",
    )
    st.caption(comment)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["date"], y=df["close"], mode="lines", name="close"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema20"], mode="lines", name="ema20"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema50"], mode="lines", name="ema50"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ema200"], mode="lines", name="ema200"))

    # レイアウト調整
    fig.update_layout(
        height=250,  # 高さを下げる
        yaxis=dict(
            range=[df["close"].min() * 0.95, df["close"].max() * 1.05]
        ),  # y軸範囲
        margin=dict(l=10, r=10, t=20, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def metric_card(title: str, value: str, delta: str, trend: str):
    """
    Streamlit用のシンプルなカードUIコンポーネント
    """
    color = "green" if "Up" in trend else "red" if "Down" in trend else "gray"

    st.markdown(
        f"""
        <div style="
            background-color:#f9f9f9;
            padding:15px;
            border-radius:12px;
            border-left: 6px solid {color};
            box-shadow:2px 2px 6px rgba(0,0,0,0.1);
            margin-bottom:10px;
        ">
            <h4 style="margin:0;">{title}</h4>
            <p style="font-size:24px;margin:5px 0;font-weight:bold;">{value}</p>
            <p style="margin:0;color:{color};">{trend} ({delta})</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
