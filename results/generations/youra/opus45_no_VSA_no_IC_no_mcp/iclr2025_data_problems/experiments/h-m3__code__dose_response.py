"""Dose-response analysis for optimal threshold identification."""
import numpy as np
import statsmodels.api as sm
from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class DoseResponseResult:
    optimal_threshold: float
    optimal_score: float
    confidence_interval: Tuple[float, float]
    best_model: str
    aic_values: Dict[str, float]
    bic_values: Dict[str, float]
    is_peak_internal: bool
    model_coefficients: Dict[str, np.ndarray] = None

def fit_polynomial_models(
    thresholds: np.ndarray,
    scores: np.ndarray
) -> Dict[str, dict]:
    """Fit linear/quadratic/cubic OLS models."""
    x = thresholds / 100.0
    results = {}
    for degree, name in [(1, 'linear'), (2, 'quadratic'), (3, 'cubic')]:
        X = np.vander(x, degree + 1)
        model = sm.OLS(scores, X).fit()
        results[name] = {
            'coefficients': model.params,
            'aic': model.aic,
            'bic': model.bic,
            'rsquared': model.rsquared
        }
    return results

def find_optimal_threshold(
    thresholds: np.ndarray,
    scores: np.ndarray,
    model_coeffs: np.ndarray,
    degree: int
) -> Tuple[float, float, bool]:
    """Derivative-based peak search."""
    if degree == 1:
        idx = np.argmax(scores)
        return float(thresholds[idx]), float(scores[idx]), False

    poly = np.poly1d(model_coeffs)
    deriv = np.polyder(poly)
    critical = np.roots(deriv)
    critical = critical[np.isreal(critical)].real
    critical = critical[(critical >= 0) & (critical <= 1)]

    if len(critical) == 0:
        idx = np.argmax(scores)
        return float(thresholds[idx]), float(scores[idx]), False

    candidates = np.concatenate([[0], critical, [1]])
    values = poly(candidates)
    best_idx = np.argmax(values)
    optimal_x = candidates[best_idx]
    is_internal = (optimal_x > 0.05) and (optimal_x < 0.95)
    return float(optimal_x * 100), float(values[best_idx]), is_internal

def compute_confidence_interval(
    thresholds: np.ndarray,
    scores_matrix: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> Tuple[float, float]:
    """Bootstrap CI for optimal threshold."""
    np.random.seed(seed)
    n_thresholds, n_seeds = scores_matrix.shape
    optimal_thresholds = []

    for _ in range(n_bootstrap):
        seed_idx = np.random.choice(n_seeds, n_seeds, replace=True)
        resampled = scores_matrix[:, seed_idx].mean(axis=1)
        idx = np.argmax(resampled)
        optimal_thresholds.append(thresholds[idx])

    lower = np.percentile(optimal_thresholds, 2.5)
    upper = np.percentile(optimal_thresholds, 97.5)
    return float(lower), float(upper)

def analyze_dose_response(
    sweep_results: Dict[float, dict]
) -> DoseResponseResult:
    """Full analysis pipeline."""
    thresholds = np.array(sorted(sweep_results.keys()))
    scores_matrix = np.array([sweep_results[t]['scores'] for t in thresholds])
    mean_scores = scores_matrix.mean(axis=1)

    models = fit_polynomial_models(thresholds, mean_scores)
    best_name = min(models.keys(), key=lambda k: models[k]['bic'])
    best_model = models[best_name]
    degree = {'linear': 1, 'quadratic': 2, 'cubic': 3}[best_name]

    optimal_t, optimal_s, is_internal = find_optimal_threshold(
        thresholds, mean_scores, best_model['coefficients'], degree
    )
    ci = compute_confidence_interval(thresholds, scores_matrix)

    return DoseResponseResult(
        optimal_threshold=optimal_t,
        optimal_score=optimal_s,
        confidence_interval=ci,
        best_model=best_name,
        aic_values={k: v['aic'] for k, v in models.items()},
        bic_values={k: v['bic'] for k, v in models.items()},
        is_peak_internal=is_internal,
        model_coefficients={k: v['coefficients'] for k, v in models.items()}
    )

def verify_optimal_balance_point(result: DoseResponseResult) -> bool:
    """Verify H-M3 success criteria."""
    print(f"\n=== H-M3 Verification ===")
    print(f"Optimal threshold: p{result.optimal_threshold:.0f}")
    print(f"Optimal score: {result.optimal_score:.4f}")
    print(f"95% CI: [{result.confidence_interval[0]:.0f}, {result.confidence_interval[1]:.0f}]")
    print(f"Best model: {result.best_model}")
    print(f"Is peak internal: {result.is_peak_internal}")

    ci_width = result.confidence_interval[1] - result.confidence_interval[0]
    print(f"CI width: {ci_width:.1f}")

    if not result.is_peak_internal:
        print("FAIL: Peak at boundary")
        return False
    if result.best_model == 'linear':
        print("FAIL: Linear model selected (no curvature)")
        return False
    if ci_width > 30:
        print(f"FAIL: CI too wide ({ci_width:.1f} > 30)")
        return False

    print("PASS: All criteria met")
    return True
