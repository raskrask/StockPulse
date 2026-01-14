import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _add_entry_points(fig: go.Figure, entry_points: list | None):
    if not entry_points:
        return

    fig.add_trace(
        go.Scatter(
            x=[p["date"] for p in entry_points],
            y=[p["price"] for p in entry_points],
            mode="markers",
            marker=dict(size=10, color="blue", symbol="triangle-up"),
            name="Entry",
            text=[p.get("label", "") for p in entry_points],
            hovertemplate="%{text}<br>%{x}<br>%{y}<extra></extra>",
        )
    )


def make_candlestick(df: pd.DataFrame, title: str, future_days: int, entry_points: list | None = None):
    fig = go.Figure()

    df = df.copy()

    last_date = df["date"].iloc[-1]
    future_index = pd.date_range(
        start=last_date + pd.offsets.BDay(1),
        periods=future_days,
        freq="B",
    )

    dummy = pd.DataFrame(index=future_index, columns=df.columns)

    # ===== index を date に =====
    df = df.set_index("date")
    df = pd.concat([df, dummy])

    # ===== ローソク =====
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        )
    )

    # ===== 移動平均線 =====
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["ma5"],
            mode="lines",
            name="MA 5",
            line=dict(width=1),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["ma25"],
            mode="lines",
            name="MA 25",
            line=dict(width=1.5),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["ma75"],
            mode="lines",
            name="MA 75",
            line=dict(width=2),
        )
    )

    # ===== 出来高 =====
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["volume"],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
        )
    )

    # ===== レイアウト =====
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        yaxis=dict(title="Price"),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    _add_entry_points(fig, entry_points)

    return fig


def make_result_candlestick(
    df: pd.DataFrame,
    entry_date,
    entry_price: float,
    title: str,
    entry_points: list | None = None,
    future_days: int = 0,
):
    fig = go.Figure()
    df = df.copy()

    if future_days > 0:
        last_date = df["date"].iloc[-1]
        future_index = pd.date_range(
            start=last_date + pd.offsets.BDay(1),
            periods=future_days,
            freq="B",
        )
        dummy = pd.DataFrame(index=future_index, columns=df.columns)
        df = df.set_index("date")
        df = pd.concat([df, dummy])
    else:
        df = df.set_index("date")

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        )
    )

    if entry_points is None:
        entry_points = [{"date": entry_date, "price": entry_price, "label": "Entry"}]

    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        height=500,
    )

    _add_entry_points(fig, entry_points)

    return fig


def render_scoreboard(score: float, plays: int, round_index: int, max_rounds: int):
    st.markdown(
        f"""
**Score:** `{score:.1f}`  
**Plays:** `{plays}`  
**Round:** `{round_index} / {max_rounds}`
"""
    )


def render_result_feedback(action: str, score: float, multiplier: int):
    bonus_label = f"(x{multiplier})" if multiplier > 1 else ""

    if action == "buy":
        if score > 0:
            st.success(f"🎉 勝ち！ +{score}% {bonus_label}".strip())
        else:
            st.error(f"💀 負け… {score}% {bonus_label}".strip())
    else:
        if score > 0:
            st.error(f"💸 見逃し… {score}% {bonus_label}".strip())
        else:
            st.success(f"🚩 セーフ +{score}% {bonus_label}".strip())
