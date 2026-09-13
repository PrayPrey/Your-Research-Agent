from __future__ import annotations
import numpy as np
from scipy.stats import f as f_dist
import statsmodels.api as sm
from pipeline import ols_detrend
import ruptures as rpt
from config import CFG

# ponytail: fast_jump=5 for permutation/bootstrap loops; primary detection uses jump=1.
# Speedup ~5x with negligible loss in breakpoint position accuracy for N~100.
_FAST_JUMP = 5


def _pelt_bkp_idx(paper_counts: np.ndarray, cov_values: np.ndarray,
                   jump: int = _FAST_JUMP) -> int | None:
    """Lightweight PELT call returning only breakpoint_idx. Used in loops."""
    try:
        sorted_pc, residual_cov, _ = ols_detrend(paper_counts, cov_values)
    except ValueError:
        return None
    T = len(residual_cov)
    sigma = residual_cov.std(ddof=1)
    if sigma == 0:
        return None
    bic_pen = sigma ** 2 * np.log(T)
    algo = rpt.Pelt(model=CFG.pelt_model, min_size=CFG.pelt_min_size, jump=jump)
    algo.fit(residual_cov)
    bkps = algo.predict(pen=float(bic_pen))
    n_bkps = len(bkps) - 1
    return (bkps[0] - 1) if n_bkps >= 1 else None


def _pelt_paper_count_star(paper_counts: np.ndarray, cov_values: np.ndarray,
                            jump: int = _FAST_JUMP) -> float | None:
    """Lightweight PELT returning paper_count_star. Used in bootstrap loop."""
    try:
        sorted_pc, residual_cov, _ = ols_detrend(paper_counts, cov_values)
    except ValueError:
        return None
    T = len(residual_cov)
    sigma = residual_cov.std(ddof=1)
    if sigma == 0:
        return None
    bic_pen = sigma ** 2 * np.log(T)
    algo = rpt.Pelt(model=CFG.pelt_model, min_size=CFG.pelt_min_size, jump=jump)
    algo.fit(residual_cov)
    bkps = algo.predict(pen=float(bic_pen))
    n_bkps = len(bkps) - 1
    if n_bkps >= 1:
        return float(sorted_pc[bkps[0] - 1])
    return None


def run_permutation_test(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    n_permutations: int = None,
    seed: int = None,
) -> dict:
    """Permutation test: shuffle paper_count labels, rerun PELT pipeline."""
    if n_permutations is None:
        n_permutations = CFG.n_permutations
    if seed is None:
        seed = CFG.seed

    rng = np.random.default_rng(seed)

    # Observed statistic (primary — jump=1 for accuracy)
    observed_bkp_idx = _pelt_bkp_idx(paper_counts, cov_values, jump=CFG.pelt_jump)

    if observed_bkp_idx is None:
        return {
            "permutation_p": 1.0,
            "null_distribution": np.array([]),
            "observed_bkp_idx": None,
        }

    N = len(paper_counts)
    null_bkp_positions = []
    for i in range(n_permutations):
        shuffled_pc = rng.permutation(paper_counts)
        null_bkp = _pelt_bkp_idx(shuffled_pc, cov_values, jump=_FAST_JUMP)
        null_bkp_positions.append(null_bkp if null_bkp is not None else N)
        if (i + 1) % 200 == 0:
            print(f"  Permutation {i+1}/{n_permutations}...", flush=True)

    null_dist = np.array(null_bkp_positions)
    permutation_p = float(np.sum(null_dist <= observed_bkp_idx) / n_permutations)

    print(f"Permutation test: p={permutation_p:.4f} (n={n_permutations})", flush=True)

    return {
        "permutation_p": permutation_p,
        "null_distribution": null_dist,
        "observed_bkp_idx": observed_bkp_idx,
    }


def run_bootstrap_ci(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    n_resamples: int = None,
    seed: int = None,
    confidence_level: float = 0.95,
) -> dict:
    """Bootstrap CI for paper_count* via percentile method."""
    if n_resamples is None:
        n_resamples = CFG.n_bootstrap
    if seed is None:
        seed = CFG.seed

    rng = np.random.default_rng(seed)
    N = len(paper_counts)
    estimates = []

    for i in range(n_resamples):
        idx = rng.integers(0, N, size=N)
        boot_pc = paper_counts[idx]
        boot_cov = cov_values[idx]
        pcs = _pelt_paper_count_star(boot_pc, boot_cov, jump=_FAST_JUMP)
        estimates.append(pcs if pcs is not None else np.nan)
        if (i + 1) % 200 == 0:
            print(f"  Bootstrap {i+1}/{n_resamples}...", flush=True)

    estimates = np.array(estimates)
    alpha = 1 - confidence_level
    ci_lower = float(np.nanpercentile(estimates, 100 * alpha / 2))
    ci_upper = float(np.nanpercentile(estimates, 100 * (1 - alpha / 2)))
    ci_width = ci_upper - ci_lower

    print(f"Bootstrap CI: [{ci_lower:.1f}, {ci_upper:.1f}] width={ci_width:.1f}", flush=True)

    return {
        "bootstrap_ci_lower": ci_lower,
        "bootstrap_ci_upper": ci_upper,
        "bootstrap_ci_width": float(ci_width),
        "bootstrap_estimates": estimates,
    }


def run_piecewise_ftest(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    paper_count_star: float,
) -> dict:
    """F-test: piecewise linear vs single linear model at paper_count_star."""
    sort_idx = np.argsort(paper_counts)
    pc = paper_counts[sort_idx].astype(float)
    cov = cov_values[sort_idx].astype(float)

    above = (pc >= paper_count_star).astype(float)
    pc_above = pc * above

    X_full = sm.add_constant(np.column_stack([pc, above, pc_above]))
    model_full = sm.OLS(cov, X_full).fit()

    X_restricted = sm.add_constant(pc)
    model_restricted = sm.OLS(cov, X_restricted).fit()

    f_stat = (
        (model_restricted.ssr - model_full.ssr) / 2
    ) / (model_full.ssr / model_full.df_resid)
    piecewise_f_p = float(1 - f_dist.cdf(f_stat, dfn=2, dfd=model_full.df_resid))

    print(f"Piecewise F-test: F={f_stat:.3f}, p={piecewise_f_p:.4f}", flush=True)

    return {
        "piecewise_f_p": piecewise_f_p,
        "f_statistic": float(f_stat),
    }


def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """Check all mechanism activation indicators."""
    indicators = {
        "pelt_detected_breakpoint": results.get("n_bkps_detected", 0) >= 1,
        "paper_count_star_in_range": (
            results.get("paper_count_star") is not None
            and CFG.paper_count_star_min <= results["paper_count_star"] <= CFG.paper_count_star_max
        ),
        "permutation_p_significant": results.get("permutation_p", 1.0) < CFG.p_threshold,
    }
    all_pass = all(indicators.values())
    if not all_pass:
        print(f"MECHANISM VERIFICATION FAILED: {indicators}", flush=True)
    else:
        print(
            f"MECHANISM VERIFIED: paper_count*={results['paper_count_star']}, "
            f"p={results['permutation_p']:.4f}",
            flush=True,
        )
    return all_pass, indicators
