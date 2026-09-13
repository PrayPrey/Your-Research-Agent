"""Statistical tests for H-M2."""
from typing import List, Dict
from scipy.stats import chi2_contingency, mannwhitneyu


def chi_square_test(
    u_line_correct: int, u_line_total: int,
    u_ignore_correct: int, u_ignore_total: int
) -> Dict:
    """Chi-square test for accuracy difference."""
    table = [
        [u_line_correct, u_line_total - u_line_correct],
        [u_ignore_correct, u_ignore_total - u_ignore_correct]
    ]

    min_expected = min(u_line_total, u_ignore_total) * 0.1
    if min_expected < 5:
        return {"chi2": 0.0, "p_value": 1.0, "significant": False, "note": "low cell counts"}

    chi2, p_value, dof, expected = chi2_contingency(table)
    return {
        "chi2": float(chi2),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05)
    }


def mann_whitney_test(u_line_distances: List[int], u_ignore_distances: List[int]) -> Dict:
    """Mann-Whitney U test for distance distributions."""
    if len(u_line_distances) < 5 or len(u_ignore_distances) < 5:
        return {"u_statistic": 0.0, "p_value": 1.0, "significant": False, "note": "insufficient samples"}

    stat, p_value = mannwhitneyu(u_line_distances, u_ignore_distances, alternative='less')
    return {
        "u_statistic": float(stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05)
    }
