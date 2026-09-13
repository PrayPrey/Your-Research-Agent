"""Differential profile analysis for H-M4 benchmark comparison."""
import numpy as np
from scipy.stats import ttest_ind, pearsonr
from typing import List, Dict
from config import HM4Config


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d (pooled std) between two groups."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def analyze_differential_profiles(dpo_results: List[dict], rlhf_results: List[dict], cfg: HM4Config) -> dict:
    """Analyze differential performance profiles across benchmarks."""
    benchmarks = ["truthfulqa", "hh_helpful", "hh_harmless"]
    effects = {}

    for benchmark in benchmarks:
        dpo_scores = np.concatenate([r[benchmark]["scores"] for r in dpo_results])
        rlhf_scores = np.concatenate([r[benchmark]["scores"] for r in rlhf_results])

        d = compute_cohens_d(dpo_scores, rlhf_scores)
        t_stat, p_value = ttest_ind(dpo_scores, rlhf_scores)

        effects[benchmark] = {
            "dpo_mean": float(np.mean(dpo_scores)),
            "rlhf_mean": float(np.mean(rlhf_scores)),
            "dpo_accuracy": float(np.mean([r[benchmark]["accuracy"] for r in dpo_results])),
            "rlhf_accuracy": float(np.mean([r[benchmark]["accuracy"] for r in rlhf_results])),
            "cohens_d": float(d),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
        }

    d_values = [abs(effects[b]["cohens_d"]) for b in benchmarks]
    max_d = max(d_values)
    min_d = min(d_values)

    # Primary criterion: max(|d|) > 0.3 AND min(|d|) < 0.15
    differential_profile = max_d > cfg.d_large_threshold and min_d < cfg.d_small_threshold

    return {
        "benchmark_effects": effects,
        "max_d": float(max_d),
        "min_d": float(min_d),
        "differential_profile": differential_profile,
        "hypothesis_supported": differential_profile,
    }


def analyze_profile_shape(dpo_results: List[dict], rlhf_results: List[dict], cfg: HM4Config) -> dict:
    """Analyze profile shape using z-normalized vectors."""
    benchmarks = ["truthfulqa", "hh_helpful", "hh_harmless"]

    dpo_profile = np.array([np.mean([r[b]["accuracy"] for r in dpo_results]) for b in benchmarks])
    rlhf_profile = np.array([np.mean([r[b]["accuracy"] for r in rlhf_results]) for b in benchmarks])

    # Z-normalize
    dpo_norm = (dpo_profile - np.mean(dpo_profile)) / (np.std(dpo_profile) + 1e-8)
    rlhf_norm = (rlhf_profile - np.mean(rlhf_profile)) / (np.std(rlhf_profile) + 1e-8)

    # Pearson correlation between profiles
    profile_corr = np.corrcoef(dpo_norm, rlhf_norm)[0, 1]
    distinct_profiles = profile_corr < cfg.profile_corr_threshold

    return {
        "dpo_profile": dpo_profile.tolist(),
        "rlhf_profile": rlhf_profile.tolist(),
        "dpo_normalized": dpo_norm.tolist(),
        "rlhf_normalized": rlhf_norm.tolist(),
        "profile_correlation": float(profile_corr),
        "distinct_profiles": distinct_profiles,
    }


def analyze_cross_benchmark_correlations(dpo_results: List[dict], rlhf_results: List[dict], cfg: HM4Config) -> dict:
    """Analyze pairwise benchmark correlations per method."""
    benchmarks = ["truthfulqa", "hh_helpful", "hh_harmless"]
    pairs = [("truthfulqa", "hh_helpful"), ("truthfulqa", "hh_harmless"), ("hh_helpful", "hh_harmless")]

    dpo_corrs = {}
    rlhf_corrs = {}
    diffs = {}

    for b1, b2 in pairs:
        dpo_b1 = [r[b1]["accuracy"] for r in dpo_results]
        dpo_b2 = [r[b2]["accuracy"] for r in dpo_results]
        rlhf_b1 = [r[b1]["accuracy"] for r in rlhf_results]
        rlhf_b2 = [r[b2]["accuracy"] for r in rlhf_results]

        dpo_r, _ = pearsonr(dpo_b1, dpo_b2) if len(dpo_b1) > 2 else (0.0, 1.0)
        rlhf_r, _ = pearsonr(rlhf_b1, rlhf_b2) if len(rlhf_b1) > 2 else (0.0, 1.0)

        pair_key = f"{b1}_vs_{b2}"
        dpo_corrs[pair_key] = float(dpo_r)
        rlhf_corrs[pair_key] = float(rlhf_r)
        diffs[pair_key] = float(dpo_r - rlhf_r)

    distinct_pattern = any(abs(d) > cfg.correlation_diff_threshold for d in diffs.values())

    return {
        "dpo_correlations": dpo_corrs,
        "rlhf_correlations": rlhf_corrs,
        "correlation_differences": diffs,
        "distinct_correlation_patterns": distinct_pattern,
    }


def run_full_analysis(cfg: HM4Config, benchmark_results: dict) -> dict:
    """Run all analyses and return combined results."""
    # Separate by method
    dpo_results = [benchmark_results[k] for k in benchmark_results if "dpo" in k]
    rlhf_results = [benchmark_results[k] for k in benchmark_results if "rlhf" in k]

    differential = analyze_differential_profiles(dpo_results, rlhf_results, cfg)
    profile = analyze_profile_shape(dpo_results, rlhf_results, cfg)
    correlations = analyze_cross_benchmark_correlations(dpo_results, rlhf_results, cfg)

    return {
        "differential_analysis": differential,
        "profile_analysis": profile,
        "correlation_analysis": correlations,
        "hypothesis_supported": differential["hypothesis_supported"],
        "secondary_s1_passed": profile["distinct_profiles"],
        "secondary_s2_passed": correlations["distinct_correlation_patterns"],
    }
