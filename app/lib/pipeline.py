"""
Churn model pipeline — a single source of truth for features, training,
persistence, and inference.

Design notes
------------
* Engineered features are built from RAW values (not z-scored), so SHAP
  attributions read in real units ("Age = 58 pushed churn up").
* GradientBoosting is invariant to monotonic feature scaling, so the
  StandardScaler used in the original notebook added a train/serve skew bug
  (Product_Density was built from scaled Tenure at train time but raw Tenure
  at serve time) without improving the model. It is removed here.
* `build_features` is the ONLY place features are defined, and it is reused
  by training, single-row scoring, and batch scoring — so train/serve skew
  is structurally impossible.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

# --- paths -----------------------------------------------------------------
LIB_DIR = pathlib.Path(__file__).resolve().parent
APP_DIR = LIB_DIR.parent
ROOT_DIR = APP_DIR.parent
DATA_PATH = ROOT_DIR / "data" / "European_Bank.csv"
MODEL_PATH = ROOT_DIR / "models" / "churn_pipeline.joblib"

# --- schema ----------------------------------------------------------------
GEOGRAPHIES = ["France", "Germany", "Spain"]
GENDERS = ["Female", "Male"]
RAW_INPUTS = [
    "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "EstimatedSalary", "Geography", "Gender",
]
# Fixed model feature order (built once at train time, reused at inference).
FEATURE_ORDER = [
    "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "EstimatedSalary",
    "Geography_France", "Geography_Germany", "Geography_Spain",
    "Gender_Female", "Gender_Male",
    "Balance_Salary_Ratio", "Age_Tenure_Interaction",
    "Product_Density", "Engagement_Score",
]
DEFAULT_THRESHOLD = 0.35

GB_PARAMS = dict(
    n_estimators=200, learning_rate=0.08, max_depth=4,
    subsample=0.9, random_state=42,
)


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Turn raw customer rows into the model feature matrix.

    `raw` must contain the RAW_INPUTS columns. Works for one row or many.
    Returns a frame with columns in FEATURE_ORDER (missing one-hots -> 0).
    """
    df = raw.copy()
    # one-hot the categoricals
    df["Geography"] = pd.Categorical(df["Geography"], categories=GEOGRAPHIES)
    df["Gender"] = pd.Categorical(df["Gender"], categories=GENDERS)
    df = pd.get_dummies(df, columns=["Geography", "Gender"], dtype=int)

    # engineered features — from RAW values, so they stay interpretable
    df["Balance_Salary_Ratio"] = df["Balance"] / (df["EstimatedSalary"] + 1)
    df["Age_Tenure_Interaction"] = df["Age"] * df["Tenure"]
    df["Product_Density"] = df["NumOfProducts"] / (df["Tenure"] + 1)
    df["Engagement_Score"] = (
        df["IsActiveMember"] * (df["NumOfProducts"] / 4) * (df["HasCrCard"] + 1)
    )
    # guarantee column presence + order
    return df.reindex(columns=FEATURE_ORDER, fill_value=0)


@dataclass
class ChurnModel:
    """Trained model + the metadata the app needs to be honest about it."""
    model: GradientBoostingClassifier
    metrics: dict = field(default_factory=dict)
    threshold: float = DEFAULT_THRESHOLD
    feature_order: list = field(default_factory=lambda: list(FEATURE_ORDER))
    n_rows: int = 0

    # -- inference ----------------------------------------------------------
    def predict_proba(self, raw: pd.DataFrame) -> np.ndarray:
        X = build_features(raw)[self.feature_order]
        return self.model.predict_proba(X)[:, 1]

    def score_one(self, **kwargs) -> float:
        return float(self.predict_proba(pd.DataFrame([kwargs]))[0])

    def score_batch(self, raw: pd.DataFrame, threshold: float | None = None) -> pd.DataFrame:
        thr = self.threshold if threshold is None else threshold
        proba = self.predict_proba(raw)
        out = raw.copy()
        out["Churn_Probability"] = proba.round(4)
        out["Prediction"] = np.where(proba >= thr, "Will Churn", "Will Stay")
        out["Balance_at_Risk"] = (proba * raw["Balance"]).round(0)
        return out


def _evaluate(model, X_te, y_te, threshold: float) -> dict:
    proba = model.predict_proba(X_te)[:, 1]
    pred = (proba >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_te, proba)),
        "accuracy": float(accuracy_score(y_te, pred)),
        "precision": float(precision_score(y_te, pred, zero_division=0)),
        "recall": float(recall_score(y_te, pred, zero_division=0)),
        "f1": float(f1_score(y_te, pred, zero_division=0)),
        "threshold": float(threshold),
        "test_n": int(len(y_te)),
    }


def train(data_path: pathlib.Path = DATA_PATH,
          threshold: float = DEFAULT_THRESHOLD) -> ChurnModel:
    """Train on the dataset and evaluate on a held-out split. The metrics
    returned are the metrics of THIS model — no hardcoding."""
    df = pd.read_csv(data_path)
    # 'Year' is a constant synthetic column; drop identifiers + target
    drop_cols = [c for c in ["Year", "CustomerId", "Surname", "RowNumber"] if c in df.columns]
    y = df["Exited"].astype(int)
    raw = df.drop(columns=drop_cols + ["Exited"])

    X = build_features(raw)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = GradientBoostingClassifier(**GB_PARAMS).fit(X_tr, y_tr)
    metrics = _evaluate(model, X_te, y_te, threshold)
    return ChurnModel(model=model, metrics=metrics, threshold=threshold,
                      feature_order=list(FEATURE_ORDER), n_rows=len(df))


def save(cm: ChurnModel, path: pathlib.Path = MODEL_PATH) -> pathlib.Path:
    import joblib
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(cm, path)
    return path


def load(path: pathlib.Path = MODEL_PATH) -> ChurnModel:
    """Load the persisted artifact; fall back to a fresh train if the file is
    missing or unreadable (e.g. a sklearn version mismatch on the host). This
    keeps the deployed app from ever hard-crashing on a stale pickle."""
    import joblib
    try:
        if path.exists():
            return joblib.load(path)
    except Exception:
        pass
    return train()
