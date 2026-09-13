"""OLS regression analysis with bootstrap CI and LOO-CV for small-N."""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from m2_config import N_BOOTSTRAP, SEED, R2_PASS_THRESHOLD


class TemporalPredictionAnalyzer:
    """Analyze temporal DNSI → gap prediction with small-N methods."""

    def __init__(self, n_bootstrap: int = N_BOOTSTRAP, seed: int = SEED):
        self.n_bootstrap = n_bootstrap
        self.rng = np.random.default_rng(seed)

    def analyze(self, dnsi_pre: np.ndarray, gap_post: np.ndarray) -> dict:
        """Run OLS regression with bootstrap CI and LOO-CV."""
        n = len(dnsi_pre)
        if n < 2:
            return {"n": n, "error": "insufficient_data", "hypothesis_supported": False}

        X = dnsi_pre.reshape(-1, 1)
        y = gap_post

        model = LinearRegression().fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - 2) if n > 2 else float("nan")

        bootstrap_r2 = self._bootstrap_r2(dnsi_pre, gap_post)
        if bootstrap_r2.size > 0:
            ci_lower, ci_upper = np.percentile(bootstrap_r2, [2.5, 97.5])
        else:
            ci_lower, ci_upper = float("nan"), float("nan")

        loo_r2 = self._loo_cv(dnsi_pre, gap_post)

        return {
            "n": n,
            "r2": float(r2),
            "adj_r2": float(adj_r2),
            "loo_r2": float(loo_r2),
            "ci_95_lower": float(ci_lower),
            "ci_95_upper": float(ci_upper),
            "slope": float(model.coef_[0]),
            "intercept": float(model.intercept_),
            "hypothesis_supported": r2 > R2_PASS_THRESHOLD,
        }

    def _bootstrap_r2(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Bootstrap R² distribution."""
        n = len(x)
        r2_values = []
        for _ in range(self.n_bootstrap):
            idx = self.rng.integers(0, n, size=n)
            if len(np.unique(idx)) <= 1:
                continue
            X_boot = x[idx].reshape(-1, 1)
            y_boot = y[idx]
            model = LinearRegression().fit(X_boot, y_boot)
            r2 = r2_score(y_boot, model.predict(X_boot))
            if np.isfinite(r2):
                r2_values.append(r2)
        return np.array(r2_values)

    def _loo_cv(self, x: np.ndarray, y: np.ndarray) -> float:
        """Leave-one-out cross-validation R²."""
        n = len(x)
        preds = []
        actuals = []
        for i in range(n):
            X_train = np.delete(x, i).reshape(-1, 1)
            y_train = np.delete(y, i)
            model = LinearRegression().fit(X_train, y_train)
            preds.append(model.predict(x[i].reshape(1, -1))[0])
            actuals.append(y[i])
        preds = np.array(preds)
        actuals = np.array(actuals)
        ss_res = np.sum((actuals - preds) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
