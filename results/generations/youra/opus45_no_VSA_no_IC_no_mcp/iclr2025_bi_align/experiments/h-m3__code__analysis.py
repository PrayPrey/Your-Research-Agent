"""Clustering and statistical analysis for H-M3 attractor experiment."""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from scipy.stats import ttest_ind


def compute_similarity_matrix(embeddings_dict: dict) -> dict:
    """Compute pairwise cosine similarity between model embeddings.

    Args:
        embeddings_dict: {model_id: [n_probes, hidden_dim]} arrays

    Returns:
        Dictionary with similarity matrix and clustering gap metrics
    """
    model_ids = list(embeddings_dict.keys())
    # Mean over probes to get single embedding per model
    model_means = np.stack([embeddings_dict[m].mean(axis=0) for m in model_ids])

    sim = cosine_similarity(model_means)

    method_labels = ["dpo" if "dpo" in m else "rlhf" for m in model_ids]
    within, cross = [], []
    n = len(model_ids)

    for i in range(n):
        for j in range(i + 1, n):
            if method_labels[i] == method_labels[j]:
                within.append(sim[i, j])
            else:
                cross.append(sim[i, j])

    return {
        "model_ids": model_ids,
        "similarity_matrix": sim.tolist(),
        "within_method_sims": within,
        "cross_method_sims": cross,
        "within_mean": float(np.mean(within)) if within else 0.0,
        "cross_mean": float(np.mean(cross)) if cross else 0.0,
        "clustering_gap": float(np.mean(within) - np.mean(cross)) if within and cross else 0.0,
    }


def analyze_clustering(embeddings: np.ndarray, method_labels: list) -> dict:
    """Run K-means clustering and compute silhouette scores.

    Args:
        embeddings: [n_models, hidden_dim] array
        method_labels: List of "dpo" or "rlhf" labels

    Returns:
        Dictionary with clustering metrics
    """
    if len(set(method_labels)) < 2:
        return {
            "silhouette_score": 0.0,
            "dpo_silhouette": 0.0,
            "rlhf_silhouette": 0.0,
            "cluster_labels": [],
            "cluster_alignment": 0.0,
            "error": "Fewer than 2 classes"
        }

    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)

    # Convert string labels to numeric for silhouette
    labels_arr = np.array(method_labels)
    numeric_labels = (labels_arr == "dpo").astype(int)

    score = silhouette_score(embeddings, numeric_labels)
    samples = silhouette_samples(embeddings, numeric_labels)

    # Cluster alignment: how well clusters match method labels
    alignment = max(
        np.mean(cluster_labels[labels_arr == "dpo"] == 0),
        np.mean(cluster_labels[labels_arr == "dpo"] == 1),
    )

    return {
        "silhouette_score": float(score),
        "dpo_silhouette": float(np.mean(samples[labels_arr == "dpo"])),
        "rlhf_silhouette": float(np.mean(samples[labels_arr == "rlhf"])),
        "cluster_labels": cluster_labels.tolist(),
        "cluster_alignment": float(alignment),
    }


def permutation_test(embeddings: np.ndarray, method_labels: list, n_permutations: int = 1000) -> dict:
    """Run permutation test on clustering gap statistic.

    Args:
        embeddings: [n_models, hidden_dim] array
        method_labels: List of "dpo" or "rlhf" labels
        n_permutations: Number of permutation iterations

    Returns:
        Dictionary with observed gap, p-value, significance
    """
    def compute_gap(emb, labels):
        sim = cosine_similarity(emb)
        labels_arr = np.array(labels)
        n = len(labels_arr)
        within, cross = [], []
        for i in range(n):
            for j in range(i + 1, n):
                if labels_arr[i] == labels_arr[j]:
                    within.append(sim[i, j])
                else:
                    cross.append(sim[i, j])
        return np.mean(within) - np.mean(cross) if within and cross else 0.0

    observed_gap = compute_gap(embeddings, method_labels)
    labels_arr = np.array(method_labels)

    np.random.seed(42)
    null_dist = np.empty(n_permutations)
    for k in range(n_permutations):
        shuffled = np.random.permutation(labels_arr)
        null_dist[k] = compute_gap(embeddings, shuffled)

    p_value = float(np.mean(null_dist >= observed_gap))

    return {
        "observed_gap": float(observed_gap),
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def compute_cohens_d(within_sims: list, cross_sims: list) -> dict:
    """Compute Cohen's d effect size.

    Args:
        within_sims: List of within-method similarities
        cross_sims: List of cross-method similarities

    Returns:
        Dictionary with Cohen's d and significance flag
    """
    if not within_sims or not cross_sims:
        return {"cohens_d": 0.0, "effect_significant": False}

    within_arr = np.array(within_sims)
    cross_arr = np.array(cross_sims)

    mean_diff = np.mean(within_arr) - np.mean(cross_arr)
    pooled_std = np.sqrt((np.var(within_arr) + np.var(cross_arr)) / 2)

    if pooled_std == 0:
        d = 0.0
    else:
        d = mean_diff / pooled_std

    return {
        "cohens_d": float(d),
        "effect_significant": abs(d) > 0.3,
    }


def run_full_analysis(embeddings_dict: dict) -> dict:
    """Run complete clustering and statistical analysis.

    Args:
        embeddings_dict: {model_id: [n_probes, hidden_dim]} arrays

    Returns:
        Combined metrics dictionary
    """
    # Similarity matrix and gap
    sim_results = compute_similarity_matrix(embeddings_dict)

    # Prepare model-level embeddings
    model_ids = sim_results["model_ids"]
    model_means = np.stack([embeddings_dict[m].mean(axis=0) for m in model_ids])
    method_labels = ["dpo" if "dpo" in m else "rlhf" for m in model_ids]

    # Clustering analysis
    clustering = analyze_clustering(model_means, method_labels)

    # Permutation test
    perm = permutation_test(model_means, method_labels)

    # Effect size
    effect = compute_cohens_d(
        sim_results["within_method_sims"],
        sim_results["cross_method_sims"]
    )

    # Combine all metrics
    metrics = {
        **sim_results,
        **clustering,
        **perm,
        **effect,
    }

    return metrics
