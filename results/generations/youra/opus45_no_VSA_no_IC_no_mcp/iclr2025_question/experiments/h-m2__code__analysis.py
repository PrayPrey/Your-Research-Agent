"""Analysis functions for H-M2: N-sample consistency mechanism."""

import numpy as np
import pandas as pd
from scipy import stats


def load_scores(csv_path: str) -> pd.DataFrame:
    """Load h-e1 scores.csv. Raises FileNotFoundError with actionable message if missing."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"h-e1 scores.csv not found at {csv_path}. Run h-e1 first.")

    required = {"question_id", "entropy", "consistency", "label"}
    if not required <= set(df.columns):
        raise ValueError(f"Missing columns. Required: {required}, got: {set(df.columns)}")
    return df


def partition_by_label(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Split 'consistency' column by 'label' (0=correct, 1=incorrect).
    Returns (consistency_correct, consistency_incorrect)."""
    correct = df.loc[df.label == 0, "consistency"].to_numpy()
    incorrect = df.loc[df.label == 1, "consistency"].to_numpy()
    return correct, incorrect


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d = (mean1 - mean2) / pooled_std."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def cohens_d_ci(group1: np.ndarray, group2: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for Cohen's d via standard error approximation. Returns (lo, hi)."""
    n1, n2 = len(group1), len(group2)
    d = cohens_d(group1, group2)
    se_d = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    z = stats.norm.ppf(1 - alpha / 2)
    return d - z * se_d, d + z * se_d


def run_ttest(group1: np.ndarray, group2: np.ndarray) -> tuple[float, float]:
    """scipy.stats.ttest_ind. Returns (t_statistic, p_value)."""
    result = stats.ttest_ind(group1, group2)
    return float(result.statistic), float(result.pvalue)


def analyze_stability_link(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Full pipeline: partition -> cohens_d -> ttest.
    Returns {mean_correct, mean_incorrect, std_correct, std_incorrect,
             cohens_d, cohens_d_ci, t_stat, p_value,
             significant, direction_correct}."""
    correct, incorrect = partition_by_label(df)

    d = cohens_d(correct, incorrect)
    d_ci = cohens_d_ci(correct, incorrect, alpha)
    t_stat, p_value = run_ttest(correct, incorrect)

    mean_correct = float(np.mean(correct))
    mean_incorrect = float(np.mean(incorrect))

    return {
        "n_correct": len(correct),
        "n_incorrect": len(incorrect),
        "mean_correct": mean_correct,
        "mean_incorrect": mean_incorrect,
        "std_correct": float(np.std(correct, ddof=1)),
        "std_incorrect": float(np.std(incorrect, ddof=1)),
        "cohens_d": d,
        "cohens_d_ci": list(d_ci),
        "t_stat": t_stat,
        "p_value": p_value,
        "significant": p_value < alpha,
        "direction_correct": mean_correct > mean_incorrect,
    }
