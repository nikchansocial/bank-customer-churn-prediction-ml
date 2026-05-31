"""Small render helpers so views stay declarative and DRY."""
from __future__ import annotations

import streamlit as st

from lib import config


import streamlit.components.v1 as components  # noqa: E402

_PRINT_BTN = """
<button onclick="try{window.parent.print()}catch(e){window.print()}" style="
  font-family:'Instrument Sans',sans-serif; font-size:13px; font-weight:600;
  color:#c15f3c; background:#ffffff; border:1px solid #e7e3d8; border-radius:10px;
  padding:8px 12px; cursor:pointer; width:100%;">🖨 Print / PDF</button>
"""


def topbar() -> None:
    """Right-aligned Print/PDF button + clean-view toggle for capture."""
    _, c_print, c_clean = st.columns([5, 1.5, 1.5])
    with c_print:
        components.html(_PRINT_BTN, height=44)
    with c_clean:
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
