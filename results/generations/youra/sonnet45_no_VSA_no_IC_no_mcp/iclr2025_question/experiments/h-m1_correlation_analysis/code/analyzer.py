"""Statistical correlation analyzer."""

from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np
from typing import List, Tuple


class CorrelationAnalyzer:
    """Compute Pearson correlation and linear regression."""

    def compute_pearson(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """
        Compute Pearson correlation.
        Returns: (r, p_value)
        """
        r, p = pearsonr(x, y)
        return r, p

    def fit_linear_regression(
        self,
        x: List[float],
        y: List[float]
    ) -> Tuple[float, float, List[float]]:
        """
        Fit y = k*x linear model.
        Returns: (k, r2, residuals)
        """
        X = np.array(x).reshape(-1, 1)  # [N, 1]
        Y = np.array(y)  # [N]

        model = LinearRegression()
        model.fit(X, Y)

        k = model.coef_[0]  # Scaling factor
        y_pred = model.predict(X)  # [N]
        r2 = r2_score(Y, y_pred)
        residuals = (Y - y_pred).tolist()  # [N]

        return k, r2, residuals

    def compute_cv(self, values: List[float]) -> float:
        """
        Coefficient of variation.
        cv = std / mean
        """
        arr = np.array(values)
        return float(np.std(arr) / np.mean(arr))
