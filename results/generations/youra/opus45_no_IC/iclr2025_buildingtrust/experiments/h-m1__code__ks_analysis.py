"""KS test analysis for pairwise cluster confidence distribution comparison."""

import numpy as np
from scipy.stats import ks_2samp
from itertools import combinations
from collections import defaultdict


def extract_cluster_confidences(records):
    """Group confidence values by cluster_id from predict() records."""
    grouped = defaultdict(list)
    for r in records:
        grouped[r["cluster_id"]].append(r["confidence"])
    return {c: np.array(v) for c, v in grouped.items()}


def pairwise_ks_tests(cluster_confidences):
    """Run KS test for all C(7,2)=21 pairs. Returns {(c1,c2): {statistic, pvalue}}."""
    cluster_ids = sorted(cluster_confidences.keys())
    results = {}
    for c1, c2 in combinations(cluster_ids, 2):
        stat, pvalue = ks_2samp(
            cluster_confidences[c1], cluster_confidences[c2], alternative="two-sided"
        )
        results[(c1, c2)] = {"statistic": float(stat), "pvalue": float(pvalue)}
    return results


def evaluate_gate_condition(ks_results, alpha=0.05, majority=11):
    """Pass if >=majority of pairs have p < alpha. Returns (gate_passed, significant_count, total_pairs)."""
    total = len(ks_results)
    significant = sum(1 for r in ks_results.values() if r["pvalue"] < alpha)
    return significant >= majority, significant, total


def cluster_mean_std(cluster_confidences):
    """Per-cluster mean/std + confidence range across clusters."""
    stats = {
        c: {"mean": float(np.mean(v)), "std": float(np.std(v)), "n": len(v)}
        for c, v in cluster_confidences.items()
    }
    means = [s["mean"] for s in stats.values()]
    stats["_range"] = max(means) - min(means)
    return stats
