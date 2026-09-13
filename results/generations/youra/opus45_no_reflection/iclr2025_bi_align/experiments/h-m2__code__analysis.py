"""Scoring and statistical analysis for H-M2."""
import numpy as np
from scipy import stats
from collab_score import compute_collab_score_v2, score_components
import config as cfg


def score_responses(responses: list) -> list:
    """Apply compute_collab_score_v2 to each response."""
    return [compute_collab_score_v2(r) for r in responses]


def compare_collab_scores(bidpo_scores: list, dpo_scores: list) -> dict:
    """Paired t-test (ttest_rel), one-sided p-value, Cohen's d, gate_passed."""
    bidpo_arr = np.array(bidpo_scores)
    dpo_arr = np.array(dpo_scores)

    t_stat, p_two = stats.ttest_rel(bidpo_arr, dpo_arr)
    p_one = p_two / 2 if t_stat > 0 else 1 - p_two / 2

    bidpo_mean = float(np.mean(bidpo_arr))
    dpo_mean = float(np.mean(dpo_arr))
    bidpo_std = float(np.std(bidpo_arr))
    dpo_std = float(np.std(dpo_arr))

    pooled_std = np.sqrt((bidpo_std**2 + dpo_std**2) / 2)
    if pooled_std > 0:
        cohens_d = (bidpo_mean - dpo_mean) / pooled_std
    else:
        cohens_d = 0.0

    gate_passed = bidpo_mean > dpo_mean and p_one < cfg.ALPHA_ONE_SIDED

    return {
        "bidpo_mean": bidpo_mean,
        "bidpo_std": bidpo_std,
        "dpo_mean": dpo_mean,
        "dpo_std": dpo_std,
        "mean_difference": bidpo_mean - dpo_mean,
        "t_statistic": float(t_stat),
        "p_value": float(p_two),
        "p_value_onesided": float(p_one),
        "effect_size_cohens_d": float(cohens_d),
        "gate_passed": bool(gate_passed),
        "n_samples": len(bidpo_scores),
    }


def get_component_means(responses: list) -> dict:
    """Get mean component scores for visualization."""
    components = [score_components(r) for r in responses]
    return {
        "reasoning": np.mean([c["reasoning"] for c in components]),
        "uncertainty": np.mean([c["uncertainty"] for c in components]),
        "engagement": np.mean([c["engagement"] for c in components]),
        "depth": np.mean([c["depth"] for c in components]),
    }
