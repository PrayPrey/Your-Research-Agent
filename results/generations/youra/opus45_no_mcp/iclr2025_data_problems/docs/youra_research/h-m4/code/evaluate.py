import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import pearsonr


def compute_auc(ssi: np.ndarray, labels: np.ndarray) -> float:
    if len(np.unique(labels)) < 2:
        return float('nan')
    return roc_auc_score(labels, ssi)


def compute_pearson_by_level(mean_ssi_per_level: list[float],
                              contamination_pcts: list[float]) -> tuple[float, float]:
    if len(mean_ssi_per_level) < 3:
        return float('nan'), float('nan')
    r, p = pearsonr(contamination_pcts, mean_ssi_per_level)
    return float(r), float(p)


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def verify_gate(auc: float, r: float, d: float,
                auc_threshold: float = 0.7,
                r_threshold: float = 0.6,
                d_threshold: float = 0.5) -> dict:
    primary_pass = auc > auc_threshold
    secondary_r_pass = r > r_threshold
    secondary_d_pass = abs(d) > d_threshold
    secondary_pass = secondary_r_pass and secondary_d_pass

    if primary_pass and secondary_pass:
        gate_result = "PASS"
    elif primary_pass:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"

    return {
        "gate_result": gate_result,
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
        "auc": auc,
        "auc_threshold": auc_threshold,
        "pearson_r": r,
        "r_threshold": r_threshold,
        "cohens_d": d,
        "d_threshold": d_threshold,
    }
