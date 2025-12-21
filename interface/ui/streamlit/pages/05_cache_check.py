import streamlit as st
from pathlib import Path
import humanize

st.title("Cache チェック — 初期フェーズ")

CACHE_DIR = Path("cache")

def scan_cache(path: Path):
    if not path.exists():
        return {}, 0
    per_symbol = {}
    total_files = 0
    total_size = 0
    for child in sorted(path.iterdir()):
        if child.is_dir():
            files = list(child.rglob("*.*"))
            cnt = len(files)
            size = sum(f.stat().st_size for f in files if f.exists())
            per_symbol[child.name] = {"count": cnt, "size": size}
            total_files += cnt
            total_size += size
    return per_symbol, {"total_files": total_files, "total_size": total_size}

st.sidebar.markdown("## 操作")
if st.sidebar.button("再スキャン"):
    st.experimental_rerun()

st.markdown("### 概要")
per_symbol, totals = scan_cache(CACHE_DIR)
st.metric("総ファイル数", totals["total_files"]) if totals else st.write("キャッシュ無し")
st.write("総サイズ: ", humanize.naturalsize(totals["total_size"]))

st.markdown("---")
st.markdown("### シンボル別サマリ")
if not per_symbol:
    st.info("cache フォルダが存在しないか、キャッシュがありません。")
else:
    for sym, meta in sorted(per_symbol.items(), key=lambda x: x[0]):
        with st.expander(f"{sym} — {meta['count']} files, {humanize.naturalsize(meta['size'])}"):
            files = list((CACHE_DIR / sym).rglob("*.*"))
            st.write(f"合計 {len(files)} ファイル")
            # show up to 50 files
            for f in files[:50]:
                st.text(f.relative_to(CACHE_DIR))
            if len(files) > 50:
                st.write(f"... and {len(files)-50} more")

st.caption("初期フェーズ：削除や詳細操作は今後追加予定です")
