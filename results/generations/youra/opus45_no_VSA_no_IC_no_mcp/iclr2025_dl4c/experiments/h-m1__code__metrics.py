"""Metrics calculation for H-M1 experiment."""
import pandas as pd
import numpy as np
from scipy import stats
from config import CFG

def cf_score_distribution(df: pd.DataFrame) -> dict:
    """Calculate CF score distribution statistics."""
    scores = df["cf_score"]
    return {
        "mean": float(scores.mean()),
        "median": float(scores.median()),
        "std": float(scores.std()),
        "p70": float(np.percentile(scores, 70)),
        "min": float(scores.min()),
        "max": float(scores.max()),
        "count": len(scores),
    }

def hypothesis_test(df: pd.DataFrame, threshold: float = None) -> dict:
    """One-sample t-test: H0: mean CF_score <= threshold."""
    threshold = threshold or CFG.hypothesis_test_threshold
    scores = df["cf_score"]
    t_stat, p_value = stats.ttest_1samp(scores, threshold)
    p_one_sided = p_value / 2 if t_stat > 0 else 1 - p_value / 2
    return {
        "t_statistic": float(t_stat),
        "p_value_two_sided": float(p_value),
        "p_value_one_sided": float(p_one_sided),
        "reject_null": p_one_sided < 0.05 and scores.mean() > threshold,
        "mean": float(scores.mean()),
        "threshold": threshold,
    }

def cf_by_bug_type_anova(df: pd.DataFrame) -> dict:
    """ANOVA test for CF score by bug type."""
    groups = [group["cf_score"].values for _, group in df.groupby("bug_type")]
    if len(groups) < 2:
        return {"f_statistic": None, "p_value": None, "significant": False}
    f_stat, p_value = stats.f_oneway(*groups)
    return {
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "group_means": {bt: float(g["cf_score"].mean()) for bt, g in df.groupby("bug_type")},
    }

def root_cause_accuracy(df: pd.DataFrame) -> dict:
    """Calculate root cause identification accuracy."""
    if "identifies_root_cause" not in df.columns:
        return {"overall": None, "by_bug_type": {}}
    overall = float(df["identifies_root_cause"].mean())
    by_type = {bt: float(g["identifies_root_cause"].mean()) for bt, g in df.groupby("bug_type")}
    return {"overall": overall, "by_bug_type": by_type}

def cohens_kappa(human_labels: list, auto_labels: list) -> float:
    """Calculate Cohen's kappa for inter-rater reliability."""
    if len(human_labels) != len(auto_labels):
        raise ValueError("Label lists must have same length")
    n = len(human_labels)
    if n == 0:
        return 0.0
    observed_agreement = sum(h == a for h, a in zip(human_labels, auto_labels)) / n
    unique_labels = set(human_labels) | set(auto_labels)
    expected_agreement = 0.0
    for label in unique_labels:
        p_human = sum(h == label for h in human_labels) / n
        p_auto = sum(a == label for a in auto_labels) / n
        expected_agreement += p_human * p_auto
    if expected_agreement == 1.0:
        return 1.0
    kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
    return float(kappa)

def above_threshold_rate(df: pd.DataFrame, threshold: float = None) -> dict:
    """Calculate rate of samples with CF_score >= threshold."""
    threshold = threshold or CFG.cf_threshold
    above = (df["cf_score"] >= threshold).sum()
    total = len(df)
    return {
        "count_above": int(above),
        "total": total,
        "rate": float(above / total) if total > 0 else 0.0,
        "threshold": threshold,
    }

if __name__ == "__main__":
    df = pd.DataFrame({
        "cf_score": [0.2, 0.4, 0.6, 0.8, 0.4, 0.6],
        "bug_type": ["syntax", "syntax", "logic", "logic", "type", "type"],
        "identifies_root_cause": [True, False, True, True, False, True],
    })
    print("Distribution:", cf_score_distribution(df))
    print("Hypothesis test:", hypothesis_test(df))
    print("ANOVA:", cf_by_bug_type_anova(df))
    print("Root cause:", root_cause_accuracy(df))
    print("Above threshold:", above_threshold_rate(df))
