"""Theme — a single refined light palette (warm, editorial, premium).

Aesthetic: warm paper background, clay/terracotta accent, earthy semantic
colours, a serif display face (Fraunces) paired with a clean body sans
(Instrument Sans). Calm, spacious-but-compact, BI-grade.
"""
from __future__ import annotations

import streamlit as st

PALETTE = dict(
    bg="#f7f5f0", panel="#ffffff", panel2="#f3f1ea", text="#26241d",
    muted="#79746b", border="#e7e3d8", accent="#c15f3c", accent_soft="#d98b6e",
    good="#4f7a5f", warn="#b07d2e", bad="#b14a32",
    money_bg="linear-gradient(135deg,#2b2822,#43352b)",
    shadow="0 1px 2px rgba(38,36,29,0.05), 0 6px 20px rgba(38,36,29,0.05)",
    grid="rgba(38,36,29,0.07)",
)


def get_theme() -> dict:
    return PALETTE


def inject_css(T: dict) -> None:
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Instrument+Sans:wght@400;500;600;700&display=swap');

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="block-container"], .main, .block-container {{ background:{T['bg']} !important; }}
[data-testid="stHeader"] {{ background:transparent !important; }}
html, body, .stMarkdown, .stMarkdown p, .stMarkdown span {{ font-family:'Instrument Sans',sans-serif; }}
[data-testid="stMain"] .stMarkdown, [data-testid="stMain"] .stMarkdown * {{ color:{T['text']}; }}
#MainMenu, footer {{ visibility:hidden; }}

[data-testid="block-container"] {{ padding-top:0.9rem; padding-bottom:0.8rem; max-width:1140px; }}
[data-testid="stVerticalBlock"] {{ gap:0.4rem; }}

/* slim page header */
.phd {{ margin:2px 0 12px 0; padding:0 0 10px 0; border-bottom:1px solid {T['border']}; }}
.phd h1 {{ font-family:'Fraunces',serif; font-weight:600; font-size:23px; margin:0; color:{T['text']} !important; letter-spacing:-0.4px; }}
.phd h1 .dia {{ color:{T['accent']}; font-size:17px; vertical-align:1px; margin-right:4px; }}
.phd p {{ margin:3px 0 0 0; font-size:10.5px; color:{T['muted']} !important; letter-spacing:0.7px; font-weight:600; text-transform:uppercase; }}

/* section label */
.sec {{ font-family:'Instrument Sans',sans-serif; font-size:11px; font-weight:700; letter-spacing:1.3px;
       text-transform:uppercase; color:{T['muted']} !important; margin:12px 0 6px 2px;
       display:flex; align-items:center; gap:9px; }}
.sec::after {{ content:""; flex:1; height:1px; background:{T['border']}; }}

/* cards */
.card {{ background:{T['panel']}; border:1px solid {T['border']}; border-radius:15px;
        padding:15px 14px; text-align:center; box-shadow:{T['shadow']};
        transition:transform .18s ease, border-color .18s ease; height:100%; }}
.card:hover {{ transform:translateY(-2px); border-color:{T['accent_soft']}; }}
.card .v {{ font-family:'Fraunces',serif; font-size:30px; font-weight:600; line-height:1; color:{T['text']} !important; }}
.card .l {{ font-size:10.5px; color:{T['muted']} !important; text-transform:uppercase; letter-spacing:1px; margin-top:8px; font-weight:600; }}
.card .d {{ font-size:11px; margin-top:5px; font-weight:600; }}

