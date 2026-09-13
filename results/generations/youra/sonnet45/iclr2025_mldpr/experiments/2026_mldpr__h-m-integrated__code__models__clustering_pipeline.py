"""
Clustering Pipeline for h-m-integrated
Semantic K-means clustering
"""

import numpy as np
from sklearn.cluster import KMeans


class ClusteringPipeline:
    """K-means clustering for semantic embeddings."""

    def __init__(self, config):
        """
        Initialize clustering pipeline.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.clustering_config = config.clustering

    def cluster_semantic(self, embeddings: np.ndarray) -> np.ndarray:
        """
        K-means clustering on semantic embeddings.

        Args:
            embeddings: [N, 384] semantic embeddings

        Returns:
            np.ndarray: [N] cluster labels {0, 1}
        """
        print(f"Running K-means clustering (k={self.clustering_config.n_clusters})...")

        clusterer = KMeans(
            n_clusters=self.clustering_config.n_clusters,
            init=self.clustering_config.init_method,
            random_state=self.clustering_config.random_state,
            max_iter=self.clustering_config.max_iter,
            n_init=self.clustering_config.n_init
        )

        labels_pred = clusterer.fit_predict(embeddings)

        # Validate output
        unique_labels = np.unique(labels_pred)
        if len(unique_labels) != self.clustering_config.n_clusters:
            print(f"Warning: K-means produced {len(unique_labels)} clusters "
                  f"(expected {self.clustering_config.n_clusters})")

        print(f"Clustering completed. Cluster distribution: {np.bincount(labels_pred)}")
        return labels_pred
