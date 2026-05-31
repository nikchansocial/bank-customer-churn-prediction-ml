"""
Customer Churn Intelligence — Streamlit entry point.

Run from the repo root with:  streamlit run app/app.py
"""
import pathlib
import sys
import warnings

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
warnings.filterwarnings("ignore", category=FutureWarning)

from lib import data  # noqa: E402
from lib.theme import clean_css, get_theme, inject_css  # noqa: E402
from views import batch, overview, scorer  # noqa: E402

st.set_page_config(page_title="Churn Intelligence", page_icon="◆", layout="wide")

T = get_theme()
inject_css(T)

# clean-view (screenshot) mode — hides sidebar/chrome
st.session_state.setdefault("clean", False)
if st.session_state["clean"]:
    st.markdown(clean_css(), unsafe_allow_html=True)

# define pages; hide the auto nav so we can put the brand ABOVE the links
pages = [
    st.Page(overview.render, title="Overview", icon=":material/dashboard:",
            url_path="overview", default=True),
    st.Page(scorer.render, title="Risk Scorer", icon=":material/person_search:",
            url_path="scorer"),
    st.Page(batch.render, title="Batch Scoring", icon=":material/upload_file:",
            url_path="batch"),
]
nav = st.navigation(pages, position="hidden")

# custom sidebar: brand on top, then navigation links
with st.sidebar:
    st.markdown('<div class="brand"><span class="dot">◆</span> Churn Intelligence</div>',
                unsafe_allow_html=True)
    st.caption("Predictive retention analytics")
    st.divider()
    for p in pages:
        st.page_link(p)
    st.divider()

data.get_model()  # warm caches
nav.run()
