"""Tests for the churn model pipeline.

These guard the things that actually matter for this app:
  * features are built consistently (no train/serve skew),
  * predictions are valid probabilities,
  * the trained model meets a baseline quality bar.
"""
import pathlib
import sys

import pandas as pd

# make the app package importable
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from lib import pipeline as P  # noqa: E402

SAMPLE = dict(
    CreditScore=650, Age=45, Tenure=3, Balance=120000, NumOfProducts=2,
    HasCrCard=1, IsActiveMember=1, EstimatedSalary=100000,
    Geography="France", Gender="Female",
)


def _model():
    return P.load()


def test_build_features_has_expected_columns():
    feats = P.build_features(pd.DataFrame([SAMPLE]))
    assert list(feats.columns) == P.FEATURE_ORDER
    assert len(feats) == 1


def test_engineered_features_present():
    feats = P.build_features(pd.DataFrame([SAMPLE]))
    for col in ["Balance_Salary_Ratio", "Age_Tenure_Interaction",
                "Product_Density", "Engagement_Score"]:
        assert col in feats.columns


def test_prediction_is_a_valid_probability():
    p = _model().score_one(**SAMPLE)
    assert isinstance(p, float)
    assert 0.0 <= p <= 1.0


def test_no_train_serve_skew():
    """Single-row and batch scoring must give identical results."""
    m = _model()
    one = m.predict_proba(pd.DataFrame([SAMPLE]))[0]
    batch = m.predict_proba(pd.DataFrame([SAMPLE, SAMPLE, SAMPLE]))[0]
    assert one == batch


def test_high_risk_scores_higher_than_low_risk():
    """A clearly risky profile should score above a clearly safe one."""
    m = _model()
    high = m.score_one(**{**SAMPLE, "Age": 58, "NumOfProducts": 4,
                          "IsActiveMember": 0, "Geography": "Germany"})
    low = m.score_one(**{**SAMPLE, "Age": 30, "NumOfProducts": 2,
                         "IsActiveMember": 1, "Geography": "France"})
    assert high > low


def test_model_meets_quality_bar():
    """Held-out ROC-AUC should clear a sensible baseline."""
    m = _model()
    assert m.metrics["roc_auc"] > 0.80


def test_batch_scoring_outputs():
    m = _model()
    df = pd.DataFrame([SAMPLE] * 5)
    out = m.score_batch(df)
    assert "Churn_Probability" in out.columns
    assert "Prediction" in out.columns
    assert len(out) == 5
