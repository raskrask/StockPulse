import streamlit as st
import pandas as pd
from application.trading_gym_usecase import TradingGymUsecase
from domain.model.trading_gym.trading_gym_models import TradingGymState, WINDOW_DAYS, MAX_ROUNDS
from ui.streamlit.components.trading_gym import (
    make_candlestick,
    make_result_candlestick,
    render_scoreboard,
    render_result_feedback,
)

usecase = TradingGymUsecase()


@st.cache_data
def get_universe():
    return usecase.get_universe()

# =========================
# セッション初期化
# =========================
if "trading_gym_state" not in st.session_state:
    st.session_state.trading_gym_state = TradingGymState().to_dict()

state = TradingGymState.from_dict(st.session_state.trading_gym_state)

# =========================
# 出題生成
# =========================
universe = get_universe()

# =========================
# 新しい問題を用意
# =========================
if state.current_question is None:
    state.current_question = usecase.generate_question(universe)
    state.current_round = 1


def next_chart():
    usecase.next_question(state, universe)
    st.session_state.trading_gym_state = state.to_dict()

show_continuation = False
feedback_action = None
feedback_score = 0.0
feedback_multiplier = 1

if state.show_result and state.action == "buy" and state.score > 0 and state.current_round < MAX_ROUNDS:
    feedback_action = state.action
    feedback_score = state.score
    feedback_multiplier = state.multiplier
    usecase.advance_round(state, universe)
    st.session_state.trading_gym_state = state.to_dict()
    show_continuation = True

q = state.current_question
df = q["df"]
idx = q["idx"]
symbol = q["symbol"]
name = q["name"]
round_data = usecase.get_round_data(df, idx, state.current_round)
entry_points = []
for round_index in range(1, state.current_round + 1):
    round_snapshot = usecase.get_round_data(df, idx, round_index)
    entry_points.append(
        {
            "date": round_snapshot.entry_date,
            "price": round_snapshot.entry_price,
            "label": f"Entry {round_index}",
        }
    )

# =========================
# 判定用データ
# =========================
entry_price = round_data.entry_price
entry_date = round_data.entry_date

# =========================
# 表示
# =========================
st.set_page_config(page_title="Trading Gym", layout="wide")
st.title("🏋️ Trading Gym")
st.caption(f"{symbol} / {name}")

render_scoreboard(
    state.gym_score,
    state.gym_count,
    state.current_round,
    MAX_ROUNDS,
)

display_result = state.show_result and not show_continuation

if display_result:
    window = usecase.get_window(df, idx, round_data.entry_idx, show_result=True)
    fig = make_result_candlestick(
        window,
        entry_date,
        entry_price,
        f"Result: {symbol} / {entry_date}",
        entry_points=entry_points,
        future_days=WINDOW_DAYS if state.current_round > 1 else 0,
    )
else:
    window = usecase.get_window(df, idx, round_data.entry_idx, show_result=False)
    fig = make_candlestick(window, f"{symbol} / {entry_date}", WINDOW_DAYS, entry_points=entry_points)

st.plotly_chart(fig, use_container_width=True)


# =========================
# 操作ボタン
# =========================

if display_result:
    render_result_feedback(state.action, state.score, state.multiplier)
    st.button("▶ 次のチャートへ", on_click=next_chart)
elif show_continuation:
    render_result_feedback(feedback_action, feedback_score, feedback_multiplier)

if not display_result:
    col1, col2 = st.columns(2)
    buy_label = "✅ 買う" if state.current_round == 1 else f"✅ 買う x{round_data.multiplier}"
    skip_label = "⏭ スルー" if state.current_round == 1 else "💰 利確"
    if col1.button(buy_label, use_container_width=True):
        usecase.apply_action(
            state=state,
            action="buy",
            round_data=round_data,
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
        )
        st.session_state.trading_gym_state = state.to_dict()
        st.rerun()

    if col2.button(skip_label, use_container_width=True):
        usecase.apply_action(
            state=state,
            action="skip",
            round_data=round_data,
            symbol=symbol,
            entry_date=entry_date,
            entry_price=entry_price,
        )
        st.session_state.trading_gym_state = state.to_dict()
        st.rerun()

# =========================
# デバッグ / ログ表示（任意）
# =========================
with st.expander("📄 History (debug)"):
    if state.gym_history:
        st.dataframe(pd.DataFrame(state.gym_history))
    else:
        st.write("No history yet.")

st.session_state.trading_gym_state = state.to_dict()
