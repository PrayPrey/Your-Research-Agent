"""OLS regression + bootstrap CI for H-M3."""
import numpy as np
import statsmodels.api as sm
from scipy import stats


def _run_scipy_ols(kl: np.ndarray, gap: np.ndarray) -> dict:
    slope, intercept, r_value, p_value, std_err = stats.linregress(kl, gap)
    r_squared = float(r_value ** 2)
    t_stat = float(slope / std_err) if std_err != 0 else float("nan")
    fitted = slope * kl + intercept
    residuals = gap - fitted
    return {
        "slope":     float(slope),
        "intercept": float(intercept),
        "r_value":   float(r_value),
        "r_squared": r_squared,
        "p_value":   float(p_value),
        "std_err":   float(std_err),
        "t_stat":    t_stat,
        "fitted":    fitted,
        "residuals": residuals,
        "n":         int(len(kl)),
    }


def _run_statsmodels_ols(kl: np.ndarray, gap: np.ndarray) -> dict:
    X = sm.add_constant(kl)
    model = sm.OLS(gap, X).fit()
    ci = model.conf_int(alpha=0.05)
    ci_low, ci_high = float(ci[1, 0]), float(ci[1, 1])
    return {
        "ci_parametric":      (ci_low, ci_high),
        "statsmodels_summary": str(model.summary()),
    }


def _run_bootstrap(kl: np.ndarray, gap: np.ndarray, n_boot: int = 10_000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(kl))
    boot_slopes = np.empty(n_boot, dtype=np.float64)

    for i in range(n_boot):
        s = rng.choice(idx, size=len(idx), replace=True)
        b_slope, *_ = stats.linregress(kl[s], gap[s])
        boot_slopes[i] = b_slope

    # Handle degenerate bootstrap samples (zero variance → nan slope)
    nan_count = int(np.isnan(boot_slopes).sum())
    if nan_count > 0:
        print(f"⚠ {nan_count} NaN bootstrap slopes removed (degenerate samples)")
        boot_slopes = boot_slopes[~np.isnan(boot_slopes)]

    assert len(boot_slopes) >= n_boot * 0.99, (
        f"Bootstrap convergence failure: {len(boot_slopes)}/{n_boot} valid slopes"
    )

    ci_bootstrap = np.percentile(boot_slopes, [2.5, 97.5])
    return {
        "boot_slopes":  boot_slopes,
        "ci_bootstrap": ci_bootstrap,
    }


def fit_ols_regression(
    kl_values: np.ndarray,
    gap_values: np.ndarray,
    n_boot: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Full H-M3 regression analysis: OLS slope test + bootstrap CI.

    Returns dict with slope, intercept, r_squared, p_value, std_err, t_stat,
    r_value, ci_parametric, ci_bootstrap, boot_slopes, fitted, residuals, n,
    statsmodels_summary.
    """
    if np.std(gap_values) == 0:
        raise ValueError("Degenerate gap array: all values equal — regression undefined")
    if len(kl_values) < 5:
        raise ValueError(f"Insufficient data: N={len(kl_values)}, minimum 5 required")

    scipy_res = _run_scipy_ols(kl_values, gap_values)
    sm_res    = _run_statsmodels_ols(kl_values, gap_values)
    boot_res  = _run_bootstrap(kl_values, gap_values, n_boot=n_boot, seed=seed)

    return {**scipy_res, **sm_res, **boot_res}


def verify_mechanism_activated(results: dict):
    """Verify OLS produced valid output. Raises RuntimeError on failure."""
    indicators = {
        "data_loaded":     results.get("n") == 10,
        "slope_computed":  results.get("slope") is not None and not np.isnan(results["slope"]),
        "p_value_valid":   0.0 <= results.get("p_value", 1.1) <= 1.0,
        "r_squared_valid": 0.0 <= results.get("r_squared", -1.0) <= 1.0,
        "ci_computed":     results.get("ci_bootstrap") is not None,
    }
    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(f"Mechanism verification FAILED: {failed}")
    print("✓ Mechanism activation verified")
    return True, indicators


def check_gate(results: dict):
    """
    Gate: slope > 0 AND p < 0.05 AND R² > 0.5

    Returns:
        (gate_pass: bool, gate_reason: str)
    """
    slope     = results["slope"]
    p_value   = results["p_value"]
    r_squared = results["r_squared"]

    conditions = {
        "slope > 0": slope > 0,
        "p < 0.05":  p_value < 0.05,
        "R² > 0.5":  r_squared > 0.5,
    }
    gate_pass = all(conditions.values())

    if gate_pass:
        gate_reason = (
            f"PASS: slope={slope:.4f}>0, p={p_value:.2e}<0.05, R²={r_squared:.4f}>0.5"
        )
    else:
        failed = [name for name, ok in conditions.items() if not ok]
        gate_reason = (
            f"FAIL: conditions not met: {failed}. "
            f"slope={slope:.4f}, p={p_value:.2e}, R²={r_squared:.4f}. "
            "Action: ABANDON H-BiAlign-v1; route to Phase 0."
        )
    return gate_pass, gate_reason
