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
    ui.topbar()
    ui.header(T, "Batch Scoring", "Score and export an entire customer file")

    # ---- how it works ----------------------------------------------------
    cols_inline = " · ".join(RAW_INPUTS)
    ui.render(
        f'<div class="box accent"><h4>Score an entire customer book at once</h4>'
        f'<p>Upload a CSV and every customer is scored, ranked by churn risk, and '
        f'made available to download. Your file needs these {len(RAW_INPUTS)} columns:</p>'
        f'<p style="margin-top:7px;color:{T["muted"]};font-size:12px">{cols_inline}</p></div>'
    )

    # ---- step 1: template -------------------------------------------------
    ui.section("Step 1 · Get the format")
    a, b = st.columns([3, 2])
    with a:
        ui.render('<div class="box"><p>New here? Download a ready-made 20-row template with the '
                  'exact columns in the right order — fill it with your data, or just use it as-is '
                  'to see how scoring works.</p></div>')
    with b:
        st.download_button("⬇  Download template (20 rows)", _template_csv(),
                           "churn_template.csv", "text/csv", width="stretch")
        st.caption("CSV · opens in Excel or Sheets")

    # ---- step 2: score ----------------------------------------------------
    ui.section("Step 2 · Score your customers")
    threshold = st.slider(
        "Flag threshold", 0.20, 0.60, model.threshold, 0.05,
        help="A customer is flagged 'will churn' when their probability is at or above this. "
             "Lower = catches more churners (higher recall). Tuned default: 0.35.",
    )

    up = st.file_uploader("Upload your customer CSV", type=["csv"])

    if up is None:
        st.caption("No file uploaded yet — or try the model instantly on the bundled dataset:")
        if st.button("▶  Score the bundled European_Bank sample (200 rows)", width="stretch"):
            df = data.load_data()[RAW_INPUTS].head(200)
            _show_results(df, model, threshold, T, cur)
        else:
            ui.footer()
        return

    try:
        df = pd.read_csv(up)
    except Exception as e:
        st.error(f"Could not read that CSV: {e}")
        return

    missing = [c for c in RAW_INPUTS if c not in df.columns]
    if missing:
        st.error("That file is missing required column(s): " + ", ".join(missing)
                 + ". Download the template above for the correct format.")
        return

    _show_results(df[RAW_INPUTS], model, threshold, T, cur)


def _show_results(df, model, threshold, T, cur):
    scored = model.score_batch(df, threshold=threshold)
    n = len(scored)
    flagged = int((scored["Churn_Probability"] >= threshold).sum())
    exposure = float((scored["Churn_Probability"] * scored["Balance"]).sum())

    ui.section("Results · Portfolio Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(ui.kpi(f"{n:,}", "Customers Scored"), unsafe_allow_html=True)
    c2.markdown(ui.kpi(f"{flagged:,}", f"Flagged @ {threshold:.2f}", color=T["bad"]), unsafe_allow_html=True)
    c3.markdown(ui.kpi(f"{flagged/n*100:.1f}%", "Flagged Rate", color=T["warn"]), unsafe_allow_html=True)
    c4.markdown(ui.money_card(f"{cur}{exposure/1e6:.2f}M", "Exposure at Risk",
                              "Σ probability × balance"), unsafe_allow_html=True)

    ui.section("Top 15 Highest-Risk Customers")
    top = scored.sort_values("Churn_Probability", ascending=False).head(15)
    show = top[["Age", "Geography", "Gender", "NumOfProducts", "Balance",
                "IsActiveMember", "Churn_Probability", "Prediction", "Balance_at_Risk"]]
    st.dataframe(
        show, width="stretch", hide_index=True,
        column_config={
            "NumOfProducts": "Products",
            "IsActiveMember": st.column_config.NumberColumn("Active"),
            "Balance": st.column_config.NumberColumn("Balance", format=f"{cur}%d"),
            "Churn_Probability": st.column_config.ProgressColumn(
                "Churn Probability", min_value=0.0, max_value=1.0, format="%.2f"),
            "Balance_at_Risk": st.column_config.NumberColumn("Balance at Risk", format=f"{cur}%d"),
        },
    )

    out = io.BytesIO()
    scored.to_csv(out, index=False)
    st.download_button(f"⬇  Download all {n:,} scored customers (CSV)", out.getvalue(),
                       "scored_customers.csv", "text/csv", width="stretch")
    ui.footer()
