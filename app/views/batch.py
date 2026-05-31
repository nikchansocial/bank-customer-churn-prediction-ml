"""Batch Scoring — score a whole customer file and export the results."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from lib import config, data, ui
from lib.pipeline import RAW_INPUTS
from lib.theme import get_theme


def _template_csv() -> bytes:
    sample = data.load_data()[RAW_INPUTS].head(20)
    return sample.to_csv(index=False).encode()


def render():
    T = get_theme()
    model = data.get_model()
    cur = config.CURRENCY
    ui.header(T)

    ui.section("Batch Customer Scoring")
    ui.render('<div class="box accent"><p>Upload a CSV of customers and score every row at once. '
              "Required columns: <span class='tag'>"
              + "</span> <span class='tag'>".join(RAW_INPUTS) + "</span></p></div>")

    cdl, cup = st.columns([1, 2])
    cdl.download_button("⬇ Download template (20 rows)", _template_csv(),
                        "churn_template.csv", "text/csv", width='stretch')
    threshold = cup.slider("Flag threshold", 0.20, 0.60, model.threshold, 0.05)

    up = st.file_uploader("Upload customer CSV", type=["csv"], label_visibility="collapsed")
    if up is None:
        st.caption("No file yet — download the template above to see the expected format, "
                   "or try it on the bundled dataset.")
        if st.button("▶ Score the bundled European_Bank sample (200 rows)"):
            df = data.load_data()[RAW_INPUTS].head(200)
            _show_results(df, model, threshold, T, cur)
        return

    try:
        df = pd.read_csv(up)
    except Exception as e:
        st.error(f"Could not read that CSV: {e}")
        return

    missing = [c for c in RAW_INPUTS if c not in df.columns]
    if missing:
        st.error("Missing required column(s): " + ", ".join(missing))
        return

    _show_results(df[RAW_INPUTS], model, threshold, T, cur)


def _show_results(df, model, threshold, T, cur):
    scored = model.score_batch(df, threshold=threshold)
    n = len(scored)
    flagged = int((scored["Churn_Probability"] >= threshold).sum())
    exposure = float((scored["Churn_Probability"] * scored["Balance"]).sum())

    ui.section("Results Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(ui.kpi(f"{n:,}", "Customers Scored"), unsafe_allow_html=True)
    c2.markdown(ui.kpi(f"{flagged:,}", f"Flagged @ {threshold:.2f}", color=T["bad"]), unsafe_allow_html=True)
    c3.markdown(ui.kpi(f"{flagged/n*100:.1f}%", "Flagged Rate", color=T["warn"]), unsafe_allow_html=True)
    c4.markdown(ui.money_card(f"{cur}{exposure/1e6:.2f}M", "Probability-Weighted Exposure",
                              "Σ prob × balance"), unsafe_allow_html=True)

    ui.section("Highest-Risk Customers")
    top = scored.sort_values("Churn_Probability", ascending=False).head(15)
    st.dataframe(
        top, width='stretch', hide_index=True,
        column_config={
            "Churn_Probability": st.column_config.ProgressColumn(
                "Churn Prob", min_value=0.0, max_value=1.0, format="%.2f"),
            "Balance_at_Risk": st.column_config.NumberColumn("Balance at Risk", format=f"{cur}%d"),
        },
    )

    out = io.BytesIO()
    scored.to_csv(out, index=False)
    st.download_button("⬇ Download full scored CSV", out.getvalue(),
                       "scored_customers.csv", "text/csv", width='stretch')
    ui.footer()
