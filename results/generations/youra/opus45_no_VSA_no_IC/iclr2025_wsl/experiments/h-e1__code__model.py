"""Ridge regression baseline model."""
import numpy as np
from sklearn.linear_model import RidgeCV
from typing import List
import config


def fit_ridge(
    X_train: np.ndarray,
    y_train: np.ndarray,
    alphas: List[float] = config.ALPHAS
) -> RidgeCV:
    """Fit RidgeCV with cross-validation for alpha selection."""
    model = RidgeCV(alphas=alphas, cv=config.CV_FOLDS)
    model.fit(X_train, y_train)
    return model


def evaluate(model: RidgeCV, X_test: np.ndarray, y_test: np.ndarray) -> float:
    """Evaluate model on test set, return R² score."""
    return float(model.score(X_test, y_test))
