"""Spearman correlation analysis, Kruskal-Wallis, and ablations for h-m2."""
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kruskal, permutation_test, spearmanr


def spearman_with_permutation(
    x: List[float],
    y: List[float],
    n_resamples: int = 9999,
    seed: int = 42,
) -> dict:
    """Returns {rho, p_asymptotic, p_exact}.

    Uses spearmanr(alternative='greater') + permutation_test(permutation_type='pairings').
    """
    rho, p_asymptotic = spearmanr(x, y, alternative="greater")

    def stat_fn(xs):
        return spearmanr(xs, y).statistic

    res = permutation_test(
        (x,),
        stat_fn,
        permutation_type="pairings",
        n_resamples=n_resamples,
        alternative="greater",
        random_state=seed,
    )
    return {"rho": float(rho), "p_asymptotic": float(p_asymptotic), "p_exact": float(res.pvalue)}


def bootstrap_rho_ci(
    x: List[float],
    y: List[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Returns (ci_lower, ci_upper) — 95% bootstrap CI on Spearman rho."""
    rng = np.random.default_rng(seed)
    x_arr = np.array(x)
    y_arr = np.array(y)
    rhos = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, len(x_arr), size=len(x_arr))
        r, _ = spearmanr(x_arr[idx], y_arr[idx])
        rhos.append(r)
    rhos = np.array(rhos)
    ci_lower = float(np.percentile(rhos, 2.5))
    ci_upper = float(np.percentile(rhos, 97.5))
    return ci_lower, ci_upper


def kruskal_wallis_tiers(
    richness_df: pd.DataFrame,
    gap_dict: dict,
) -> Tuple[float, float]:
    """Returns (kw_stat, kw_p).  Groups gap values by tier 1-4."""
    groups = []
    for tier in [1, 2, 3, 4]:
        tids = richness_df[richness_df["tier"] == tier]["task_id"].tolist()
        vals = [gap_dict[t] for t in tids if t in gap_dict]
        if vals:
            groups.append(vals)
    if len(groups) < 2:
        return float("nan"), float("nan")
    stat, p = kruskal(*groups)
    return float(stat), float(p)


def tier_means(
    richness_df: pd.DataFrame,
    gap_dict: dict,
) -> Dict[int, float]:
    """Returns {1: float, 2: float, 3: float, 4: float} — mean gap per tier."""
    result = {}
    for tier in [1, 2, 3, 4]:
        tids = richness_df[richness_df["tier"] == tier]["task_id"].tolist()
        vals = [gap_dict[t] for t in tids if t in gap_dict]
        result[tier] = float(np.mean(vals)) if vals else float("nan")
    return result


def run_ablations(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    h1_results: dict,
    gap_dict_by_model: dict,
    task_type_dict: dict,
) -> dict:
    """Run all 4 ablations.  Returns dict keyed by ablation name."""
    ablations = {}

    # Align scores and gaps for full set
    merged = richness_df.copy()
    merged["gap"] = merged["task_id"].map(gap_dict)
    merged = merged.dropna(subset=["gap"])

    # Ablation 1: discrete tier as IV
    x_tier = merged["tier"].tolist()
    y_gap = merged["gap"].tolist()
    ablations["discrete_tier"] = spearman_with_permutation(x_tier, y_gap, n_resamples=9999)

    # Ablation 2: per-model Spearman
    per_model = {}
    for model, model_gaps in gap_dict_by_model.items():
        tids = [t for t in merged["task_id"] if t in model_gaps]
        if len(tids) < 10:
            continue
        x_m = merged.set_index("task_id").loc[tids, "score"].tolist()
        y_m = [model_gaps[t] for t in tids]
        r, p = spearmanr(x_m, y_m, alternative="greater")
        per_model[model] = {"rho": float(r), "p_asymptotic": float(p), "n": len(tids)}
    ablations["per_model"] = per_model

    # Ablation 3: HumanEval+ / MBPP+ subsets
    merged["task_type"] = merged["task_id"].map(task_type_dict)
    for subset_name, prefix in [("humaneval_plus", "humaneval"), ("mbpp_plus", "mbpp")]:
        subset = merged[merged["task_type"].str.lower().str.contains(prefix, na=False)]
        if len(subset) >= 10:
            x_s = subset["score"].tolist()
            y_s = subset["gap"].tolist()
            r_s = spearman_with_permutation(x_s, y_s, n_resamples=9999)
            ablations[subset_name] = {**r_s, "n": len(subset)}
        else:
            ablations[subset_name] = {"rho": float("nan"), "p_asymptotic": float("nan"), "n": len(subset)}

    # Ablation 4: node_count only as IV
    x_nc = merged["node_count"].tolist()
    ablations["node_count_only"] = spearman_with_permutation(x_nc, y_gap, n_resamples=9999)

    return ablations


def run_full_analysis(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    h1_results: dict,
    gap_dict_by_model: dict,
    task_type_dict: dict,
) -> dict:
    """Run primary test + KW + bootstrap CI + ablations.
    Returns complete results dict for h_m2_results.json.
    Sets FLAT_GRADIENT=True if rho < 0.15.
    """
    # Align x and y
    merged = richness_df.copy()
    merged["gap"] = merged["task_id"].map(gap_dict)
    merged = merged.dropna(subset=["gap"])

    x = merged["score"].tolist()
    y = merged["gap"].tolist()

    primary = spearman_with_permutation(x, y)
    rho = primary["rho"]

    if np.isnan(rho):
        raise ValueError("Spearman rho is NaN — check input alignment")

    ci_lower, ci_upper = bootstrap_rho_ci(x, y)
    kw_stat, kw_p = kruskal_wallis_tiers(richness_df, gap_dict)
    t_means = tier_means(richness_df, gap_dict)
    ablation_results = run_ablations(richness_df, gap_dict, h1_results, gap_dict_by_model, task_type_dict)

    gate_passed = rho >= 0.30 and primary["p_exact"] < 0.05

    results = {
        "rho": rho,
        "p_asymptotic": primary["p_asymptotic"],
        "p_exact": primary["p_exact"],
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "kw_stat": kw_stat,
        "kw_p": kw_p,
        "tier_means": t_means,
        "FLAT_GRADIENT": rho < 0.15,
        "gate_passed": gate_passed,
        "n_tasks": len(merged),
        "ablations": ablation_results,
    }
    return results
