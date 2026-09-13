"""baseline.py — Naive feature extraction and logistic regression baseline for H-E1."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


def extract_naive_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Extract naive features per benchmark for saturation classification."""
    results = []

    for benchmark in panel["benchmark"].unique():
        bdf = panel[panel["benchmark"] == benchmark].copy()
        label = bdf["label"].mode()[0] if len(bdf) > 0 else "excluded"

        scores = bdf["score"].values

        # Feature 1: score variance over last 4 quarters
        quarters = sorted(bdf["quarter"].unique())
        last_4q = quarters[-4:] if len(quarters) >= 4 else quarters
        last4_scores = bdf[bdf["quarter"].isin(last_4q)]["score"].values
        score_variance_last_4q = float(np.var(last4_scores)) if len(last4_scores) > 1 else 0.0

        # Feature 2: improvement slope (linear trend of best score per quarter)
        if len(quarters) >= 2:
            best_per_quarter = [
                bdf[bdf["quarter"] == q]["score"].max() for q in quarters
            ]
            x = np.arange(len(best_per_quarter), dtype=float)
            y = np.array(best_per_quarter)
            if len(x) > 1:
                slope = float(np.polyfit(x, y, 1)[0])
            else:
                slope = 0.0
        else:
            slope = 0.0
        improvement_slope = slope

        # Feature 3: benchmark age in months
        if "date" in bdf.columns and bdf["date"].notna().any():
            min_date = bdf["date"].dropna().min()
            max_date = bdf["date"].dropna().max()
            benchmark_age_months = float((max_date - min_date).days / 30.0)
        else:
            benchmark_age_months = float(len(quarters) * 3)

        results.append({
            "benchmark": benchmark,
            "label": label,
            "score_variance_last_4q": score_variance_last_4q,
            "improvement_slope": improvement_slope,
            "benchmark_age_months": benchmark_age_months,
        })

    return pd.DataFrame(results)


def fit_baseline(
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> LogisticRegression:
    """Fit logistic regression with balanced class weights."""
    model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    return model


def predict_baseline(
    model: LogisticRegression,
    X: np.ndarray,
) -> np.ndarray:
    """Return predicted probabilities for saturated class (class=1)."""
    proba = model.predict_proba(X)
    # Return probability for positive class
    classes = list(model.classes_)
    if 1 in classes:
        idx = classes.index(1)
    else:
        idx = -1
    return proba[:, idx]
