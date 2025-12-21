import time
import streamlit as st
from domain.service.progress.progress_reporter import ProgressReporter


class StreamlitProgressReporter(ProgressReporter):
    def __init__(self):
        self.bar = st.progress(0.0)
        self._t_start = None
        self._t_last = None


    def report(self, progress, text: str =""):
        if self._t_start is None:
            self._t_start = time.perf_counter()

        if self._t_last is None and progress >= 100:
            self._t_last = time.perf_counter()

        now = time.perf_counter()
        elapsed = ((self._t_last or now) - self._t_start) / 60.0
        per_pct = ((elapsed / progress) if progress > 0 else 0)

        text += f" | [{elapsed:.1f} / {per_pct:.1f} min]"

        self.bar.progress(progress, text=text)
