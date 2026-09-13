"""ANOVA F-ratio and Cohen's d computation for h-m2 dissociation test."""
import numpy as np
from scipy import stats


def compute_dissociation_metrics(all_profiles: dict) -> dict:
    """Compute ANOVA F-ratio and Cohen's d for method dissociation.

    Runs per-dimension ANOVA and takes max F-ratio across dimensions.
    This tests whether methods differ in their mode sensitivity patterns.

    Args:
        all_profiles: {method: [profile_seed0, ..., profile_seedN]} where each profile is [3]

    Returns:
        dict with F_ratio, p_value, cohens_d, ss_between, ss_within
    """
    methods = list(all_profiles.keys())
    n_dims = 3

    # Stack: {method: [n_seeds, 3]}
    stacked = {m: np.stack(all_profiles[m]) for m in methods}

    # Per-dimension ANOVA, take max F-ratio
    f_ratios = []
    p_values = []
    for d in range(n_dims):
        groups = [stacked[m][:, d] for m in methods]
        F, p = stats.f_oneway(*groups)
        f_ratios.append(F)
        p_values.append(p)

    # Use max F-ratio (most discriminative dimension)
    max_idx = np.argmax(f_ratios)
    F_ratio = f_ratios[max_idx]
    p_value = p_values[max_idx]

    # Compute SS for the max dimension
    d = max_idx
    groups = [stacked[m][:, d] for m in methods]
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    group_means = [g.mean() for g in groups]
    n_per_group = len(groups[0])

    ss_between = sum(n_per_group * (gm - grand_mean) ** 2 for gm in group_means)
    ss_within = sum(np.sum((g - gm) ** 2) for g, gm in zip(groups, group_means))

    # Cohen's d: max over all method pairs and dims
    cohens_d = _compute_max_cohens_d(all_profiles, methods)

    return {
        "F_ratio": float(F_ratio),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "ss_between": float(ss_between),
        "ss_within": float(ss_within),
        "df_between": len(methods) - 1,
        "df_within": len(all_vals) - len(methods),
        "max_f_dimension": int(max_idx),
    }


def _compute_max_cohens_d(all_profiles: dict, methods: list) -> float:
    """Compute max Cohen's d across all method pairs and dimensions."""
    max_d = 0.0
    n = len(all_profiles[methods[0]])

    for i, m1 in enumerate(methods):
        for m2 in methods[i + 1:]:
            arr1 = np.stack(all_profiles[m1])  # [n_seeds, 3]
            arr2 = np.stack(all_profiles[m2])

            for dim in range(3):
                v1 = arr1[:, dim]
                v2 = arr2[:, dim]

                mean_diff = abs(v1.mean() - v2.mean())
                pooled_std = np.sqrt(((n - 1) * v1.std() ** 2 + (n - 1) * v2.std() ** 2) / (2 * n - 2))

                if pooled_std > 1e-8:
                    d = mean_diff / pooled_std
                    max_d = max(max_d, d)

    return max_d


def verify_dissociation(results: dict, cfg=None) -> bool:
    """Verify dissociation gate: F_ratio > 4.0 AND cohens_d > 0.5.

    Args:
        results: output from compute_dissociation_metrics
        cfg: optional config with threshold overrides

    Returns:
        bool: gate pass status
    """
    f_thresh = cfg.f_ratio_threshold if cfg else 4.0
    d_thresh = cfg.cohens_d_threshold if cfg else 0.5
    p_thresh = cfg.p_value_threshold if cfg else 0.05

    f_pass = results["F_ratio"] > f_thresh
    d_pass = results["cohens_d"] > d_thresh
    p_pass = results["p_value"] < p_thresh

    print(f"F-ratio: {results['F_ratio']:.3f} > {f_thresh}: {'PASS' if f_pass else 'FAIL'}")
    print(f"Cohen's d: {results['cohens_d']:.3f} > {d_thresh}: {'PASS' if d_pass else 'FAIL'}")
    print(f"p-value: {results['p_value']:.4f} < {p_thresh}: {'PASS' if p_pass else 'FAIL'}")

    gate_pass = f_pass and d_pass
    print(f"\nGATE (F>4 AND d>0.5): {'PASS' if gate_pass else 'FAIL'}")

    return gate_pass
