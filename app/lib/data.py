"""Cached data access + aggregate insights for the Overview page.

`@st.cache_data` / `@st.cache_resource` mean the CSV is parsed once and the
model is loaded/trained once per session, not on every interaction.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import pipeline as P


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(P.DATA_PATH)
    drop = [c for c in ["Year", "CustomerId", "Surname", "RowNumber"] if c in df.columns]
    df = df.drop(columns=drop)
    df["AgeBand"] = pd.cut(
        df["Age"], [17, 30, 40, 50, 60, 200],
        labels=["18–30", "31–40", "41–50", "51–60", "60+"],
    )
    return df


@st.cache_resource(show_spinner=False)
def get_model() -> P.ChurnModel:
    return P.load()


@st.cache_data(show_spinner=False)
def headline_kpis() -> dict:
    df = load_data()
    churned = df[df["Exited"] == 1]
    return {
        "rows": len(df),
        "churn_rate": df["Exited"].mean(),
        "customers_lost": int(df["Exited"].sum()),
        "balance_at_risk": float(churned["Balance"].sum()),
        "high_value_churn": float(df.loc[df["Balance"] > 100_000, "Exited"].mean()),
    }


@st.cache_data(show_spinner=False)
def churn_by(col: str) -> pd.DataFrame:
    """Churn rate (%) and customer count by a categorical column."""
    df = load_data()
    g = df.groupby(col, observed=True)["Exited"].agg(["mean", "count"]).reset_index()
    g["churn_pct"] = (g["mean"] * 100).round(1)
    g = g.rename(columns={"count": "customers"})
    return g[[col, "churn_pct", "customers"]]
