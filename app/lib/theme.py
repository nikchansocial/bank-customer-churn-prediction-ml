"""Theme system — one palette dict drives all CSS and chart styling.

Aesthetic: a refined "risk-desk" look — graphite/ink neutrals, a warm gold
brand accent (money/premium banking), a clear semantic trio for risk
(emerald / amber / red), Sora for display, Manrope for body, JetBrains Mono
for figures (the financial-terminal touch).
"""
from __future__ import annotations

import streamlit as st


def _palette(dark: bool) -> dict:
    if dark:
        return dict(
            bg="#0b0e14", panel="#141925", panel2="#1b2230", text="#e7e9ef",
            muted="#8a92a6", border="#222a3a", accent="#e0b54a", accent_soft="#f0cd7a",
            good="#34d399", warn="#fbbf24", bad="#f87171",
            money_bg="linear-gradient(135deg,#1a1f2e,#2a2417)",
            shadow="0 6px 24px rgba(0,0,0,0.45)", grid="rgba(255,255,255,0.06)",
        )
    return dict(
        bg="#f3f4f8", panel="#ffffff", panel2="#f8f9fc", text="#161a24",
        muted="#697089", border="#e4e7f0", accent="#b8862b", accent_soft="#d9a93f",
        good="#059669", warn="#d97706", bad="#dc2626",
        money_bg="linear-gradient(135deg,#1a1f2e,#33365a)",
        shadow="0 4px 18px rgba(20,22,40,0.08)", grid="rgba(20,22,40,0.07)",
    )


def get_theme() -> dict:
    """Return the active palette; defaults to dark."""
    return _palette(st.session_state.get("dark", True))


def inject_css(T: dict) -> None:
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap');

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="block-container"], .main, .block-container {{ background:{T['bg']} !important; }}
[data-testid="stHeader"] {{ background:transparent !important; }}
html, body, .stMarkdown, .stMarkdown p, .stMarkdown span {{ font-family:'Manrope',sans-serif; }}
[data-testid="stMain"] .stMarkdown, [data-testid="stMain"] .stMarkdown * {{ color:{T['text']}; }}
#MainMenu, footer {{ visibility:hidden; }}

[data-testid="block-container"] {{ padding-top:1.1rem; padding-bottom:1rem; max-width:1180px; }}
[data-testid="stVerticalBlock"] {{ gap:0.5rem; }}

/* header */
.hd {{ display:flex; align-items:center; gap:12px; padding:12px 18px; border-radius:14px;
      background:{T['panel']}; border:1px solid {T['border']}; box-shadow:{T['shadow']}; margin:2px 0 14px 0; }}
.hd .mark {{ width:34px; height:34px; border-radius:10px; flex:0 0 auto;
      background:linear-gradient(135deg,{T['accent']},{T['accent_soft']});
      display:flex; align-items:center; justify-content:center; color:#1a1206; font-size:17px; font-weight:800;
      box-shadow:0 3px 12px {T['accent']}44; }}
.hd h1 {{ font-family:'Sora',sans-serif; font-weight:800; font-size:18px; margin:0; color:{T['text']} !important; letter-spacing:-0.3px; }}
.hd p  {{ margin:1px 0 0 0; font-size:11px; color:{T['muted']} !important; letter-spacing:0.5px; font-weight:600; text-transform:uppercase; }}

/* section label */
.sec {{ font-family:'Sora',sans-serif; font-size:12px; font-weight:700; letter-spacing:1.4px;
       text-transform:uppercase; color:{T['muted']} !important; margin:14px 0 7px 2px;
       display:flex; align-items:center; gap:8px; }}
.sec::after {{ content:""; flex:1; height:1px; background:{T['border']}; }}

/* cards */
.card {{ background:{T['panel']}; border:1px solid {T['border']}; border-radius:14px;
        padding:16px 14px; text-align:center; box-shadow:{T['shadow']};
        transition:transform .18s ease, border-color .18s ease; height:100%; }}
.card:hover {{ transform:translateY(-2px); border-color:{T['accent']}; }}
.card .v {{ font-family:'JetBrains Mono',monospace; font-size:27px; font-weight:700; line-height:1; color:{T['accent']} !important; }}
.card .l {{ font-size:11px; color:{T['muted']} !important; text-transform:uppercase; letter-spacing:1px; margin-top:8px; font-weight:600; }}
.card .d {{ font-size:11px; margin-top:5px; font-weight:600; }}

