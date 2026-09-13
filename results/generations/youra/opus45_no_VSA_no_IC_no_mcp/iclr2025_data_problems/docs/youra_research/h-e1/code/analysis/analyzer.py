"""Polynomial regression + AIC model selection for dose-response analysis."""

import os
import json
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANALYSIS_CONFIG
from eval import compute_ensemble_score


def fit_polynomial(x: np.ndarray, y: np.ndarray, degree: int) -> dict:
    """Fit polynomial regression and compute AIC."""
    X_poly = PolynomialFeatures(degree).fit_transform(x.reshape(-1, 1))
    model = LinearRegression().fit(X_poly, y)
    y_pred = model.predict(X_poly)

    n = len(y)
    k = degree + 1
    rss = np.sum((y - y_pred) ** 2)
    aic = n * np.log(rss / n + 1e-10) + 2 * k

    return {
        "degree": degree,
        "aic": aic,
        "model": model,
        "coef": model.coef_.tolist(),
        "intercept": float(model.intercept_),
        "r2": float(model.score(X_poly, y)),
    }


def fit_and_select(x: np.ndarray, y: np.ndarray, max_degree: int = 3) -> dict:
    """Fit polynomials degree 1-max_degree, select by AIC."""
    best = None
    all_fits = []

    for degree in range(1, max_degree + 1):
        fit = fit_polynomial(x, y, degree)
        all_fits.append(fit)
        if best is None or fit["aic"] < best["aic"]:
            best = fit

    best["all_fits"] = [{k: v for k, v in f.items() if k != "model"} for f in all_fits]
    return best


def find_peak(coef: list, x_range: tuple, degree: int) -> float:
    """Find interior maximum of polynomial."""
    if degree < 2:
        return None

    poly_coef = [coef[0]] + list(coef[1:])
    deriv_coef = [i * poly_coef[i] for i in range(1, len(poly_coef))]

    if len(deriv_coef) < 2:
        return None

    if degree == 2:
        if abs(deriv_coef[1]) < 1e-10:
            return None
        root = -deriv_coef[0] / (2 * deriv_coef[1])
        if x_range[0] < root < x_range[1] and deriv_coef[1] < 0:
            return float(root)
        return None

    roots = np.roots(deriv_coef[::-1])
    real_roots = [r.real for r in roots if abs(r.imag) < 1e-10]
    interior = [r for r in real_roots if x_range[0] < r < x_range[1]]

    if not interior:
        return None

    second_deriv = [i * deriv_coef[i] for i in range(1, len(deriv_coef))]
    for r in interior:
        if sum(c * (r ** i) for i, c in enumerate(second_deriv)) < 0:
            return float(r)
    return None


def analyze(results: dict, fig_dir: str = "figures/") -> dict:
    """Run full dose-response analysis."""
    all_scores = {cid: res["scores"] for cid, res in results.items()}
    ensemble_scores = compute_ensemble_score(all_scores)

    perp_configs = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    x_perp = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], dtype=float)
    y_perp = np.array([ensemble_scores.get(c, 0) for c in perp_configs])

    dedup_configs = ["D0", "D1", "D2", "D3", "D4"]
    x_dedup = np.array([0, 1, 2, 3, 4], dtype=float)
    y_dedup = np.array([ensemble_scores.get(c, 0) for c in dedup_configs])

    perp_fit = fit_and_select(x_perp, y_perp)
    perp_peak = find_peak(perp_fit["coef"], (0, 90), perp_fit["degree"])

    dedup_fit = fit_and_select(x_dedup, y_dedup)
    dedup_peak = find_peak(dedup_fit["coef"], (0, 4), dedup_fit["degree"])

    analysis_results = {
        "perplexity": {
            "x": x_perp.tolist(),
            "y": y_perp.tolist(),
            "fit": {k: v for k, v in perp_fit.items() if k != "model"},
            "peak": perp_peak,
            "is_concave": perp_fit["degree"] >= 2 and perp_peak is not None,
        },
        "dedup": {
            "x": x_dedup.tolist(),
            "y": y_dedup.tolist(),
            "fit": {k: v for k, v in dedup_fit.items() if k != "model"},
            "peak": dedup_peak,
            "is_concave": dedup_fit["degree"] >= 2 and dedup_peak is not None,
        },
        "ensemble_scores": ensemble_scores,
    }

    return analysis_results


def run_analysis(results_path: str = "results/all_configs.json", fig_dir: str = "figures/") -> dict:
    """Load results and run analysis."""
    with open(results_path, "r") as f:
        results = json.load(f)
    return analyze(results, fig_dir)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/all_configs.json")
    parser.add_argument("--fig-dir", default="figures/")
    args = parser.parse_args()

    analysis = run_analysis(args.results, args.fig_dir)
    print(json.dumps(analysis, indent=2))
