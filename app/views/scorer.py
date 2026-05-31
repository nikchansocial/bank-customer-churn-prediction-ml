"""Risk Scorer — score a single customer, explain it with SHAP, simulate."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import config, data, ui
from lib.theme import get_theme


def _inputs():
    s = st.sidebar
    s.markdown("## Customer Profile")
    s.caption("Adjust the inputs to score a customer.")
    s.markdown('<div class="sgroup">Demographics</div>', unsafe_allow_html=True)
    age = s.slider("Age", 18, 92, 45,
                   help="Customer's age in years. Churn rises sharply in the 51–60 band.")
    gender = s.selectbox("Gender", ["Female", "Male"],
                         help="Recorded gender. In this dataset, female customers churn more.")
    geography = s.selectbox("Geography", ["France", "Germany", "Spain"],
                            help="Country of residence. Germany is the highest-risk market (32.4%).")
    s.markdown('<div class="sgroup">Account & Financials</div>', unsafe_allow_html=True)
    credit = s.slider("Credit Score", 300, 850, 650,
                      help="Creditworthiness score (300–850). Lower scores can signal risk.")
    balance = s.number_input("Account Balance (€)", 0, 250000, 120000, step=1000,
                             help="Current account balance. Drives the 'balance at risk' figure.")
    salary = s.number_input("Estimated Salary (€)", 0, 200000, 100000, step=1000,
                            help="Estimated annual salary, used in the balance-to-salary ratio.")
    tenure = s.slider("Tenure (Years)", 0, 10, 3,
                      help="Years the customer has been with the bank.")
    s.markdown('<div class="sgroup">Engagement</div>', unsafe_allow_html=True)
    products = s.selectbox("Number of Products", [1, 2, 3, 4],
                           help="Bank products held. 3+ products churn at 83–100% (over-bundling).")
    card = s.selectbox("Has Credit Card", [1, 0], format_func=lambda x: "Yes" if x else "No",
                       help="Whether the customer holds a credit card.")
    active = s.selectbox("Is Active Member", [1, 0], format_func=lambda x: "Yes" if x else "No",
                         help="Active members churn far less (14.3% vs 26.9% for inactive).")
    s.markdown('<div class="sgroup">Model Setting</div>', unsafe_allow_html=True)
    threshold = s.slider("Churn flag cutoff", 0.20, 0.60, 0.35, 0.05,
                         help="Probability above which a customer is flagged. Lower = higher recall "
                              "(catches more churners). Tuned to 0.35.")
    return dict(CreditScore=credit, Age=age, Tenure=tenure, Balance=balance,
                NumOfProducts=products, HasCrCard=card, IsActiveMember=active,
                EstimatedSalary=salary, Geography=geography, Gender=gender), threshold


def _shap_panel(model, profile, T):
    """Per-customer SHAP: which features pushed this prediction up/down."""
    try:
        import shap
        from lib.pipeline import build_features
        X = build_features(pd.DataFrame([profile]))[model.feature_order]
        sv = shap.TreeExplainer(model.model)(X)
        contribs = sorted(zip(model.feature_order, sv.values[0]),
                          key=lambda t: -abs(t[1]))[:6]
        rows = ""
        for feat, val in contribs:
            up = val > 0
            color = T["bad"] if up else T["good"]
            arrow = "▲ raises" if up else "▼ lowers"
            name = feat.replace("_", " ")
            rows += (f'<div class="pill {"bad" if up else "good"}">'
                     f'<span class="g">{"▲" if up else "▼"}</span>'
                     f'<span><b>{name}</b> — {arrow} churn risk '
                     f'<span style="color:{color};font-weight:700">({val:+.2f})</span></span></div>')
        ui.render(rows)
    except Exception as e:
        st.info(f"SHAP explanation unavailable in this environment ({type(e).__name__}).")


def render():
    T = get_theme()
    model = data.get_model()
    profile, threshold = _inputs()
    cur = config.CURRENCY

    ui.topbar()
    ui.header(T, "Customer Risk Scorer", "Single-customer churn probability & explanation")

    prob = model.score_one(**profile)
    label, glyph, band = config.risk_band(prob)
    rc = {"bad": T["bad"], "warn": T["warn"], "good": T["good"]}[band]
    will_churn = prob >= threshold
    money_at_risk = prob * profile["Balance"]

    # ---- risk assessment --------------------------------------------------
    ui.section("Risk Assessment")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(ui.kpi(f"{prob*100:.1f}%", "Churn Probability"), unsafe_allow_html=True)
    c2.markdown(ui.kpi(f"{glyph} {label}", "Risk Level", color=rc, size=18), unsafe_allow_html=True)
    pcol = T["bad"] if will_churn else T["good"]
    c3.markdown(ui.kpi("Will Churn" if will_churn else "Will Stay",
                       f"Prediction @ {threshold:.2f}", color=pcol, size=18), unsafe_allow_html=True)
    c4.markdown(ui.money_card(f"{cur}{money_at_risk:,.0f}", "Balance at Risk",
                              f"{prob*100:.0f}% × {cur}{profile['Balance']:,.0f}"), unsafe_allow_html=True)

    ui.section("Probability Meter")
    st.progress(float(prob))
    ui.render(f"<p style='text-align:center;color:{T['muted']};font-size:12px;font-weight:600'>"
              f"Churn Risk {prob*100:.1f}% · Flag Threshold {threshold*100:.0f}%</p>")

    # ---- explanation + what-if -------------------------------------------
    left, right = st.columns([1, 1])
    with left:
        ui.section("Why — SHAP Explanation")
        _shap_panel(model, profile, T)
    with right:
        ui.section("What-If Simulator")
        sims = []
        if profile["IsActiveMember"] == 0:
            alt = {**profile, "IsActiveMember": 1}
            sims.append(("Re-activate this member", model.score_one(**alt)))
        if profile["NumOfProducts"] >= 3:
            alt = {**profile, "NumOfProducts": 2}
            sims.append(("Consolidate to 2 products", model.score_one(**alt)))
        if not sims:
            ui.render('<div class="box accent"><p>This customer is active with a healthy product '
                      'count. Toggle <b>Is Active Member</b> to <b>No</b> or raise <b>Number of '
                      'Products</b> in the sidebar to simulate an intervention.</p></div>')
        for name, p2 in sims:
            drop = (prob - p2) * 100
            saved = (prob - p2) * profile["Balance"]
            if drop > 0.1:
                ui.render(f'<div class="box accent"><p><b>{name}</b><br>Churn moves '
                          f'<b style="color:{T["bad"]}">{prob*100:.1f}%</b> → '
                          f'<b style="color:{T["good"]}">{p2*100:.1f}%</b> (−{drop:.1f} pts), '
                          f'protecting ≈ <b style="color:{T["accent_soft"]}">{cur}{saved:,.0f}</b>.</p></div>')
            else:
                ui.render(f'<div class="box accent"><p><b>{name}</b><br>Barely moves risk '
                          f'({prob*100:.1f}% → {p2*100:.1f}%) — other factors dominate here.</p></div>')

        # behavioral signals — fills the column so it balances the SHAP list
        ui.section("Behavioral Signals")
        eng = ("High" if (profile["IsActiveMember"] and profile["NumOfProducts"] in (1, 2))
               else "Low" if not profile["IsActiveMember"] else "Moderate")
        tags = [
            f"Engagement: {eng}",
            f"Product density: {profile['NumOfProducts']/(profile['Tenure']+1):.2f}/yr",
            f"Balance/Salary: {profile['Balance']/(profile['EstimatedSalary']+1):.2f}",
            f"Active: {'Yes' if profile['IsActiveMember'] else 'No'}",
            f"Credit card: {'Yes' if profile['HasCrCard'] else 'No'}",
        ]
        ui.render('<div class="box">' + "".join(f'<span class="tag">{t}</span>' for t in tags) + '</div>')

    # ---- recommended action plan -----------------------------------------
    ui.section("Recommended Action Plan")
    plans = {
        "bad": ("High Risk — Immediate Intervention", T["bad"], [
            "Assign a dedicated relationship manager within 48 hours.",
            "Offer a personalised retention package — preferential rates or fee waivers.",
            "If 3+ products: review for mis-selling and consolidate to the 2 most-used.",
            "Schedule a direct call, not an automated email.",
            f"Priority justified: <b>{cur}{money_at_risk:,.0f}</b> of balance is exposed.",
        ]),
        "warn": ("Medium Risk — Proactive Engagement", T["warn"], [
            "Enrol in a targeted re-engagement campaign over the next 30 days.",
            "Send a personalised product-fit review and loyalty offer.",
            "For affluent customers: present competitive savings / FD options early.",
            "Track engagement monthly; escalate if activity drops further.",
            f"Balance to monitor: <b>{cur}{money_at_risk:,.0f}</b>.",
        ]),
        "good": ("Low Risk — Nurture & Grow", T["good"], [
            "Maintain standard relationship touchpoints.",
            "Identify a thoughtful, needs-based upsell (stay within 2 core products).",
            "Invite into loyalty or referral programmes.",
            "Continue quarterly health checks — no active intervention needed.",
        ]),
    }
    title, col, items = plans[band]
    lis = "".join(f"<li>{x}</li>" for x in items)
    ui.render(f'<div class="box" style="border-left:4px solid {col}"><h4>{title}</h4><ul>{lis}</ul></div>')

    # ---- real model performance ------------------------------------------
    ui.section("Model Performance · held-out test set")
    m = model.metrics
    p1, p2c, p3, p4 = st.columns(4)
    cards = [("Gradient Boosting", "Model", 15),
             (f"{m['accuracy']*100:.1f}%", "Accuracy", 23),
             (f"{m['recall']*100:.1f}%", f"Recall @ {m['threshold']:.2f}", 23),
             (f"{m['roc_auc']:.4f}", "ROC-AUC", 23)]
    for col_, (val, lab, sz) in zip([p1, p2c, p3, p4], cards):
        col_.markdown(ui.kpi(val, lab, size=sz), unsafe_allow_html=True)

    ui.footer()
