import numpy as np
from sklearn.metrics import roc_auc_score


def bootstrap_auroc(
    scores: list,
    labels: list,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple:
    """Stratified bootstrap AUROC. Returns (auroc, ci_lower, ci_upper)."""
    rng = np.random.default_rng(seed)
    scores_arr = np.array(scores)
    labels_arr = np.array(labels)
    pos_idx = np.where(labels_arr == 1)[0]
    neg_idx = np.where(labels_arr == 0)[0]
    point_auroc = float(roc_auc_score(labels_arr, scores_arr))
    boot_aurocs = []
    for _ in range(n_boot):
        bi = np.concatenate([
            rng.choice(pos_idx, len(pos_idx), replace=True),
            rng.choice(neg_idx, len(neg_idx), replace=True),
        ])
        boot_aurocs.append(float(roc_auc_score(labels_arr[bi], scores_arr[bi])))
    ci_lower, ci_upper = np.percentile(boot_aurocs, [2.5, 97.5])
    return (point_auroc, float(ci_lower), float(ci_upper))


def compute_delta_auroc(
    se_clustered: list,
    within_fracs: list,
    em_labels: list,
    cfg,
) -> dict:
    """Returns dict: auroc_clustered, ci_clustered, auroc_ablated, ci_ablated, delta_auroc, gate_pass, gate_verdict."""
    auroc_c, ci_c_lo, ci_c_hi = bootstrap_auroc(se_clustered, em_labels, cfg.n_bootstrap, cfg.seed)
    # within_fracs: higher = more clustered = lower uncertainty; invert for uncertainty predictor
    # SE_clustered: higher = more uncertain; within_fracs: higher = more certain (inverse predictor)
    # For AUROC: we want predictor where HIGHER score = more INCORRECT (em=0)
    # SE_clustered: high SE = uncertain = likely wrong -> good predictor as-is
    # within_fracs: high frac = more clustered = more certain = likely correct -> invert
    within_fracs_inv = [1.0 - f for f in within_fracs]
    auroc_a, ci_a_lo, ci_a_hi = bootstrap_auroc(within_fracs_inv, em_labels, cfg.n_bootstrap, cfg.seed)
    delta = auroc_c - auroc_a
    gate_pass = delta >= cfg.delta_auroc_gate
    verdict = "PASS" if gate_pass else ("PARTIAL" if delta >= 0.01 else "FAIL")
    return {
        "auroc_clustered": auroc_c,
        "ci_clustered": [ci_c_lo, ci_c_hi],
        "auroc_ablated": auroc_a,
        "ci_ablated": [ci_a_lo, ci_a_hi],
        "delta_auroc": delta,
        "gate_pass": gate_pass,
        "gate_verdict": verdict,
    }


def compute_secondary_metrics(
    within_fracs: list,
    cluster_assignments: dict,
    paraphrase_subset_ids: list,
) -> dict:
    """Returns mean_within_cluster_fraction, entailment_coclustering_rate, mean_cluster_count."""
    mean_wf = float(np.mean(within_fracs))

    # co-clustering rate on subset: fraction of question pairs in same cluster
    co_rates = []
    for qid in paraphrase_subset_ids:
        if qid not in cluster_assignments:
            continue
        cids = list(cluster_assignments[qid].values())
        K = len(cids)
        if K < 2:
            continue
        # fraction of samples in the largest cluster
        from collections import Counter
        counts = Counter(cids)
        largest = max(counts.values())
        co_rates.append(largest / K)
    entailment_cocluster = float(np.mean(co_rates)) if co_rates else 0.0

    # mean cluster count across all questions
    all_counts = [len(set(ca.values())) for ca in cluster_assignments.values()]
    mean_count = float(np.mean(all_counts))

    return {
        "mean_within_cluster_fraction": mean_wf,
        "entailment_coclustering_rate": entailment_cocluster,
        "mean_cluster_count": mean_count,
    }


def verify_mechanism_activated(results: dict) -> tuple:
    """Checks 4 indicators. Returns (gate_pass, mechanism_active, indicators)."""
    indicators = {
        "clustering_reduces_n": results["mean_cluster_count"] < 10.0,
        "entropy_saving_nonzero": results["mean_within_cluster_fraction"] > 0.0,
        "auroc_delta_positive": results["delta_auroc"] > 0.0,
        "delta_meets_gate": results["gate_pass"],
    }
    mechanism_active = all(indicators.values())
    gate_pass = indicators["delta_meets_gate"]
    return (gate_pass, mechanism_active, indicators)
