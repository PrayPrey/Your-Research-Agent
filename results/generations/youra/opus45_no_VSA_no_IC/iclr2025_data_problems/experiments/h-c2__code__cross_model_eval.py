"""Cross-model correlation analysis for h-c2."""
from itertools import combinations
from typing import Dict, Tuple

import numpy as np
from scipy.stats import pearsonr


def compute_mode_profile(scores: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Mean score per mode -> profile vector."""
    return {mode: float(np.mean(s)) for mode, s in scores.items()}


def pairwise_correlations(
    profiles: Dict[str, Dict[str, float]],
    modes: tuple = ("mem", "transfer", "spurious"),
    bonferroni_n: int = 3
) -> Dict[Tuple[str, str], dict]:
    """Pearson r + Bonferroni-corrected p-value for each model pair."""
    results = {}
    for m1, m2 in combinations(profiles.keys(), 2):
        v1 = np.array([profiles[m1][m] for m in modes])
        v2 = np.array([profiles[m2][m] for m in modes])
        r, p = pearsonr(v1, v2)
        p_corrected = min(p * bonferroni_n, 1.0)
        results[(m1, m2)] = {
            "r": r, "p": p, "p_corrected": p_corrected,
            "significant": p_corrected < 0.05 / bonferroni_n
        }
    return results


def bootstrap_ci(v1: np.ndarray, v2: np.ndarray, n_boot: int = 1000, seed: int = 42) -> Tuple[float, float]:
    """95% CI for Pearson r via bootstrap."""
    rng = np.random.default_rng(seed)
    n = len(v1)
    rs = []
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        r, _ = pearsonr(v1[idx], v2[idx])
        rs.append(r)
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def check_transfer_success(correlations: dict, threshold: float = 0.7) -> str:
    """PASS if all r > threshold, PARTIAL if mean > threshold, FAIL otherwise."""
    rs = [c["r"] for c in correlations.values()]
    if all(r > threshold for r in rs):
        return "PASS"
    if np.mean(rs) > threshold:
        return "PARTIAL"
    return "FAIL"


def ablation_method_comparison(trak_correlations: dict, kronfluence_correlations: dict) -> dict:
    """ABL-1: Compare TRAK vs Kronfluence correlation patterns."""
    agreement = True
    for pair in trak_correlations:
        if pair in kronfluence_correlations:
            diff = abs(trak_correlations[pair]["r"] - kronfluence_correlations[pair]["r"])
            if diff > 0.2:
                agreement = False
    return {"trak": trak_correlations, "kronfluence": kronfluence_correlations, "agreement": agreement}


def ablation_probe_stability(full_correlations: dict, subset_correlations: dict) -> dict:
    """ABL-2: Check stability of correlations with 50% probe subset."""
    stable = True
    max_diff = 0.0
    for pair in full_correlations:
        if pair in subset_correlations:
            diff = abs(full_correlations[pair]["r"] - subset_correlations[pair]["r"])
            max_diff = max(max_diff, diff)
            if diff > 0.1:
                stable = False
    return {"full": full_correlations, "subset": subset_correlations, "stable": stable, "max_diff": max_diff}
