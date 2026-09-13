"""Statistical analysis for h-m2 Pareto-Optimal ECE hypothesis."""

import numpy as np
from scipy import stats

from config import SEED, P_THRESHOLD, D_THRESHOLD
from pareto import identify_pareto_optimal, label_pareto
from ece import compute_all_ece


def welch_ttest(pareto_ece: np.ndarray, non_pareto_ece: np.ndarray) -> dict:
    """Welch's t-test for unequal variances."""
    if len(pareto_ece) < 2 or len(non_pareto_ece) < 2:
        return {"t": float("nan"), "p": float("nan"),
                "mean_pareto": float("nan"), "mean_non_pareto": float("nan")}
    t, p = stats.ttest_ind(pareto_ece, non_pareto_ece, equal_var=False)
    return {
        "t": float(t),
        "p": float(p),
        "mean_pareto": float(np.mean(pareto_ece)),
        "mean_non_pareto": float(np.mean(non_pareto_ece)),
    }


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Pooled-std effect size between two 1D arrays."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled_std = np.sqrt(
        ((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1))
        / (len(a) + len(b) - 2)
    )
    if pooled_std == 0:
        return float("nan")
    return float((np.mean(a) - np.mean(b)) / pooled_std)


def random_split_baseline(df, seed: int = SEED) -> dict:
    """Randomly split df in half, run welch_ttest+cohens_d on ECE."""
    n_pareto = df["is_pareto"].sum()
    shuffled = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    group_a = shuffled.iloc[:n_pareto]
    group_b = shuffled.iloc[n_pareto:]
    ece_a = np.array([compute_all_ece(group_a["model"].tolist(), seed)[m]
                      for m in group_a["model"]])
    ece_b = np.array([compute_all_ece(group_b["model"].tolist(), seed)[m]
                      for m in group_b["model"]])
    result = welch_ttest(ece_a, ece_b)
    result["cohens_d"] = cohens_d(ece_a, ece_b)
    return result


def size_matched_baseline(df, seed: int = SEED) -> dict:
    """Split by median log_params instead of Pareto status."""
    median_lp = df["log_params"].median()
    small = df[df["log_params"] <= median_lp]
    large = df[df["log_params"] > median_lp]
    ece_s = np.array([compute_all_ece(small["model"].tolist(), seed)[m]
                      for m in small["model"]])
    ece_l = np.array([compute_all_ece(large["model"].tolist(), seed)[m]
                      for m in large["model"]])
    result = welch_ttest(ece_s, ece_l)
    result["cohens_d"] = cohens_d(ece_s, ece_l)
    return result


def run_analysis(df) -> dict:
    """Full pipeline: label pareto -> compute ECE -> stats -> gate verdict."""
    pareto_models = identify_pareto_optimal(df)
    df = label_pareto(df, pareto_models)
    ece_map = compute_all_ece(df["model"].tolist(), SEED)
    df = df.copy()
    df["ece"] = df["model"].map(ece_map)

    pareto_ece = df[df["is_pareto"]]["ece"].values
    non_pareto_ece = df[~df["is_pareto"]]["ece"].values

    ttest = welch_ttest(pareto_ece, non_pareto_ece)
    d = cohens_d(pareto_ece, non_pareto_ece)
    rand_base = random_split_baseline(df, SEED)
    size_base = size_matched_baseline(df, SEED)

    gate_passed = (
        ttest["p"] < P_THRESHOLD
        and ttest["mean_pareto"] < ttest["mean_non_pareto"]
        and len(pareto_ece) >= 3
        and len(non_pareto_ece) >= 5
        and abs(d) > D_THRESHOLD
    )

    return {
        "pareto_models": pareto_models,
        "n_pareto": len(pareto_ece),
        "n_non_pareto": len(non_pareto_ece),
        "ttest": ttest,
        "cohens_d": d,
        "random_baseline": rand_base,
        "size_matched_baseline": size_base,
        "gate_passed": gate_passed,
        "df_with_labels": df,
    }
