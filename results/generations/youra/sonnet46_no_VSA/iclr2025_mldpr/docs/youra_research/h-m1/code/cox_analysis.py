import warnings
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from scipy import stats

from config import CoxConfig


@dataclass
class LRTResult:
    lrt_stat: float
    p_value: float
    HR: float
    CI_lower: float
    CI_upper: float
    abs_effect: float
    concordance: float
    M0_log_likelihood: float
    M1_log_likelihood: float
    direction: str   # "H1" | "H2" | "H0"
    gate_passed: bool


def load_panel(cfg: CoxConfig) -> pd.DataFrame:
    """Load and validate H-E1 output panel."""
    panel_df = pd.read_csv(cfg.panel_path)
    required_cols = [
        cfg.duration_col, cfg.event_col,
        *cfg.base_covariates,
        cfg.diversity_col,
    ]
    missing = [c for c in required_cols if c not in panel_df.columns]
    assert not missing, f"Missing columns: {missing}"
    assert len(panel_df) >= 300, f"Unexpected row count: {len(panel_df)}"
    # Drop NaN in analysis columns
    n_before = len(panel_df)
    panel_df = panel_df.dropna(subset=required_cols)
    if len(panel_df) < n_before:
        print(f"Dropped {n_before - len(panel_df)} rows with NaN")
    print(f"Panel loaded: {len(panel_df)} rows, {len(panel_df.columns)} columns")
    return panel_df


def fit_models(
    panel_df: pd.DataFrame,
    cfg: CoxConfig,
) -> Tuple[CoxPHFitter, CoxPHFitter]:
    """Fit M0 (controls) and M1 (controls + diversity). Returns (M0, M1)."""
    base_cols = list(cfg.base_covariates) + [cfg.duration_col, cfg.event_col]
    full_cols = base_cols + [cfg.diversity_col]

    def _fit(fitter: CoxPHFitter, cols: list, label: str) -> CoxPHFitter:
        df_sub = panel_df[cols].dropna()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fitter.fit(df_sub, duration_col=cfg.duration_col, event_col=cfg.event_col)
            converged = not any("ConvergenceWarning" in str(x.category) for x in w)
        if not converged:
            print(f"WARNING: {label} convergence issue — refitting penalizer={cfg.penalizer_fallback}")
            fitter2 = CoxPHFitter(penalizer=cfg.penalizer_fallback)
            fitter2.fit(df_sub, duration_col=cfg.duration_col, event_col=cfg.event_col)
            return fitter2
        return fitter

    M0 = _fit(CoxPHFitter(penalizer=cfg.penalizer), base_cols, "M0")
    print(f"M0 fitted: log_likelihood={M0.log_likelihood_:.4f}")

    M1 = _fit(CoxPHFitter(penalizer=cfg.penalizer), full_cols, "M1")
    print(f"M1 fitted: log_likelihood={M1.log_likelihood_:.4f}, concordance={M1.concordance_index_:.4f}")

    return M0, M1


def run_lrt(
    M0: CoxPHFitter,
    M1: CoxPHFitter,
    cfg: CoxConfig,
) -> LRTResult:
    """LRT chi2(df=1), HR/CI extraction, gate eval, direction routing."""
    ll0 = M0.log_likelihood_
    ll1 = M1.log_likelihood_

    if not (np.isfinite(ll0) and np.isfinite(ll1)):
        raise ValueError(f"Non-finite log-likelihoods: M0={ll0}, M1={ll1}")

    lrt_stat = -2.0 * (ll0 - ll1)

    # L2 penalty can make M1 slightly worse than M0 in log-likelihood
    if lrt_stat < 0:
        print(f"WARNING: lrt_stat={lrt_stat:.6f} < 0; M1 not better than M0 under L2 penalty")
        lrt_stat = max(lrt_stat, 0.0)

    p_value = stats.chi2.sf(lrt_stat, df=cfg.lrt_df)
    print(f"LRT stat={lrt_stat:.4f}, p={p_value:.4f}")

    HR = float(M1.hazard_ratios_[cfg.diversity_col])
    ci_cols = list(M1.confidence_intervals_.columns)
    lower_col = next((c for c in ci_cols if "lower" in c.lower()), ci_cols[0])
    upper_col = next((c for c in ci_cols if "upper" in c.lower()), ci_cols[1])
    CI_lower = float(np.exp(M1.confidence_intervals_.loc[cfg.diversity_col, lower_col]))
    CI_upper = float(np.exp(M1.confidence_intervals_.loc[cfg.diversity_col, upper_col]))
    abs_effect = abs(HR - 1.0)
    print(f"HR={HR:.4f}, CI=[{CI_lower:.4f}, {CI_upper:.4f}], |HR-1|={abs_effect:.4f}")

    gate_passed = (p_value < cfg.p_threshold) and (abs_effect >= cfg.hr_effect_threshold)

    if p_value < cfg.p_threshold and HR < 1.0:
        direction = "H1"
    elif p_value < cfg.p_threshold and HR > 1.0:
        direction = "H2"
    else:
        direction = "H0"

    return LRTResult(
        lrt_stat=lrt_stat, p_value=p_value,
        HR=HR, CI_lower=CI_lower, CI_upper=CI_upper,
        abs_effect=abs_effect,
        concordance=M1.concordance_index_,
        M0_log_likelihood=ll0, M1_log_likelihood=ll1,
        direction=direction, gate_passed=gate_passed,
    )


def run_diagnostics(M1: CoxPHFitter, panel_df: pd.DataFrame) -> dict:
    """Return concordance and PH assumption check results."""
    concordance = float(M1.concordance_index_)
    ph_violations = []
    try:
        # check_assumptions prints internally; capture violations
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            assumption_result = M1.check_assumptions(panel_df, p_value_threshold=0.05, show_plots=False)
        # lifelines returns None if no violations
        if assumption_result is not None:
            ph_violations = list(assumption_result)
    except Exception as e:
        print(f"PH assumption check warning: {e}")
    return {"concordance": concordance, "ph_violations": ph_violations}
