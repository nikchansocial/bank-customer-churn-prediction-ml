"""Static configuration: paths, currency, and shared copy."""
from __future__ import annotations

APP_TITLE = "Churn Intelligence"
APP_TAGLINE = "Retail Banking · Predictive Retention Analytics"
CURRENCY = "€"

# Risk bands (probability cutoffs) -> (label, glyph, semantic key)
# Glyphs make risk legible without relying on colour alone (accessibility).
RISK_BANDS = [
    (0.60, "HIGH RISK", "●", "bad"),
    (0.30, "MEDIUM RISK", "▲", "warn"),
    (0.00, "LOW RISK", "■", "good"),
]


def risk_band(prob: float):
    for cutoff, label, glyph, key in RISK_BANDS:
        if prob >= cutoff:
            return label, glyph, key
    return RISK_BANDS[-1][1:]


AUTHOR = "Nikhil Chandrakar"
AUTHOR_HANDLE = "@nikchansocial"
