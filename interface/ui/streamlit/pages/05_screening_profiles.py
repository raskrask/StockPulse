import streamlit as st
from ui.streamlit.components import screening_filters, set_screening_params, StreamlitProgressReporter
from application.screening_profile_usecase import ScreeningProfileUsecase

st.title("🔔 スクリーニング条件の保存")

service = ScreeningProfileUsecase()
profiles = service.list_profiles()
selected = st.selectbox("プロファイルを選択", ["<新規>"] + profiles)

data = {"filters": {}, "notify": True, "memo": ""}
if st.button("プロファイル読込み"):
    if selected != "<新規>":
        data = service.load_profile(selected)
        profiles = service.list_profiles()
    set_screening_params(data["filters"])

# --- 編集フォーム ---
data["name"] = st.text_input("プロファイル名", value="" if selected == "<新規>" else selected)
data["notify"] = st.checkbox("通知を有効にする", value=data.get("notify", True))
data["memo"]   = st.text_area("メモ", value=data.get("memo", ""))

st.write("---")
st.subheader("条件設定")
data["filters"] = screening_filters(st)

# 保存
if st.button("保存する"):
    if data["name"]:
        service.save_profile(data["name"], data)
        st.success(f"{data['name']} を保存しました！")
    else:
        st.error("プロファイル名を入力してください。")
