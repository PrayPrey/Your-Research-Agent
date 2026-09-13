"""
Clustering Analysis for Alignment Method Signatures
"""

import numpy as np
from typing import List, Dict
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import ttest_ind


class AlignmentClusterer:
    """PCA + k-means clustering with effect size computation."""

    def __init__(self, k: int = 3, random_state: int = 42):
        """Initialize with k clusters and random seed."""
        self.k = k
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3, random_state=random_state)
        self.kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=random_state)

    def prepare_features(self, signatures: List[Dict[str, float]]) -> np.ndarray:
        """
        Convert signature dicts to feature matrix.
        Returns X: [N, 5]
        """
        features = []
        for sig in signatures:
            feature_vec = [
                sig["correctness"],
                sig["cyclomatic"],
                sig["ast_depth"],
                sig["runtime_ms"],
                sig["memory_kb"]
            ]
            features.append(feature_vec)

        X = np.array(features)
        return X

    def fit_pca(self, X: np.ndarray) -> np.ndarray:
        """
        PCA transform to 3D.
        X: [N, 5] -> X_pca: [N, 3]
        """
        # Standardize first
        X_scaled = self.scaler.fit_transform(X)

        # PCA to 3D
        X_pca = self.pca.fit_transform(X_scaled)

        print(f"PCA explained variance: {self.pca.explained_variance_ratio_}")
        print(f"Total variance explained: {self.pca.explained_variance_ratio_.sum():.3f}")

        return X_pca

    def fit_kmeans(self, X_pca: np.ndarray) -> np.ndarray:
        """
        K-means clustering.
        X_pca: [N, 3] -> labels: [N]
        """
        labels = self.kmeans.fit_predict(X_pca)
        return labels

    def compute_cohens_d(self, X_pca: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute Cohen's d effect size for clustering.
        Measures intercluster distance vs intracluster variance.
        Returns scalar d.
        """
        # Compute cluster centroids
        centroids = []
        for cluster_id in range(self.k):
            cluster_points = X_pca[labels == cluster_id]
            if len(cluster_points) > 0:
                centroids.append(cluster_points.mean(axis=0))

        if len(centroids) < 2:
            return 0.0

        centroids = np.array(centroids)

        # Compute intercluster distances (between centroids)
        intercluster_dists = []
        for i in range(len(centroids)):
            for j in range(i + 1, len(centroids)):
                dist = np.linalg.norm(centroids[i] - centroids[j])
                intercluster_dists.append(dist)

        mean_intercluster = np.mean(intercluster_dists)

        # Compute intracluster variance (pooled standard deviation)
        intracluster_vars = []
        for cluster_id in range(self.k):
            cluster_points = X_pca[labels == cluster_id]
            if len(cluster_points) > 1:
                cluster_var = np.var(cluster_points, ddof=1, axis=0).mean()
                intracluster_vars.append(cluster_var)

        if not intracluster_vars:
            return 0.0

        pooled_std = np.sqrt(np.mean(intracluster_vars))

        # Cohen's d = mean_intercluster / pooled_std
        if pooled_std == 0:
            return 0.0

        cohens_d = mean_intercluster / pooled_std

        return cohens_d

    def compute_silhouette(self, X_pca: np.ndarray, labels: np.ndarray) -> float:
        """
        Silhouette score.
        Returns scalar in [-1, 1].
        """
        if len(np.unique(labels)) < 2:
            return 0.0

        try:
            score = silhouette_score(X_pca, labels)
            return score
        except:
            return 0.0

    def compute_purity(self, labels: np.ndarray, alignment_types: List[str]) -> float:
        """
        Cluster purity by alignment type.
        Returns scalar in [0, 1].
        """
        # Map alignment types to numeric categories
        type_map = {"execution": 0, "preference": 1, "baseline": 2}
        type_labels = np.array([type_map.get(t, -1) for t in alignment_types])

        # For each cluster, find the most common alignment type
        total_correct = 0
        for cluster_id in range(self.k):
            cluster_mask = (labels == cluster_id)
            cluster_types = type_labels[cluster_mask]

            if len(cluster_types) == 0:
                continue

            # Most common type in this cluster
            unique, counts = np.unique(cluster_types, return_counts=True)
            most_common_count = counts.max()
            total_correct += most_common_count

        purity = total_correct / len(labels) if len(labels) > 0 else 0.0
        return purity
