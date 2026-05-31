"""Small render helpers so views stay declarative and DRY."""
from __future__ import annotations

import streamlit as st

from lib import config


def section(label: str) -> None:
    st.markdown(f'<div class="sec">{label}</div>', unsafe_allow_html=True)


def header(T: dict) -> None:
    st.markdown(f"""
<div class="hd">
    <div class="mark">◆</div>
    <div>
        <h1>Customer {config.APP_TITLE}</h1>
        <p>{config.APP_TAGLINE}</p>
    </div>
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
