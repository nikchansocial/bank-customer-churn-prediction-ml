"""
Customer Churn Intelligence — Streamlit entry point.

Run from the repo root with:  streamlit run app/app.py
"""
import pathlib
import sys
import warnings

import streamlit as st

# make `lib` and `views` importable regardless of the working directory
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
warnings.filterwarnings("ignore", category=FutureWarning)

from lib import data  # noqa: E402  (after sys.path tweak)
from lib.theme import get_theme, inject_css  # noqa: E402
from views import batch, overview, scorer  # noqa: E402

st.set_page_config(page_title="Churn Intelligence", page_icon="◆", layout="wide")

# ---- theme toggle (persisted across pages) --------------------------------
if "dark" not in st.session_state:
    st.session_state["dark"] = True
with st.sidebar:
    st.markdown("### ◆ Churn Intelligence")
    choice = st.radio("Theme", ["🌙 Dark", "☀️ Light"], horizontal=True,
                      index=0 if st.session_state["dark"] else 1,
                      label_visibility="collapsed")
    st.session_state["dark"] = choice.startswith("🌙")

inject_css(get_theme())

# warm the caches once so page switches feel instant
data.get_model()

# ---- multipage navigation -------------------------------------------------
nav = st.navigation([
    st.Page(overview.render, title="Overview", icon=":material/dashboard:",
            url_path="overview", default=True),
    st.Page(scorer.render, title="Risk Scorer", icon=":material/person_search:",
            url_path="scorer"),
    st.Page(batch.render, title="Batch Scoring", icon=":material/upload_file:",
            url_path="batch"),
])
nav.run()