.money {{ background:{T['money_bg']}; border:1px solid {T['border']}; border-radius:15px; padding:15px 14px; text-align:center; box-shadow:{T['shadow']}; height:100%; }}
.money .v {{ font-family:'Fraunces',serif; font-size:26px; font-weight:600; color:#f0d9c8 !important; line-height:1; }}
.money .l {{ font-size:10.5px; color:#d8c4b3 !important; text-transform:uppercase; letter-spacing:1px; margin-top:8px; font-weight:600; }}
.money .s {{ font-size:10px; color:#b9a695 !important; margin-top:4px; }}

/* pills */
.pill {{ display:flex; align-items:center; gap:10px; border-radius:12px; padding:9px 14px; margin:4px 0; font-size:13px; font-weight:400;
        border:1px solid {T['border']}; background:{T['panel']}; color:{T['text']} !important; box-shadow:{T['shadow']}; }}
.pill .g {{ font-size:11px; }}
.pill.bad  {{ border-left:3px solid {T['bad']};  }}
.pill.bad .g  {{ color:{T['bad']}; }}
.pill.warn {{ border-left:3px solid {T['warn']}; }}
.pill.warn .g {{ color:{T['warn']}; }}
.pill.good {{ border-left:3px solid {T['good']}; }}
.pill.good .g {{ color:{T['good']}; }}

/* boxes */
.box {{ background:{T['panel']}; border:1px solid {T['border']}; border-radius:15px; padding:15px 19px; box-shadow:{T['shadow']}; }}
.box.accent {{ border-left:3px solid {T['accent']}; }}
.box h4 {{ font-family:'Fraunces',serif; font-weight:600; margin:0 0 8px 0; font-size:15px; color:{T['text']} !important; }}
.box ul {{ margin:0; padding-left:18px; }}
.box li {{ margin:5px 0; color:{T['text']} !important; font-size:13px; line-height:1.45; }}
.box p  {{ color:{T['text']} !important; font-size:13px; margin:0; line-height:1.5; }}

.tag {{ display:inline-block; background:{T['panel2']}; border:1px solid {T['border']};
       color:{T['accent']} !important; border-radius:20px; padding:4px 11px; margin:4px 4px 0 0; font-size:11.5px; font-weight:600; }}

/* footer */
.ft {{ text-align:center; margin-top:20px; padding:14px; border-top:1px solid {T['border']}; }}
.ft .name {{ font-family:'Fraunces',serif; font-weight:600; font-size:12.5px; color:{T['text']} !important; }}
.ft .name span {{ color:{T['accent']} !important; }}
.ft .meta {{ font-size:11px; color:{T['muted']} !important; margin-top:4px; letter-spacing:0.3px; }}
.ft .meta a {{ color:{T['accent']} !important; text-decoration:none; font-weight:600; }}
.ft .meta a:hover {{ text-decoration:underline; }}

/* sidebar */
[data-testid="stSidebar"] {{ background:{T['panel']} !important; border-right:1px solid {T['border']}; }}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {{ color:{T['text']} !important; }}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] p {{ color:{T['muted']} !important; }}
.sgroup {{ font-family:'Instrument Sans',sans-serif; font-size:10.5px; font-weight:700; letter-spacing:1px;
          text-transform:uppercase; color:{T['accent']} !important; margin:13px 0 2px 2px; }}
.brand {{ font-family:'Fraunces',serif; font-weight:600; font-size:16px; color:{T['text']} !important; display:flex; align-items:center; gap:7px; }}
.brand .dot {{ color:{T['accent']}; }}
.stProgress > div > div > div > div {{ background:{T['accent']} !important; }}

/* print / save-as-PDF: auto-clean output */
@media print {{
  [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
  [data-testid="stHeader"], [data-testid="stToolbar"],
  [data-testid="stToggle"], [data-testid="stIFrame"],
  [data-testid="stCustomComponentV1"] {{ display:none !important; }}
  [data-testid="stMain"] {{ margin-left:0 !important; }}
  .stApp, [data-testid="stAppViewContainer"] {{ background:#ffffff !important; }}
  [data-testid="block-container"] {{ max-width:100% !important; padding-top:0 !important; }}
  .card, .box, .pill, .money {{ box-shadow:none !important; break-inside:avoid; }}
}}
</style>
""", unsafe_allow_html=True)


def clean_css() -> str:
    """Returns CSS that hides app chrome for a clean screenshot."""
    return """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"], [data-testid="stToolbar"] { display:none !important; }
[data-testid="stAppViewContainer"] [data-testid="stMain"] { margin-left:0 !important; }
[data-testid="block-container"] { max-width:1180px !important; padding-top:1.2rem !important; }
</style>
"""


def style_fig(fig, T: dict, height: int = 260):
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Instrument Sans, sans-serif", color=T["muted"], size=12),
        title_font=dict(family="Fraunces, serif", color=T["text"], size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["muted"])),
        xaxis=dict(gridcolor=T["grid"], zerolinecolor=T["grid"]),
        yaxis=dict(gridcolor=T["grid"], zerolinecolor=T["grid"]),
        colorway=[T["accent"], T["good"], T["bad"], T["warn"], T["accent_soft"]],
    )
    return fig
