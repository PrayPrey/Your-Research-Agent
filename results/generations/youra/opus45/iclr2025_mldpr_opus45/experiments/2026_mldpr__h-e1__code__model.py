"""Model implementations for h-e1 DTW clustering experiment."""

import numpy as np
from typing import Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tslearn.clustering import TimeSeriesKMeans

from config import ExperimentConfig


class BaselineModel:
    """KMeans clustering on summary features (mean, std, slope)."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def fit(self, features: np.ndarray, k: int) -> np.ndarray:
        """
        Fit KMeans and return labels.

        Args:
            features: [N, 3] array of summary features
            k: number of clusters

        Returns:
            labels: [N] cluster assignments
        """
        model = KMeans(
            n_clusters=k,
            random_state=self.config.random_state,
            n_init=self.config.n_init,
        )
        return model.fit_predict(features)

    def best_k_silhouette(
        self, features: np.ndarray
    ) -> Tuple[int, float, np.ndarray, Dict[int, float]]:
        """
        Iterate k_range and select best k by silhouette score.

        Args:
            features: [N, 3] array of summary features

        Returns:
            (best_k, best_score, best_labels, all_scores)
        """
        best_k, best_score, best_labels = -1, -np.inf, None
        all_scores: Dict[int, float] = {}

        for k in range(self.config.k_range[0], self.config.k_range[1] + 1):
            labels = self.fit(features, k)
            score = silhouette_score(features, labels)
            all_scores[k] = score
            print(f"  Baseline k={k}: silhouette={score:.4f}")
            if score > best_score:
                best_k, best_score, best_labels = k, score, labels

        return best_k, best_score, best_labels, all_scores


class DTWModel:
    """DTW TimeSeriesKMeans clustering on raw trajectories."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def fit(self, X: np.ndarray, k: int) -> TimeSeriesKMeans:
        """
        Fit DTW clustering model.

        Args:
            X: [N, T, 1] tslearn 3D format array
            k: number of clusters

        Returns:
            Fitted TimeSeriesKMeans model
        """
        model = TimeSeriesKMeans(
            n_clusters=k,
            metric="dtw",
            max_iter=self.config.max_iter,
            n_init=self.config.n_init,
            random_state=self.config.random_state,
            verbose=0,
        )
        model.fit(X)
        return model

    def best_k_silhouette(
        self, X: np.ndarray
    ) -> Tuple[int, float, TimeSeriesKMeans, Dict[int, float]]:
        """
        Iterate k_range and select best k by silhouette score.

        Args:
            X: [N, T, 1] tslearn 3D format array

        Returns:
            (best_k, best_score, best_model, all_scores)
        """
        # Flatten for silhouette computation and handle NaN from padding
        X_flat = X[:, :, 0]  # [N, T]
        X_flat = np.nan_to_num(X_flat, nan=0.0)  # Replace NaN with 0

        best_k, best_score, best_model = -1, -np.inf, None
        all_scores: Dict[int, float] = {}

        for k in range(self.config.k_range[0], self.config.k_range[1] + 1):
            print(f"  Fitting DTW k={k}...")
            model = self.fit(X, k)
            labels = model.labels_  # [N]
            score = silhouette_score(X_flat, labels)
            all_scores[k] = score
            print(f"  DTW k={k}: silhouette={score:.4f}")
            if score > best_score:
                best_k, best_score, best_model = k, score, model

        return best_k, best_score, best_model, all_scores
