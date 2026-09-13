"""Benchmark clustering analysis for H-E1 Experiment."""

import numpy as np
from typing import Dict, Tuple
from scipy.stats import gaussian_kde
from scipy.spatial.distance import jensenshannon, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score
from config import KDE_BANDWIDTH, ENTROPY_SUPPORT_RANGE, ENTROPY_SUPPORT_POINTS, CLUSTER_K_RANGE, LINKAGE_METHOD


class BenchmarkClusteringAnalyzer:
    """Cluster benchmarks by JS-divergence of entropy distributions."""

    def __init__(self, kde_bandwidth: str = KDE_BANDWIDTH):
        self.kde_bandwidth = kde_bandwidth
        self.support = np.linspace(
            ENTROPY_SUPPORT_RANGE[0],
            ENTROPY_SUPPORT_RANGE[1],
            ENTROPY_SUPPORT_POINTS
        )

    def fit_kde(self, entropies: np.ndarray) -> gaussian_kde:
        """Fit KDE to entropy distribution."""
        entropies = np.clip(entropies, 1e-6, None)
        return gaussian_kde(entropies, bw_method=self.kde_bandwidth)

    def js_divergence_matrix(self, kdes: Dict[str, gaussian_kde]) -> np.ndarray:
        """Compute 6x6 JS-divergence matrix.

        Returns symmetric matrix with zero diagonal.
        """
        names = list(kdes.keys())
        n = len(names)

        pdfs = {}
        for name, kde in kdes.items():
            pdf = kde(self.support)
            pdf = pdf / pdf.sum()
            pdfs[name] = pdf

        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                js = jensenshannon(pdfs[names[i]], pdfs[names[j]])
                matrix[i, j] = js
                matrix[j, i] = js

        return matrix

    def cluster(self, js_matrix: np.ndarray) -> Tuple[np.ndarray, float, int]:
        """Hierarchical clustering with Ward linkage.

        Tests k=2..4, returns (labels, best_silhouette, best_k).
        """
        condensed = squareform(js_matrix, checks=False)
        Z = linkage(condensed, method=LINKAGE_METHOD)

        best_score = -1.0
        best_labels = None
        best_k = 2

        for k in range(CLUSTER_K_RANGE[0], CLUSTER_K_RANGE[1] + 1):
            labels = fcluster(Z, k, criterion="maxclust")
            if len(np.unique(labels)) < 2:
                continue
            score = silhouette_score(js_matrix, labels, metric="precomputed")
            if score > best_score:
                best_score = score
                best_labels = labels
                best_k = k

        return best_labels, best_score, best_k

    def verify_mechanism(self, js_matrix: np.ndarray, labels: np.ndarray, silhouette: float) -> bool:
        """Verify mechanism activation per PRD protocol."""
        checks = {
            "js_matrix_shape": js_matrix.shape == (6, 6),
            "js_matrix_symmetric": np.allclose(js_matrix, js_matrix.T),
            "js_matrix_diagonal_zero": np.allclose(np.diag(js_matrix), 0, atol=1e-6),
            "cluster_labels_valid": len(np.unique(labels)) >= 2,
            "silhouette_in_range": -1 <= silhouette <= 1,
        }

        print("Mechanism Verification:")
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {check}: {status}")

        return all(checks.values())
