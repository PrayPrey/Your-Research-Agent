"""Stratified correlation analysis: compute within-group partial correlations."""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from config import SEED, N_BOOTSTRAP, R_THRESHOLD, P_THRESHOLD


def residualize(v: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Residualize v against z using OLS."""
    coef = np.polyfit(z, v, deg=1)
    fitted = np.polyval(coef, z)
    return v - fitted


def partial_corr(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple:
    """Compute partial correlation of x,y controlling for z."""
    rx = residualize(x, z)
    ry = residualize(y, z)
    r, p = pearsonr(rx, ry)
    return r, p


def bootstrap_ci_group(
    df: pd.DataFrame,
    x_col: str = "truthfulqa_mc1",
    y_col: str = "advglue_avg",
    z_col: str = "log_params",
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    """Bootstrap CI for partial correlation within a group."""
    x = df[x_col].values
    y = df[y_col].values
    z = df[z_col].values
    n = len(x)

    if n < 4:
        return {
            "r": np.nan,
            "p": np.nan,
            "ci_lower": np.nan,
            "ci_upper": np.nan,
            "n": n,
            "gate_passed": False,
            "error": "insufficient_samples",
        }

    rng = np.random.default_rng(seed)
    r_obs, p_obs = partial_corr(x, y, z)

    bootstrap_rs = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        xb, yb, zb = x[idx], y[idx], z[idx]
        if len(np.unique(zb)) < 2:
            continue
        try:
            rb, _ = partial_corr(xb, yb, zb)
            bootstrap_rs.append(rb)
        except Exception:
            continue

    if len(bootstrap_rs) < 100:
        ci_lower, ci_upper = np.nan, np.nan
    else:
        ci_lower, ci_upper = np.percentile(bootstrap_rs, [2.5, 97.5])

    gate_passed = (
        not np.isnan(r_obs)
        and r_obs > R_THRESHOLD
        and p_obs < P_THRESHOLD
    )

    return {
        "r": float(r_obs),
        "p": float(p_obs),
        "ci_lower": float(ci_lower) if not np.isnan(ci_lower) else None,
        "ci_upper": float(ci_upper) if not np.isnan(ci_upper) else None,
        "n": n,
        "gate_passed": bool(gate_passed),
    }


def stratified_analysis(df: pd.DataFrame) -> dict:
    """Run correlation analysis per model type."""
    results = {}

    for model_type in ["base", "instruction-tuned"]:
        subset = df[df["model_type"] == model_type]
        results[model_type] = bootstrap_ci_group(subset)
        results[model_type]["model_type"] = model_type

    # Overall gate: both groups must pass
    base_ok = results["base"]["gate_passed"]
    inst_ok = results["instruction-tuned"]["gate_passed"]

    base_r = results["base"].get("r", 0) or 0
    inst_r = results["instruction-tuned"].get("r", 0) or 0
    same_sign = np.sign(base_r) == np.sign(inst_r) if (base_r != 0 and inst_r != 0) else False

    results["overall"] = {
        "both_pass": base_ok and inst_ok,
        "pattern_consistent": same_sign and base_r > 0 and inst_r > 0,
        "gate_passed": base_ok and inst_ok,
    }

    return results


if __name__ == "__main__":
    from data_loader import merge_all_scores
    df = merge_all_scores()
    results = stratified_analysis(df)

    for group in ["base", "instruction-tuned"]:
        r = results[group]
        print(f"\n{group.upper()}:")
        print(f"  r = {r['r']:.4f}, p = {r['p']:.4f}")
        print(f"  95% CI: [{r['ci_lower']:.4f}, {r['ci_upper']:.4f}]")
        print(f"  n = {r['n']}, gate_passed = {r['gate_passed']}")

    print(f"\nOVERALL: gate_passed = {results['overall']['gate_passed']}")
