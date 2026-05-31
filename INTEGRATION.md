# Rebuilt App — Integration Guide

A multipage Streamlit app (Overview · Risk Scorer · Batch Scoring) that replaces the single-file `app/app.py`. Every page is wired to real data and the real model; tested headless before shipping.

## What's in this bundle
```
app/
  app.py              # entry point: theme toggle + st.navigation (3 pages)
  lib/
    config.py         # currency, risk bands, copy
    theme.py          # dual palette + CSS + Plotly styling
    data.py           # cached CSV load, KPIs, segment aggregates
    pipeline.py       # build_features / train / save / load / predict  ← core
    ui.py             # reusable card/pill/section/header/footer helpers
  views/
    overview.py       # live KPIs + Plotly segment charts + data findings
    scorer.py         # single-customer score + SHAP + what-if + action plan
    batch.py          # upload CSV → score all → summary + download
train.py              # builds models/churn_pipeline.joblib (run once)
models/churn_pipeline.joblib   # persisted, evaluated model (loads in ~15ms)
data/European_Bank.csv         # unchanged from your repo
.streamlit/config.toml         # native base theme (replaces config_for_download.toml)
requirements.txt               # pinned to the exact tested versions
runtime.txt                    # 3.11 (trailing space removed)
.gitignore                     # real one (your README claimed one that didn't exist)
```

## How to drop it into your repo
1. **Delete** the old `app/app.py` and `config_for_download.toml`.
2. **Copy in** everything from this bundle (the `app/`, `models/`, `.streamlit/` dirs, `train.py`, and the updated `requirements.txt` / `runtime.txt` / `.gitignore`).
3. Commit the `models/churn_pipeline.joblib` artifact (it's ~480 KB).
4. Update the README "Repository Structure" block to match (the old one listed wrong paths).
5. Push. Streamlit Cloud entry point stays `app/app.py`, so your existing deployment config is unchanged.

To retrain after changing the data or feature logic:
```bash
python train.py        # re-evaluates on a held-out split and re-saves the artifact
```

## Run locally
```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## What changed vs. the old app (the fixes from the audit)
- **Train/serve skew removed.** Features are defined once in `build_features()` and reused by training, single-row, and batch scoring — so the `Product_Density` mismatch is structurally impossible. Verified: single-row and batch produce byte-identical probabilities.
- **Real metrics, not hardcoded.** `train.py` evaluates on a 2,000-row held-out split and stores the numbers in the artifact. The app displays *those*. Verified: **ROC-AUC 0.864 · Accuracy 85.4% · Recall 60.4% @ 0.35**. (Your old "60% recall" claim was actually right; the notebook's "50%" was a different variant.)
- **Real model persistence.** `joblib` now does something: `train.py` saves, the app loads in ~15 ms, with a graceful retrain-on-load fallback if the pickle is ever unreadable.
- **SHAP is now real.** The Scorer shows per-customer SHAP contributions (top drivers, ▲ raises / ▼ lowers), so the footer claim is true.
- **Scaler dropped on purpose.** GradientBoosting is scale-invariant, so the StandardScaler only added the skew bug and made SHAP unreadable. Removing it keeps SHAP in real units.
- **Dead code/deps gone.** No unused `numpy`/`matplotlib`/`seaborn` imports; `requirements.txt` pinned to tested versions; viz now actually uses Plotly.
- **README claims now match the app.** The Overview page *is* the executive dashboard (live KPIs, geographic/product/age/gender charts, balance distribution) your README always described.
- **Currency consistent (€).** No more £/€ mismatch.
- **Accessibility nudges.** Risk is shown by glyph + word + colour (not colour alone); base font sizes lifted off the 10–11px floor.

## Verified before shipping
All three pages were run headless with Streamlit's `AppTest`: zero exceptions on Overview, Risk Scorer (incl. SHAP), and Batch Scoring (incl. a full 200-row scoring run), in both dark and light themes.
