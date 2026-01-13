import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from domain.repository.stock_repository import StockRepository

@st.cache_data
def get_universe():
    return StockRepository().list_all_stocks()

def load_daily(record) -> pd.DataFrame:
    """
    必須カラム:
      index: DatetimeIndex
      open, high, low, close, volume
    """
    df = record.get_daily_chart_by_days(365*3)

    # ===== 日付を datetime に =====
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # ===== 移動平均 =====
    df["ma5"]  = df["close"].rolling(5).mean()
    df["ma25"] = df["close"].rolling(25).mean()
    df["ma75"] = df["close"].rolling(75).mean()

    return df

# =========================
# チャート描画
# =========================
def make_candlestick(df: pd.DataFrame, title: str):
    fig = go.Figure()

    df = df.copy()

    last_date = df["date"].iloc[-1]
    future_index = pd.date_range(
        start=last_date + pd.offsets.BDay(1),
        periods=21,
        freq="B"
    )

    dummy = pd.DataFrame(index=future_index, columns=df.columns)

    # ===== index を date に =====
    df = df.set_index("date")
    df = pd.concat([df, dummy])

    # ===== ローソク =====
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    # ===== 移動平均線 =====
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ma5"],
        mode="lines",
        name="MA 5",
        line=dict(width=1)
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ma25"],
        mode="lines",
        name="MA 25",
        line=dict(width=1.5)
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ma75"],
        mode="lines",
        name="MA 75",
        line=dict(width=2)
    ))

    # ===== 出来高 =====
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        name="Volume",
        yaxis="y2",
        opacity=0.3
    ))

    # ===== レイアウト =====
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        yaxis=dict(title="Price"),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def make_result_candlestick(df, entry_idx, entry_price, title):
    fig = go.Figure()
    entry_date = df["date"].iloc[-21-1]
    df = df.set_index("date")

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    # エントリーポイント
    fig.add_trace(go.Scatter(
        x=[entry_date],
        y=[entry_price],
        mode="markers",
        marker=dict(
            size=12,
            color="blue",
            symbol="triangle-up"
        ),
        name="Entry"
    ))

    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        height=500
    )

    return fig

# =========================
# セッション初期化
# =========================
if "gym_score" not in st.session_state:
    st.session_state.gym_score = 0.0
    st.session_state.gym_count = 0
    st.session_state.gym_history = []
    st.session_state.current_question = None
    st.session_state.show_result = False

# =========================
# 出題生成
# =========================
def generate_question():
    universe = get_universe()

    while True:
        stock = random.choice(universe)
        df = load_daily(stock)

        if len(df) < 200:
            continue

        # 90日表示 + 20日先で判定
        idx = random.randint(0, len(df) - 90 - 21)

        return {
            "symbol": stock.symbol,
            "df": df,
            "idx": idx,
            "date": df["date"].iloc[idx]
        }

# =========================
# 新しい問題を用意
# =========================
if st.session_state.current_question is None:
    st.session_state.current_question = generate_question()

q = st.session_state.current_question
df = q["df"]
idx = q["idx"]
symbol = q["symbol"]

# =========================
# 判定用データ
# =========================
entry_price = df.iloc[idx]["close"] 
future = df.iloc[idx+1:idx+21]

max_ret = (future["close"].max() - entry_price) / entry_price
min_ret = (future["close"].min() - entry_price) / entry_price
score = max_ret if max_ret > abs(min_ret) else min_ret
score = round(score * 100, 2)  # パーセンテージ表示

# =========================
# 表示
# =========================
st.set_page_config(page_title="Trading Gym", layout="wide")
st.title("🏋️ Trading Gym")

st.markdown(
    f"""
**Score:** `{st.session_state.gym_score:.1f}`  
**Plays:** `{st.session_state.gym_count}`  
"""
)

if st.session_state.show_result :
    window = df.iloc[idx-90:idx+21]
    fig = make_result_candlestick(window, idx, entry_price, f"Result: {symbol} / {q['date']}")
else:
    window = df.iloc[idx-90:idx]
    fig = make_candlestick(window, f"{symbol} / {q['date']}")

st.plotly_chart(fig, use_container_width=True)


# =========================
# ログ保存
# =========================
def save_log(decision: str, score: float):
    log = {
        "timestamp": datetime.now(),
        "symbol": symbol,
        "date": q["date"],
        "decision": decision,
        "entry_price": entry_price,
        "max": future["close"].max() ,
        "min": future["close"].min() ,
        "max_return_20d": max_ret,
        "min_return_20d": min_ret,
        "score": score
    }
    st.session_state.gym_history.append(log)

# =========================
# 操作ボタン
# =========================

if st.session_state.show_result :
    # ===== 視覚フィードバック ===
    if st.session_state.action == "buy":
        if st.session_state.score > 0:
            st.success(f"🎉 勝ち！ +{st.session_state.score}%")
        else:
            st.error(f"💀 負け… {st.session_state.score}%")
    else:
        if st.session_state.score > 0:
            st.error(f"💸 見逃し… {st.session_state.score}%")
        else:
            st.success(f"🚩 セーフ +{st.session_state.score}%")
    
    if st.button("▶ 次のチャートへ"):
        st.session_state.current_question = generate_question()
        st.session_state.show_result = False
        st.rerun()
else:
    col1, col2 = st.columns(2)
    if col1.button("✅ 買う", use_container_width=True):
        st.session_state.score = score
        st.session_state.gym_score += st.session_state.score
        st.session_state.gym_count += 1
        st.session_state.show_result = True
        st.session_state.action = "buy"
        save_log("buy", st.session_state.score)
        st.rerun()

    if col2.button("⏭ スルー", use_container_width=True):
        st.session_state.score = score
        st.session_state.gym_score -= st.session_state.score
        st.session_state.gym_count += 1
        st.session_state.show_result = True
        st.session_state.action = "skip"
        save_log("skip", 0.0)
        st.rerun()

# =========================
# デバッグ / ログ表示（任意）
# =========================
with st.expander("📄 History (debug)"):
    if st.session_state.gym_history:
        st.dataframe(pd.DataFrame(st.session_state.gym_history))
    else:
        st.write("No history yet.")
