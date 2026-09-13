"""Gap statistic clustering for response matrix analysis."""

import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path
from config import GAP_STATISTIC, TASKS


def gap_statistic(X: np.ndarray, n_refs: int = 500, max_k: int = 6) -> tuple:
    """Compute gap statistic to find optimal k.

    Returns: (k_star, gap_values, se_values, significant)
    """
    n_samples, n_features = X.shape
    gaps = []
    sks = []

    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        wk = compute_wk(X, kmeans.labels_, kmeans.cluster_centers_)
        log_wk = np.log(wk) if wk > 0 else 0

        ref_log_wks = []
        for _ in range(n_refs):
            X_ref = np.random.uniform(X.min(axis=0), X.max(axis=0), size=(n_samples, n_features))
            kmeans_ref = KMeans(n_clusters=k, random_state=None, n_init=3)
            kmeans_ref.fit(X_ref)
            wk_ref = compute_wk(X_ref, kmeans_ref.labels_, kmeans_ref.cluster_centers_)
            ref_log_wks.append(np.log(wk_ref) if wk_ref > 0 else 0)

        ref_log_wks = np.array(ref_log_wks)
        gap = ref_log_wks.mean() - log_wk
        sk = ref_log_wks.std() * np.sqrt(1 + 1/n_refs)

        gaps.append(gap)
        sks.append(sk)

    k_star = 1
    for k in range(1, len(gaps)):
        if gaps[k-1] >= gaps[k] - sks[k]:
            k_star = k
            break
    else:
        k_star = len(gaps)

    significant = k_star > 1
    return k_star, gaps, sks, significant


def compute_wk(X: np.ndarray, labels: np.ndarray, centers: np.ndarray) -> float:
    """Compute within-cluster dispersion."""
    wk = 0.0
    for k in range(len(centers)):
        cluster_points = X[labels == k]
        if len(cluster_points) > 0:
            wk += np.sum((cluster_points - centers[k]) ** 2)
    return wk


def find_optimal_clusters(response_matrix: np.ndarray, n_refs: int = 500, max_k: int = 6):
    """Find optimal clusters using gap statistic."""
    k_star, gaps, sks, significant = gap_statistic(response_matrix, n_refs, max_k)

    gap_df = {
        "n_clusters": list(range(1, max_k + 1)),
        "gap_value": gaps,
        "sk": sks,
    }

    return k_star, gap_df, significant


def compute_silhouette(response_matrix: np.ndarray, k_star: int) -> float:
    """Compute silhouette score for k_star clusters."""
    if k_star <= 1:
        return 0.0

    kmeans = KMeans(n_clusters=k_star, random_state=42, n_init=10)
    labels = kmeans.fit_predict(response_matrix)
    return silhouette_score(response_matrix, labels)


def get_cluster_labels(response_matrix: np.ndarray, k_star: int) -> dict:
    """Get cluster assignment for each task."""
    if k_star <= 1:
        return {task: 0 for task in TASKS}

    kmeans = KMeans(n_clusters=k_star, random_state=42, n_init=10)
    labels = kmeans.fit_predict(response_matrix)
    return {task: int(label) for task, label in zip(TASKS, labels)}


def main():
    """Run clustering analysis on response matrix."""
    base_dir = Path(__file__).parent.parent
    matrix_path = base_dir / "response_matrix.npy"

    print("Loading response matrix...")
    response_matrix = np.load(matrix_path)
    print(f"Matrix shape: {response_matrix.shape}")

    print(f"\nRunning gap statistic (n_refs={GAP_STATISTIC['n_refs']}, max_k={GAP_STATISTIC['max_k']})...")
    k_star, gap_df, significant = find_optimal_clusters(
        response_matrix,
        n_refs=GAP_STATISTIC["n_refs"],
        max_k=GAP_STATISTIC["max_k"],
    )

    print(f"\nOptimal k: {k_star}")
    print(f"Significant (k > 1): {significant}")

    silhouette = compute_silhouette(response_matrix, k_star)
    print(f"Silhouette score: {silhouette:.4f}")

    cluster_labels = get_cluster_labels(response_matrix, k_star)

    gap_results = {
        "k_star": k_star,
        "significant": significant,
        "silhouette_score": silhouette,
        "gap_df": gap_df,
        "gate_passed": k_star > 1 and significant,
    }

    with open(base_dir / "gap_results.json", "w") as f:
        json.dump(gap_results, f, indent=2)
    print(f"\nSaved: gap_results.json")

    with open(base_dir / "cluster_labels.json", "w") as f:
        json.dump(cluster_labels, f, indent=2)
    print(f"Saved: cluster_labels.json")

    return gap_results, cluster_labels


if __name__ == "__main__":
    main()
