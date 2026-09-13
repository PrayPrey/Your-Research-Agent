import numpy as np
from scipy.stats import mannwhitneyu
from typing import List, Dict


def compute_peakedness(token_logprobs: List[float]) -> float:
    """max(|logprobs|) / mean(|logprobs|); returns 1.0 on degenerate input."""
    if not token_logprobs:
        return 1.0
    abs_lp = np.abs(token_logprobs)
    mean_val = np.mean(abs_lp)
    if mean_val == 0:
        return 1.0
    return float(np.max(abs_lp) / mean_val)


def analyze_group_peakedness(records: List[Dict]) -> Dict[str, List[float]]:
    """Split records by label (0=hallucinated, 1=correct), compute peakedness per group."""
    hallucinated = [compute_peakedness(r["logprobs"]) for r in records if r["label"] == 0]
    correct = [compute_peakedness(r["logprobs"]) for r in records if r["label"] == 1]
    return {"hallucinated": hallucinated, "correct": correct}


def test_peakedness_difference(
    hallucinated: List[float], correct: List[float]
) -> Dict:
    """Two-sided Mann-Whitney U test comparing peakedness distributions."""
    stat, p = mannwhitneyu(hallucinated, correct, alternative="two-sided")
    mean_h = float(np.mean(hallucinated))
    mean_c = float(np.mean(correct))
    direction = "hallucinated_higher" if mean_h > mean_c else "correct_higher"
    return {
        "statistic": float(stat),
        "p_value": float(p),
        "direction": direction,
        "mean_hallucinated": mean_h,
        "mean_correct": mean_c,
        "n_hallucinated": len(hallucinated),
        "n_correct": len(correct),
    }
