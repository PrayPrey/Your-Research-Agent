"""Model fitting: linear and 3-parameter logistic growth."""
import warnings
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning


def _r2_aic(y: np.ndarray, y_pred: np.ndarray, k: int) -> tuple[float, float]:
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    n = len(y)
    aic = n * np.log(ss_res / n) + 2 * k if ss_res > 0 and n > 0 else float("inf")
    return r2, aic


def logistic(t: np.ndarray, K: float, r: float, t0: float) -> np.ndarray:
    """3-parameter logistic: K / (1 + exp(-r*(t-t0))) with overflow guard."""
    exponent = np.clip(-r * (t - t0), -500, 500)
    return K / (1.0 + np.exp(exponent))


def fit_linear(t: np.ndarray, y: np.ndarray) -> dict:
    """Fit degree-1 polynomial; compute R² and AIC (k=2)."""
    coeffs = np.polyfit(t, y, deg=1)
    y_pred = np.polyval(coeffs, t)
    r2, aic = _r2_aic(y, y_pred, k=2)
    return {"coeffs": coeffs, "r2": r2, "aic": aic}


def fit_logistic(t: np.ndarray, y: np.ndarray) -> dict:
    """Fit logistic via curve_fit; return params, CI, R², AIC, convergence flag."""
    # Allow negative t0: inflection point may precede observation window
    # (GLUE/SuperGLUE had pre-release BERT results — inflection ~month -5 to +15)
    p0 = [0.9, 0.5, float(np.median(t) * 0.3)]  # initial guess near early growth
    bounds = ([0.8, 0.01, -20.0], [1.05, 5.0, 60.0])
    converged = False
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            popt, pcov = curve_fit(
                logistic, t, y, p0=p0, bounds=bounds, maxfev=10000
            )
        converged = not any(issubclass(x.category, OptimizeWarning) for x in w)
    except RuntimeError:
        popt = np.full(3, np.nan)
        pcov = np.full((3, 3), np.nan)
        converged = False

    ci95 = 1.96 * np.sqrt(np.diag(pcov))
    if converged:
        y_pred = logistic(t, *popt)
        r2, aic = _r2_aic(y, y_pred, k=3)
    else:
        r2, aic = float("nan"), float("nan")

    return {
        "popt": popt,
        "pcov": pcov,
        "r2": r2,
        "aic": aic,
        "ci95": ci95,
        "converged": converged,
    }
