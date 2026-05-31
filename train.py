"""Train, evaluate, and persist the churn model artifact.

Usage:  python train.py
Produces models/churn_pipeline.joblib (loaded by the Streamlit app at runtime).
Re-run whenever the dataset or feature logic changes.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "app"))

from lib import pipeline as P  # noqa: E402


def main() -> None:
    print("Training on", P.DATA_PATH)
    cm = P.train()
    print(f"Trained on {cm.n_rows:,} rows. Held-out metrics:")
    for k, v in cm.metrics.items():
        print(f"  {k:10s} {v:.4f}" if isinstance(v, float) else f"  {k:10s} {v}")
    path = P.save(cm)
    print("Saved artifact ->", path)


if __name__ == "__main__":
    main()
