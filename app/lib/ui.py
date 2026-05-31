"""Small render helpers so views stay declarative and DRY."""
from __future__ import annotations

import streamlit as st

from lib import config


def topbar() -> None:
    """Right-aligned clean-view toggle for screenshot-friendly capture."""
    _, right = st.columns([4, 1])
    with right:
        st.toggle("Clean view", key="clean",
                  help="Hide the sidebar and app chrome for a tidy screenshot.")


def section(label: str) -> None:
    st.markdown(f'<div class="sec">{label}</div>', unsafe_allow_html=True)


def header(T: dict, title: str = "Overview", subtitle: str = "") -> None:
    sub = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div class="phd">
    <h1><span class="dia">◆</span> {title}</h1>
    {sub}
</div>""", unsafe_allow_html=True)


def kpi(value: str, label: str, *, color: str | None = None, delta: str | None = None,
        delta_color: str | None = None, size: int = 27) -> str:
    style = f"color:{color} !important;" if color else ""
    d = f'<div class="d" style="color:{delta_color}">{delta}</div>' if delta else ""
    return (f'<div class="card"><div class="v" style="{style}font-size:{size}px">{value}</div>'
            f'<div class="l">{label}</div>{d}</div>')


def money_card(value: str, label: str, sub: str = "") -> str:
    s = f'<div class="s">{sub}</div>' if sub else ""
    return f'<div class="money"><div class="v">{value}</div><div class="l">{label}</div>{s}</div>'


def pill(kind: str, glyph: str, msg: str) -> str:
    return f'<div class="pill {kind}"><span class="g">{glyph}</span><span>{msg}</span></div>'


def render(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def footer() -> None:
    st.markdown(f"""
<div class="ft">
    <div class="name">Bank Customer Churn Prediction · built by <span>{config.AUTHOR_HANDLE}</span></div>
    <div class="meta">Gradient Boosting · SHAP explainability · recall-tuned threshold · Streamlit</div>
</div>""", unsafe_allow_html=True)
