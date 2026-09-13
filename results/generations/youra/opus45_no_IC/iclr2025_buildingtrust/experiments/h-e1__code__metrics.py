"""ECE computation and statistical testing."""

import numpy as np
import torch
from scipy import stats
from itertools import combinations
from config import N_BINS, N_BOOTSTRAP, CI, ALPHA


def compute_ece(confidences, accuracies, n_bins=N_BINS):
    """Compute Expected Calibration Error with equal-width binning."""
    if isinstance(confidences, list):
        confidences = torch.tensor(confidences)
    if isinstance(accuracies, list):
        accuracies = torch.tensor(accuracies, dtype=torch.float)

    bin_boundaries = torch.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        prop_in_bin = in_bin.float().mean()

        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].float().mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += torch.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return ece.item()


def compute_cluster_eces(results_by_cluster):
    """Compute ECE for each cluster."""
    cluster_eces = {}
    for cluster_id, records in results_by_cluster.items():
        confidences = [r["confidence"] for r in records]
        accuracies = [float(r["correct"]) for r in records]
        cluster_eces[cluster_id] = compute_ece(confidences, accuracies)
    return cluster_eces


def bootstrap_cluster_ece(confidences, accuracies, n_bootstrap=N_BOOTSTRAP, n_bins=N_BINS):
    """Resample with replacement and compute ECE for each bootstrap sample."""
    if isinstance(confidences, list):
        confidences = np.array(confidences)
    if isinstance(accuracies, list):
        accuracies = np.array(accuracies)

    n = len(confidences)
    samples = []

    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        conf_sample = torch.tensor(confidences[idx])
        acc_sample = torch.tensor(accuracies[idx], dtype=torch.float)
        samples.append(compute_ece(conf_sample, acc_sample, n_bins))

    return np.array(samples)


def run_anova(bootstrap_samples_by_cluster):
    """Run one-way ANOVA on bootstrap ECE samples across clusters."""
    samples = [bootstrap_samples_by_cluster[cid] for cid in sorted(bootstrap_samples_by_cluster.keys())]
    f_stat, p_value = stats.f_oneway(*samples)
    return float(f_stat), float(p_value)


def bonferroni_pairwise(bootstrap_samples_by_cluster):
    """Pairwise t-tests with Bonferroni correction."""
    cluster_ids = sorted(bootstrap_samples_by_cluster.keys())
    pairs = list(combinations(cluster_ids, 2))
    n_pairs = len(pairs)
    results = {}

    for a, b in pairs:
        _, p = stats.ttest_ind(bootstrap_samples_by_cluster[a], bootstrap_samples_by_cluster[b])
        results[(a, b)] = min(p * n_pairs, 1.0)

    return results


def confidence_interval(samples, ci=CI):
    """Compute confidence interval from bootstrap samples."""
    lower = (1 - ci) / 2 * 100
    upper = (1 + ci) / 2 * 100
    return float(np.percentile(samples, lower)), float(np.percentile(samples, upper))