.money {{ background:{T['money_bg']}; border:1px solid {T['border']}; border-radius:14px; padding:16px 14px; text-align:center; box-shadow:{T['shadow']}; height:100%; }}
.money .v {{ font-family:'JetBrains Mono',monospace; font-size:23px; font-weight:700; color:{T['accent_soft']} !important; line-height:1; }}
.money .l {{ font-size:11px; color:#c7cbe0 !important; text-transform:uppercase; letter-spacing:1px; margin-top:8px; font-weight:600; }}
.money .s {{ font-size:10.5px; color:#9aa1c4 !important; margin-top:4px; font-family:'JetBrains Mono',monospace; }}

/* pills */
.pill {{ display:flex; align-items:center; gap:9px; border-radius:11px; padding:10px 14px; margin:5px 0; font-size:13px; font-weight:500;
        border:1px solid {T['border']}; background:{T['panel2']}; color:{T['text']} !important; }}
.pill .g {{ font-size:12px; }}
.pill.bad  {{ border-left:4px solid {T['bad']};  }}
.pill.bad .g  {{ color:{T['bad']}; }}
.pill.warn {{ border-left:4px solid {T['warn']}; }}
.pill.warn .g {{ color:{T['warn']}; }}
.pill.good {{ border-left:4px solid {T['good']}; }}
.pill.good .g {{ color:{T['good']}; }}

/* boxes */
.box {{ background:{T['panel']}; border:1px solid {T['border']}; border-radius:14px; padding:15px 19px; box-shadow:{T['shadow']}; }}
.box.accent {{ border-left:4px solid {T['accent']}; }}
.box h4 {{ font-family:'Sora',sans-serif; margin:0 0 8px 0; font-size:14.5px; color:{T['text']} !important; }}
.box ul {{ margin:0; padding-left:18px; }}
.box li {{ margin:5px 0; color:{T['text']} !important; font-size:13px; line-height:1.45; opacity:0.92; }}
.box p  {{ color:{T['text']} !important; font-size:13px; margin:0; line-height:1.5; }}

.tag {{ display:inline-block; background:{T['panel2']}; border:1px solid {T['border']};
       color:{T['accent_soft']} !important; border-radius:20px; padding:5px 12px; margin:4px 4px 0 0; font-size:12px; font-weight:600;
       font-family:'JetBrains Mono',monospace; }}

/* footer */
.ft {{ text-align:center; margin-top:22px; padding:14px; border-top:1px solid {T['border']}; }}
.ft .name {{ font-family:'Sora',sans-serif; font-weight:700; font-size:12.5px; color:{T['text']} !important; }}
.ft .name span {{ color:{T['accent']} !important; }}
.ft .meta {{ font-size:10.5px; color:{T['muted']} !important; margin-top:3px; letter-spacing:0.4px; }}

/* sidebar */
[data-testid="stSidebar"] {{ background:{T['panel']} !important; border-right:1px solid {T['border']}; }}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label {{ color:{T['text']} !important; }}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] p {{ color:{T['muted']} !important; }}
.sgroup {{ font-family:'Sora',sans-serif; font-size:11px; font-weight:700; letter-spacing:1px;
          text-transform:uppercase; color:{T['accent']} !important; margin:14px 0 2px 2px; }}
.stProgress > div > div > div > div {{ background:{T['accent']} !important; }}
div[role="radiogroup"] {{ gap:4px; }}
div[role="radiogroup"] label {{ font-size:12px !important; }}
</style>
""", unsafe_allow_html=True)


def style_fig(fig, T: dict, height: int = 300):
    """Apply the active theme to a Plotly figure."""
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", color=T["muted"], size=12),
        title_font=dict(family="Sora, sans-serif", color=T["text"], size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["muted"])),
        xaxis=dict(gridcolor=T["grid"], zerolinecolor=T["grid"]),
        yaxis=dict(gridcolor=T["grid"], zerolinecolor=T["grid"]),
        colorway=[T["accent"], T["good"], T["bad"], T["warn"], T["accent_soft"]],
    )
    return fig
