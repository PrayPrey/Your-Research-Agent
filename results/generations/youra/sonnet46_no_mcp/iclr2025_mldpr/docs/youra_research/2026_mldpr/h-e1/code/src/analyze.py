"""
A-4 Statistical Analyzer
Computes existence metrics: CV, group sizes, Spearman correlations, bimodality, gate.
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional

try:
    import diptest as _diptest
    _HAS_DIPTEST = True
except ImportError:
    _HAS_DIPTEST = False


def compute_cv(scores: pd.Series) -> float:
    """Coefficient of Variation = std(ddof=1) / mean. NaN-safe."""
    clean = scores.dropna()
    if len(clean) < 2:
        return float("nan")
    mean_val = clean.mean()
    if mean_val == 0:
        return float("nan")
    return float(clean.std(ddof=1) / mean_val)


def compute_group_sizes(
    scores: pd.Series,
    threshold: float = 0.5,
) -> tuple:
    """Return (n_high, n_low) where n_high = count(scores >= threshold)."""
    clean = scores.dropna()
    n_high = int((clean >= threshold).sum())
    n_low = int((clean < threshold).sum())
    return n_high, n_low


def compute_spearman_correlations(
    df: pd.DataFrame,
    score_col: str,
    covariate_cols: list,
) -> dict:
    """Compute Spearman r between score_col and each covariate column.

    Skips columns with fewer than 10 non-null paired values (returns nan).
    Returns dict: {col_name: r_value}
    """
    result = {}
    for col in covariate_cols:
        if col not in df.columns:
            result[col] = float("nan")
            continue
        paired = df[[score_col, col]].dropna()
        if len(paired) < 10:
            result[col] = float("nan")
            continue
        r, _ = stats.spearmanr(paired[score_col], paired[col])
        result[col] = float(r)
    return result


def detect_bimodality(scores: pd.Series) -> dict:
    """Hartigan dip test + bimodality coefficient (BC).

    Returns dict: {bimodal: bool, dip_stat: float, dip_p: float, bc: float}
    bimodal = True if dip_p < 0.05 OR bc > 5/9
    """
    clean = scores.dropna().values
    n = len(clean)

    dip_stat = float("nan")
    dip_p = float("nan")

    if _HAS_DIPTEST and n >= 10:
        try:
            dip_stat, dip_p = _diptest.diptest(clean)
            dip_stat = float(dip_stat)
            dip_p = float(dip_p)
        except Exception:
            pass

    # Bimodality Coefficient
    bc = float("nan")
    if n >= 4:
        try:
            skew = float(stats.skew(clean))
            kurt = float(stats.kurtosis(clean))  # excess kurtosis
            # Adjusted formula: BC = (skew^2 + 1) / (kurtosis + 3*(n-1)^2/((n-2)*(n-3)))
            if n > 3:
                correction = 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
            else:
                correction = 3.0
            bc = (skew ** 2 + 1) / (kurt + correction) if (kurt + correction) != 0 else float("nan")
        except Exception:
            pass

    bimodal_dip = (not np.isnan(dip_p)) and (dip_p < 0.05)
    bimodal_bc = (not np.isnan(bc)) and (bc > 5.0 / 9.0)
    bimodal = bimodal_dip or bimodal_bc

    return {
        "bimodal": bimodal,
        "dip_stat": dip_stat,
        "dip_p": dip_p,
        "bc": float(bc) if not np.isnan(bc) else None,
    }


def run_analysis(scored: pd.DataFrame, cfg) -> dict:
    """Compute all existence metrics from scored DataFrame.

    Returns dict with keys: cv, n_high, n_low, r_quality, r_date,
    bimodality, mean_fair, std_fair, n_total, n_failed
    """
    valid = scored[scored["status"].isin(["ok", "fallback"])].copy()
    scores = valid["fair_aggregate"].dropna()

    cv = compute_cv(scores)
    n_high, n_low = compute_group_sizes(scores, threshold=cfg.FAIR_THRESHOLD)

    # Compute metadata_richness: count of non-null OpenML quality columns per row
    quality_cols = ["NumberOfInstances", "NumberOfFeatures", "MajorityClassPercentage"]
    present_quality_cols = [c for c in quality_cols if c in valid.columns]
    if present_quality_cols:
        valid = valid.copy()
        valid["metadata_richness"] = valid[present_quality_cols].notna().sum(axis=1)
    else:
        valid["metadata_richness"] = float("nan")

    covariate_cols = []
    if "upload_date_ordinal" in valid.columns:
        covariate_cols.append("upload_date_ordinal")
    if "metadata_richness" in valid.columns:
        covariate_cols.append("metadata_richness")

    spearman = compute_spearman_correlations(valid, "fair_aggregate", covariate_cols)

    bimodality = detect_bimodality(scores)

    n_failed = int((scored["status"].isin(["failed", "retry_exhausted", "parse_error"])).sum())

    return {
        "cv": float(cv) if not np.isnan(cv) else None,
        "n_high": n_high,
        "n_low": n_low,
        "r_quality": spearman.get("metadata_richness", float("nan")),
        "r_date": spearman.get("upload_date_ordinal", float("nan")),
        "bimodality": bimodality,
        "mean_fair": float(scores.mean()) if len(scores) > 0 else None,
        "std_fair": float(scores.std(ddof=1)) if len(scores) > 1 else None,
        "n_total": len(valid),
        "n_failed": n_failed,
    }


def evaluate_gate(metrics: dict, cfg) -> dict:
    """Evaluate primary MUST_WORK gate conditions.

    Gate passes if: CV > CV_GATE AND n_high >= GROUP_SIZE_GATE AND n_low >= GROUP_SIZE_GATE
    Returns: {passed: bool, cv: float, n_high: int, n_low: int, reason: str}
    """
    cv = metrics.get("cv")
    n_high = metrics.get("n_high", 0)
    n_low = metrics.get("n_low", 0)

    failures = []

    if cv is None or np.isnan(cv):
        failures.append("CV=None (computation failed)")
    elif cv <= cfg.CV_GATE:
        failures.append(f"CV={cv:.3f} below threshold {cfg.CV_GATE}")

    if n_high < cfg.GROUP_SIZE_GATE:
        failures.append(f"n_high={n_high} below {cfg.GROUP_SIZE_GATE}")

    if n_low < cfg.GROUP_SIZE_GATE:
        failures.append(f"n_low={n_low} below {cfg.GROUP_SIZE_GATE}")

    passed = len(failures) == 0

    return {
        "passed": passed,
        "cv": cv,
        "n_high": n_high,
        "n_low": n_low,
        "reason": "PASS" if passed else "; ".join(failures),
    }
