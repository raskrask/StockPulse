import streamlit as st
from domain.service.progress.progress_reporter import ProgressReporter


class StreamlitProgressReporter(ProgressReporter):
    def __init__(self):
        self.bar = st.progress(0.0)

    def report(self, progress, text: str =""):
        self.bar.progress(progress, text=text)
