"""Variance analysis for H-M1: intra/inter-cluster TE variance."""
import numpy as np
from collections import defaultdict, Counter


def filter_eligible_questions(
    questions: list,
    cluster_assignments: dict,
    min_cluster_size: int = 2,
) -> list:
    """Return question IDs where >=1 NLI cluster has >=min_cluster_size members."""
    eligible = []
    for q in questions:
        qid = q["question_id"]
        clusters = cluster_assignments.get(qid, {})
        cluster_sizes = Counter(clusters.values())
        if any(size >= min_cluster_size for size in cluster_sizes.values()):
            eligible.append(qid)
    assert len(eligible) >= 20, f"Only {len(eligible)} eligible questions; check NLI clustering"
    print(f"[H-M1] Eligible questions: {len(eligible)}/{len(questions)}")
    return eligible


def compute_intra_cluster_variance(
    cluster_assignments: dict,
    per_sample_te: list,
    min_cluster_size: int = 2,
) -> float:
    """Mean variance across multi-member clusters. Returns None if no cluster has >=2 members."""
    cluster_groups = defaultdict(list)
    for idx, cid in cluster_assignments.items():
        if idx < len(per_sample_te):
            cluster_groups[cid].append(per_sample_te[idx])
    variances = [np.var(members) for members in cluster_groups.values()
                 if len(members) >= min_cluster_size]
    variances = [v for v in variances if not np.isnan(v)]
    if not variances:
        return None
    return float(np.mean(variances))


def compute_inter_cluster_variance(
    cluster_assignments: dict,
    per_sample_te: list,
) -> float:
    """Variance across cluster means (between-cluster control)."""
    cluster_groups = defaultdict(list)
    for idx, cid in cluster_assignments.items():
        if idx < len(per_sample_te):
            cluster_groups[cid].append(per_sample_te[idx])
    cluster_means = [np.mean(m) for m in cluster_groups.values()]
    if len(cluster_means) <= 1:
        return None
    return float(np.var(cluster_means))


def run_analysis(
    questions: list,
    cluster_assignments: dict,
    per_sample_te: dict,
    se_scores: list,
) -> list:
    """Per-question analysis. Returns list of result dicts."""
    se_arr = np.array(se_scores)
    se_median = float(np.median(se_arr))

    results = []
    for i, q in enumerate(questions):
        qid = q["question_id"]
        cas = cluster_assignments.get(qid, {})
        pste = per_sample_te.get(qid, [])
        se = se_scores[i] if i < len(se_scores) else 0.0

        cluster_sizes = Counter(cas.values())
        n_clusters = len(cluster_sizes)
        n_multi = sum(1 for s in cluster_sizes.values() if s >= 2)
        has_paraphrase = n_multi >= 1

        intra_var = compute_intra_cluster_variance(cas, pste) if has_paraphrase else None
        inter_var = compute_inter_cluster_variance(cas, pste)

        results.append({
            "qid": qid,
            "n_clusters": n_clusters,
            "n_multi_member_clusters": n_multi,
            "mean_intra_var": intra_var,
            "inter_var": inter_var,
            "has_paraphrase": has_paraphrase,
            "se_score": se,
            "high_uncertainty": se > se_median,
            "per_sample_te": pste,
        })
    return results
