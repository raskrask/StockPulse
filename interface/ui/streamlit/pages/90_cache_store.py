import streamlit as st
from datetime import datetime
from ui.streamlit.components import StreamlitProgressReporter
from application.cache_store_usecase import CacheStoreUsecase

#from infrastructure.cache.cache_store import LocalCacheStore, S3CacheStore
#from infrastructure.persistence.cache_service import CacheService#, month_range, make_key, CacheConfig

st.set_page_config(page_title="Cache Admin", layout="wide")
st.title("Cache（取得状況 / リセット）")

progress_reporter = StreamlitProgressReporter()
app = CacheStoreUsecase(progress_reporter)

tab_status, tab_reset = st.tabs(["取得状況", "リセット"])

with tab_status:
    st.subheader("キャッシュ取得状況")

    stats = app.get_cache_stats()

    st.markdown("#### キャッシュ統計情報")
    st.dataframe([stats], use_container_width=True)

with tab_reset:
    st.subheader("キャッシュリセット（削除）")
    st.warning("削除は不可逆。まず dry-run で対象確認 → チェックを入れて実行、の流れ推奨。")

    # mode = st.radio("対象", ["daily（月指定）", "daily（期間一括）", "weekly", "monthly", "symbol配下すべて"], horizontal=True)
    # dry_run = st.checkbox("dry-run（削除せず対象だけ表示）", value=True)
    # confirm = st.checkbox("本当に実行する（チェック必須）", value=False)

    # keys = []
    # if mode == "daily（月指定）":
    #     ym = st.text_input("month (YYYY-MM)", value="2025-09")
    #     keys = [make_key(CacheConfig(MARKET, SYMBOL, "daily", month=ym))]

    # elif mode == "daily（期間一括）":
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         fym = st.text_input("from (YYYY-MM)", value="2025-01", key="reset_from")
    #     with col2:
    #         tym = st.text_input("to (YYYY-MM)", value="2025-06", key="reset_to")
    #     keys = [make_key(CacheConfig(MARKET, SYMBOL, "daily", month=ym)) for ym in month_range(fym, tym)]

    # elif mode == "weekly":
    #     keys = [make_key(CacheConfig(MARKET, SYMBOL, "weekly"))]

    # elif mode == "monthly":
    #     keys = [make_key(CacheConfig(MARKET, SYMBOL, "monthly"))]

    # elif mode == "symbol配下すべて":
    #     if st.checkbox("危険：symbol配下を全削除する", value=False):
    #         keys = svc.list_symbol_all(SYMBOL)

    # st.markdown("#### 対象キー")
    # st.code("\n".join(keys) if keys else "(none)")

    # if st.button("実行"):
    #     if not keys:
    #         st.error("対象がありません")
    #     elif not dry_run and not confirm:
    #         st.error("本削除するなら「本当に実行する」にチェックが必要です")
    #     else:
    #         deleted = app.delete_keys(keys, dry_run=dry_run)
    #         if dry_run:
    #             st.success(f"dry-run: {len(deleted)} 件が対象です")
    #         else:
    #             st.success(f"deleted: {len(deleted)} 件削除しました")
