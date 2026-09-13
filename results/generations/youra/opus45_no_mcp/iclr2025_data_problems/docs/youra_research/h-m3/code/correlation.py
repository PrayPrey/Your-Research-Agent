import numpy as np
from scipy.stats import pearsonr, spearmanr
from dataclasses import dataclass


@dataclass
class CorrelationResult:
    r_pearson: float
    p_pearson: float
    r_spearman: float
    p_spearman: float
    gate_passes: bool
    cohens_d: float


def compute_correlations(rep_variances: np.ndarray, conf_variances: np.ndarray) -> tuple:
    r_p, p_p = pearsonr(rep_variances, conf_variances)
    r_s, p_s = spearmanr(rep_variances, conf_variances)
    return r_p, p_p, r_s, p_s


def group_by_mps(rep_variances: np.ndarray, threshold: float = None) -> tuple:
    if threshold is None:
        threshold = np.median(rep_variances)
    high_mps_idx = np.where(rep_variances <= threshold)[0]
    low_mps_idx = np.where(rep_variances > threshold)[0]
    return high_mps_idx.tolist(), low_mps_idx.tolist()


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def group_comparison(conf_variances: np.ndarray, high_idx: list, low_idx: list) -> dict:
    high_conf_var = conf_variances[high_idx]
    low_conf_var = conf_variances[low_idx]

    d = cohens_d(low_conf_var, high_conf_var)

    return {
        "mean_conf_var_high_mps": float(np.mean(high_conf_var)),
        "mean_conf_var_low_mps": float(np.mean(low_conf_var)),
        "std_conf_var_high_mps": float(np.std(high_conf_var)),
        "std_conf_var_low_mps": float(np.std(low_conf_var)),
        "cohens_d": float(d),
        "high_has_lower_var": float(np.mean(high_conf_var)) < float(np.mean(low_conf_var)),
    }


def per_subject_correlation(rep_variances: dict, conf_variances: dict, subjects: dict) -> dict:
    subject_to_indices = {}
    for idx, subj in subjects.items():
        if subj not in subject_to_indices:
            subject_to_indices[subj] = []
        subject_to_indices[subj].append(idx)

    subject_correlations = {}
    for subj, indices in subject_to_indices.items():
        if len(indices) < 5:
            continue
        rep_vals = np.array([rep_variances[i] for i in indices])
        conf_vals = np.array([conf_variances[i] for i in indices])
        r, _ = pearsonr(rep_vals, conf_vals)
        subject_correlations[subj] = float(r)

    return subject_correlations


def verify_gate(r_pearson: float, threshold: float = -0.4) -> dict:
    return {
        "mechanism_active": r_pearson < 0,
        "gate_passes": r_pearson < threshold,
        "r_pearson": r_pearson,
        "threshold": threshold,
    }


def analyze_correlation(rep_vars: np.ndarray, conf_vars: np.ndarray) -> CorrelationResult:
    r_p, p_p, r_s, p_s = compute_correlations(rep_vars, conf_vars)
    high_idx, low_idx = group_by_mps(rep_vars)
    comparison = group_comparison(conf_vars, high_idx, low_idx)

    return CorrelationResult(
        r_pearson=r_p,
        p_pearson=p_p,
        r_spearman=r_s,
        p_spearman=p_s,
        gate_passes=r_p < -0.4,
        cohens_d=comparison["cohens_d"],
    )
