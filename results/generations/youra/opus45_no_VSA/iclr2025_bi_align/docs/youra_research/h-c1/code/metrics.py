import numpy as np
from sklearn.metrics import silhouette_score

from agency import classify_cluster_as_agency
import hc1_config as config


def compute_coverage(topics):
    """Compute fraction of samples assigned to non-noise clusters."""
    topics_arr = np.array(topics)
    valid = topics_arr != -1
    return valid.sum() / len(topics_arr)


def compute_silhouette(embeddings, topics):
    """Compute silhouette score on valid (non-noise) clusters."""
    topics_arr = np.array(topics)
    valid_mask = topics_arr != -1

    if valid_mask.sum() <= 1:
        return 0.0

    unique_labels = np.unique(topics_arr[valid_mask])
    if len(unique_labels) < 2:
        return 0.0

    return silhouette_score(embeddings[valid_mask], topics_arr[valid_mask])


def compute_agency_pattern_rate(topic_model):
    """Compute fraction of clusters classified as agency patterns."""
    topic_info = topic_model.get_topic_info()

    total_clusters = 0
    agency_clusters = 0
    agency_topic_ids = []

    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        if topic_id == -1:
            continue

        total_clusters += 1
        keywords_list = topic_model.get_topic_keywords(topic_id)
        keywords_str = " ".join(w for w, _ in keywords_list)

        is_agency, match_count = classify_cluster_as_agency(keywords_str)
        if is_agency:
            agency_clusters += 1
            agency_topic_ids.append(topic_id)

    agency_rate = agency_clusters / total_clusters if total_clusters > 0 else 0.0

    return {
        "agency_pattern_rate": agency_rate,
        "total_clusters": total_clusters,
        "agency_clusters": agency_clusters,
        "agency_topic_ids": agency_topic_ids,
    }


def verify_mechanism(topics, topic_embeddings):
    """Verify clustering mechanism validity."""
    topics_arr = np.array(topics)
    unique_topics = set(topics_arr) - {-1}
    n_topics = len(unique_topics)

    coverage = compute_coverage(topics)

    checks = {
        "n_topics_ok": n_topics >= 3,
        "coverage_ok": coverage > 0.5,
        "topics_distinct": True,
    }

    if topic_embeddings is not None and len(topic_embeddings) > 1:
        pairwise_corr = np.corrcoef(topic_embeddings)
        off_diag = pairwise_corr[np.triu_indices_from(pairwise_corr, k=1)]
        mean_corr = np.nanmean(off_diag) if len(off_diag) > 0 else 0.0
        checks["topics_distinct"] = mean_corr < 0.9
        checks["mean_topic_correlation"] = float(mean_corr)

    checks["n_topics"] = n_topics
    checks["coverage"] = coverage
    checks["verification_passed"] = all([
        checks["n_topics_ok"],
        checks["coverage_ok"],
        checks["topics_distinct"],
    ])

    return checks
