"""H-E1: Correlation Analysis - Pearson, Bootstrap CI, Partial Correlation"""

import json
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple

from config import (
    SEED, N_BOOTSTRAP, R_THRESHOLD, P_THRESHOLD,
    BOOTSTRAP_CI_EXCLUDES, PARTIAL_R_THRESHOLD,
    RESULTS_PATH, ANALYSIS_PATH
)


def pearson_correlation(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Compute Pearson correlation. Returns (r, p_value)."""
    x_clean = []
    y_clean = []
    for xi, yi in zip(x, y):
        if not (np.isnan(xi) or np.isnan(yi)):
            x_clean.append(xi)
            y_clean.append(yi)

    if len(x_clean) < 3:
        return np.nan, np.nan

    r, p = stats.pearsonr(x_clean, y_clean)
    return float(r), float(p)


def bootstrap_ci(
    x: List[float],
    y: List[float],
    n_boot: int = N_BOOTSTRAP,
    seed: int = SEED
) -> Tuple[Tuple[float, float], List[float]]:
    """Bootstrap resample pairs, recompute r each time. Returns ((ci_low, ci_high), bootstrap_rs)."""
    x_arr = np.array(x)
    y_arr = np.array(y)

    mask = ~(np.isnan(x_arr) | np.isnan(y_arr))
    x_clean = x_arr[mask]
    y_clean = y_arr[mask]

    n = len(x_clean)
    if n < 3:
        return (np.nan, np.nan), []

    rng = np.random.default_rng(seed)
    boot_rs = []

    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        r, _ = stats.pearsonr(x_clean[idx], y_clean[idx])
        boot_rs.append(r)

    ci_low, ci_high = np.percentile(boot_rs, [2.5, 97.5])
    return (float(ci_low), float(ci_high)), boot_rs


def partial_correlation(
    x: List[float],
    y: List[float],
    control: List[float]
) -> Tuple[float, float]:
    """Residualize x, y on control via linear regression, correlate residuals."""
    x_arr = np.array(x)
    y_arr = np.array(y)
    c_arr = np.array(control)

    mask = ~(np.isnan(x_arr) | np.isnan(y_arr) | np.isnan(c_arr))
    x_clean = x_arr[mask]
    y_clean = y_arr[mask]
    c_clean = c_arr[mask].reshape(-1, 1)

    if len(x_clean) < 4:
        return np.nan, np.nan

    lr = LinearRegression()

    lr.fit(c_clean, x_clean)
    resid_x = x_clean - lr.predict(c_clean)

    lr.fit(c_clean, y_clean)
    resid_y = y_clean - lr.predict(c_clean)

    partial_r, partial_p = stats.pearsonr(resid_x, resid_y)
    return float(partial_r), float(partial_p)


def evaluate_hypothesis(results: Dict) -> Dict:
    """Combine all analyses. Returns full analysis dict with gate evaluation."""
    mc1 = results["mc1_acc"]
    robustness = results["robustness"]
    log_params = results["log_params"]

    r, p_value = pearson_correlation(mc1, robustness)

    (ci_low, ci_high), bootstrap_rs = bootstrap_ci(mc1, robustness)

    partial_r, partial_p = partial_correlation(mc1, robustness, log_params)

    gate_passed = (
        r > R_THRESHOLD and
        p_value < P_THRESHOLD
    )

    ci_excludes_threshold = ci_low > BOOTSTRAP_CI_EXCLUDES
    partial_r_passes = partial_r > PARTIAL_R_THRESHOLD if not np.isnan(partial_r) else False

    n_valid = sum(1 for m, rob in zip(mc1, robustness)
                  if not (np.isnan(m) or np.isnan(rob)))

    analysis = {
        "n_models": n_valid,
        "pearson_r": r,
        "p_value": p_value,
        "ci_95": [ci_low, ci_high],
        "partial_r": partial_r,
        "partial_p": partial_p,
        "gate_thresholds": {
            "r_threshold": R_THRESHOLD,
            "p_threshold": P_THRESHOLD,
            "bootstrap_ci_excludes": BOOTSTRAP_CI_EXCLUDES,
            "partial_r_threshold": PARTIAL_R_THRESHOLD
        },
        "gate_checks": {
            "r_passes": r > R_THRESHOLD,
            "p_passes": p_value < P_THRESHOLD,
            "ci_excludes_threshold": ci_excludes_threshold,
            "partial_r_passes": partial_r_passes
        },
        "gate_passed": gate_passed,
        "gate_result": "PASS" if gate_passed else "FAIL",
        "gate_action": determine_gate_action(r, p_value),
        "bootstrap_rs": bootstrap_rs
    }

    return analysis


def determine_gate_action(r: float, p_value: float) -> str:
    """Determine action based on gate result."""
    if np.isnan(r):
        return "INCOMPLETE - insufficient data"
    elif r > R_THRESHOLD and p_value < P_THRESHOLD:
        return "PROCEED to H-M1 (mechanism hypothesis)"
    elif r < 0.3:
        return "ABANDON - hypothesis fundamentally wrong (r < 0.3)"
    else:
        return "PIVOT - weak correlation, investigate confounds (0.3 < r < 0.5)"


def save_analysis(analysis: Dict, path: str = ANALYSIS_PATH) -> None:
    """Save analysis to JSON file."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)

    analysis_save = {k: v for k, v in analysis.items() if k != "bootstrap_rs"}

    with open(path, 'w') as f:
        json.dump(analysis_save, f, indent=2)

    print(f"Analysis saved to {path}")


def load_results(path: str = RESULTS_PATH) -> Dict:
    """Load results from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def print_analysis_summary(analysis: Dict) -> None:
    """Print human-readable analysis summary."""
    print("\n" + "=" * 60)
    print("H-E1 HYPOTHESIS ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nModels analyzed: {analysis['n_models']}")
    print(f"\nPearson r: {analysis['pearson_r']:.4f}")
    print(f"p-value: {analysis['p_value']:.4f}")
    print(f"95% CI: [{analysis['ci_95'][0]:.4f}, {analysis['ci_95'][1]:.4f}]")
    print(f"Partial r (controlling for log params): {analysis['partial_r']:.4f}")
    print(f"\nGate Result: {analysis['gate_result']}")
    print(f"Action: {analysis['gate_action']}")
    print("=" * 60)


if __name__ == "__main__":
    results = load_results()
    analysis = evaluate_hypothesis(results)
    save_analysis(analysis)
    print_analysis_summary(analysis)
