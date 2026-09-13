"""Regression analysis for gate check (R² >0.6)."""
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from typing import Tuple, Dict, List


def fit_regression(
    X: pd.DataFrame,
    y: pd.Series
) -> Tuple[float, Dict[str, float], List[float]]:
    """Fit linear regression: syntax% ~ task_features. Returns (R², coefficients, cv_scores)."""
    model = LinearRegression()
    model.fit(X, y)

    r_squared = model.score(X, y)
    coefficients = dict(zip(X.columns, model.coef_))
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2').tolist()

    return r_squared, coefficients, cv_scores


def gate_decision(r_squared: float, threshold: float = 0.6) -> str:
    """Gate check. Returns 'PASS' | 'FAIL'."""
    return 'PASS' if r_squared > threshold else 'FAIL'
