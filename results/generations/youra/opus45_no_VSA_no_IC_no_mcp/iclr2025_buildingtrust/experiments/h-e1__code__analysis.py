"""Partial correlation analysis with bootstrap CI."""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from config import N_BOOTSTRAP, SEED, R_THRESHOLD, P_THRESHOLD, CI_LOWER_THRESHOLD


def residualize(v: np.ndarray, z: np.ndarray) -> np.ndarray:
    coef = np.polyfit(z, v, deg=1)
    fitted = np.polyval(coef, z)
    return v - fitted


def partial_corr(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple:
    rx = residualize(x, z)
    ry = residualize(y, z)
    r, p = pearsonr(rx, ry)
    return r, p


def bootstrap_ci(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    rng = np.random.default_rng(seed)
    r_obs, p_obs = partial_corr(x, y, z)

    bootstrap_rs = []
    for _ in range(n_bootstrap):
        idx = rng.choice(len(x), size=len(x), replace=True)
        xb, yb, zb = x[idx], y[idx], z[idx]
        if len(np.unique(zb)) < 2:
            continue
        rb, _ = partial_corr(xb, yb, zb)
        bootstrap_rs.append(rb)

    bootstrap_rs = np.array(bootstrap_rs)
    ci_lower, ci_upper = np.percentile(bootstrap_rs, [2.5, 97.5])

    gate_passed = (
        r_obs > R_THRESHOLD
        and p_obs < P_THRESHOLD
        and ci_lower > CI_LOWER_THRESHOLD
    )

    return {
        "r": float(r_obs),
        "p": float(p_obs),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "bootstrap_rs": bootstrap_rs.tolist(),
        "n_models": len(x),
        "gate_passed": bool(gate_passed),
    }


def run_analysis(
    df: pd.DataFrame,
    x_col: str = "truthfulqa_mc1",
    y_col: str = "advglue_avg",
    z_col: str = "log_params",
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    x = df[x_col].values
    y = df[y_col].values
    z = df[z_col].values
    return bootstrap_ci(x, y, z, n_bootstrap, seed)


if __name__ == "__main__":
    from aggregate import collect_scores
    df = collect_scores()
    result = run_analysis(df)
    print(f"r = {result['r']:.4f}, p = {result['p']:.4f}")
    print(f"95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
    print(f"Gate passed: {result['gate_passed']}")
