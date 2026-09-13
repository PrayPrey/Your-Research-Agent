import math
from scipy.stats import ttest_ind


def cohens_d(a: list, b: list) -> float:
    if len(a) < 2 or len(b) < 2:
        return float('nan')
    mean_a, mean_b = sum(a) / len(a), sum(b) / len(b)
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    pooled_std = math.sqrt(((len(a) - 1) * var_a + (len(b) - 1) * var_b) / (len(a) + len(b) - 2))
    if pooled_std == 0:
        return float('nan')
    return (mean_a - mean_b) / pooled_std


def compare_gaps(gaps_high: list, gaps_low: list) -> dict:
    d = cohens_d(gaps_high, gaps_low)
    if len(gaps_high) < 2 or len(gaps_low) < 2:
        return {"d": d, "t": float('nan'), "p": float('nan')}
    t, p = ttest_ind(gaps_high, gaps_low)
    return {"d": d, "t": float(t), "p": float(p)}
