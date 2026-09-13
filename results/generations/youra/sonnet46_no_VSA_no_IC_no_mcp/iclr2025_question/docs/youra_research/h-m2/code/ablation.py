import math
from collections import Counter


def compute_se_from_ids(cluster_ids: list, K: int) -> float:
    """Entropy over cluster distribution. Returns float in [0, log(K)]."""
    counts = Counter(cluster_ids)
    probs = [c / K for c in counts.values()]
    se = -sum(p * math.log(p + 1e-10) for p in probs)
    return se


def within_cluster_fraction(cluster_ids: list, K: int) -> float:
    """(log(K) - SE_clustered) / log(K). Returns float in [0, 1]."""
    log_K = math.log(K)
    se = compute_se_from_ids(cluster_ids, K)
    return max(0.0, min(1.0, (log_K - se) / log_K))


def compute_ablation_scores(
    cluster_assignments: dict,
    question_ids: list,
    K: int = 10,
) -> tuple:
    """Returns (se_clustered, within_fracs, cluster_counts) for all questions."""
    se_clustered, within_fracs, cluster_counts = [], [], []
    for qid in question_ids:
        assignment = cluster_assignments[qid]
        cids = list(assignment.values())
        se = compute_se_from_ids(cids, K)
        frac = within_cluster_fraction(cids, K)
        n_unique = len(set(cids))
        se_clustered.append(se)
        within_fracs.append(frac)
        cluster_counts.append(float(n_unique))
    assert all(0 <= f <= 1 for f in within_fracs), "within_fracs out of [0,1]"
    return se_clustered, within_fracs, cluster_counts
