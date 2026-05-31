"""Executive Overview — live KPIs and segment charts computed from the data."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import config, data, ui
from lib.theme import get_theme, style_fig


def _bar(frame, x, T, title, sort=False):
    f = frame.sort_values("churn_pct", ascending=False) if sort else frame
    colors = [T["bad"] if v >= 30 else T["warn"] if v >= 20 else T["good"]
              for v in f["churn_pct"]]
    fig = go.Figure(go.Bar(
        x=f[x].astype(str), y=f["churn_pct"], marker_color=colors,
        text=[f"{v:.1f}%" for v in f["churn_pct"]], textposition="outside",
        customdata=f["customers"],
        hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<br>Customers: %{customdata:,}<extra></extra>",
    ))
    fig.update_layout(title=title, yaxis_title="Churn rate %", showlegend=False)
    fig.update_yaxes(range=[0, max(f["churn_pct"]) * 1.18])
    return style_fig(fig, T, height=250)


def render():
    T = get_theme()
    ui.topbar()
    ui.header(T, "Executive Overview", "Retail banking · portfolio churn analytics")
    k = data.headline_kpis()
    cur = config.CURRENCY

    # ---- KPI row ----------------------------------------------------------
    ui.section("Portfolio Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(ui.kpi(f"{k['churn_rate']*100:.1f}%", "Overall Churn Rate", color=T["bad"]), unsafe_allow_html=True)
    c2.markdown(ui.kpi(f"{k['customers_lost']:,}", "Customers Lost"), unsafe_allow_html=True)
    c3.markdown(ui.kpi(f"{k['high_value_churn']*100:.1f}%", "High-Value Churn", color=T["warn"]), unsafe_allow_html=True)
    c4.markdown(ui.money_card(f"{cur}{k['balance_at_risk']/1e6:.1f}M", "Balance Lost to Churn",
                              f"sum of churned balances · n={k['rows']:,}"), unsafe_allow_html=True)

    # ---- Key findings (data-derived) -------------------------------------
    ui.section("What the Data Says")
    geo = data.churn_by("Geography").sort_values("churn_pct", ascending=False)
    prod = data.churn_by("NumOfProducts")
    age = data.churn_by("AgeBand")
    worst_geo = geo.iloc[0]
    worst_age = age.sort_values("churn_pct", ascending=False).iloc[0]
    p3plus = prod[prod["NumOfProducts"] >= 3]["churn_pct"]
    act = data.churn_by("IsActiveMember").set_index("IsActiveMember")["churn_pct"]
    findings = [
        ("bad", "◆", f"<b>{worst_geo['Geography']}</b> is the highest-risk market at "
                     f"<b>{worst_geo['churn_pct']:.1f}%</b> churn — roughly double France/Spain."),
        ("bad", "◆", f"Customers with <b>3+ products</b> churn at <b>{p3plus.min():.0f}–{p3plus.max():.0f}%</b> "
                     f"— a strong mis-selling / over-bundling signal."),
        ("warn", "◆", f"The <b>{worst_age['AgeBand']}</b> age band peaks at <b>{worst_age['churn_pct']:.1f}%</b> churn — "
                      f"high-value customers likely comparing rates."),
        ("warn", "◆", f"<b>Inactive</b> members churn at <b>{act.get(0,0):.1f}%</b> vs <b>{act.get(1,0):.1f}%</b> "
                      f"for active — engagement is the clearest lever."),
    ]
    for kind, g, msg in findings:
        ui.render(ui.pill(kind, g, msg))

    # ---- Charts -----------------------------------------------------------
    ui.section("Churn by Segment")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(_bar(data.churn_by("Geography"), "Geography", T, "By Geography"),
                        width='stretch', key="geo")
    with b:
        st.plotly_chart(_bar(prod, "NumOfProducts", T, "By Number of Products"),
                        width='stretch', key="prod")
    a2, b2 = st.columns(2)
    with a2:
        st.plotly_chart(_bar(age, "AgeBand", T, "By Age Band"),
                        width='stretch', key="age")
    with b2:
        gen = data.churn_by("Gender")
        st.plotly_chart(_bar(gen, "Gender", T, "By Gender", sort=True),
                        width='stretch', key="gender")

    # ---- Balance distribution --------------------------------------------
    ui.section("Balance Profile · Retained vs Churned")
    df = data.load_data()
    fig = px.histogram(df, x="Balance", color=df["Exited"].map({0: "Retained", 1: "Churned"}),
                       nbins=40, barmode="overlay", opacity=0.75,
                       color_discrete_map={"Retained": T["good"], "Churned": T["bad"]})
    fig.update_layout(title="", legend_title_text="", xaxis_title=f"Account balance ({config.CURRENCY})",
                      yaxis_title="Customers")
    st.plotly_chart(style_fig(fig, T, height=250), width='stretch', key="bal")

    ui.footer()
