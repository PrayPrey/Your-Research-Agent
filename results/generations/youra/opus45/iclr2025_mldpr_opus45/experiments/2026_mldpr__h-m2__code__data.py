"""Data loading for h-m2 Shape Descriptor experiment.

Loads time series data from h-e1 cache and performs DTW clustering to get
centroids and cluster assignments for shape descriptor analysis.
"""

import numpy as np
import json
import os
from typing import List, Tuple, Dict

from config import ExperimentConfig


def load_raw_series(config: ExperimentConfig) -> List[np.ndarray]:
    """
    Load raw time series from h-e1 cache.

    Returns:
        List of numpy arrays, each containing a time series (variable length, 0-padded)
    """
    cache_path = os.path.join(os.path.dirname(__file__), config.h_e1_cache_path)

    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"h-e1 cache not found at {cache_path}")

    with open(cache_path, 'r') as f:
        cached = json.load(f)

    # Extract series, removing zero-padding
    series_list = []
    for item in cached:
        series = np.array(item["series"], dtype=np.float64)
        # Remove trailing zeros (padding)
        nonzero_idx = np.where(series != 0)[0]
        if len(nonzero_idx) > 0:
            series = series[:nonzero_idx[-1] + 1]
        series_list.append(series)

    print(f"Loaded {len(series_list)} time series from h-e1 cache")
    return series_list


def preprocess_series(raw_series: List[np.ndarray]) -> np.ndarray:
    """
    Preprocess time series: log-transform + z-score normalize.

    Returns:
        3D array [N, T, 1] in tslearn format
    """
    from tslearn.utils import to_time_series_dataset
    from tslearn.preprocessing import TimeSeriesScalerMeanVariance

    # Log transform (shift to positive first)
    processed = []
    for ts in raw_series:
        min_val = np.min(ts)
        if min_val <= 0:
            ts_shifted = ts - min_val + 1
        else:
            ts_shifted = ts
        processed.append(np.log1p(ts_shifted))

    # Convert to tslearn 3D format
    X = to_time_series_dataset(processed)

    # Z-score normalization
    scaler = TimeSeriesScalerMeanVariance()
    X_scaled = scaler.fit_transform(X)

    return X_scaled


def perform_clustering(X: np.ndarray, config: ExperimentConfig) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform DTW clustering to get centroids and labels.

    Args:
        X: [N, T, 1] preprocessed time series
        config: experiment configuration

    Returns:
        (centroids, labels)
        centroids: (k, T) cluster centroids
        labels: (N,) cluster assignments
    """
    from tslearn.clustering import TimeSeriesKMeans

    print(f"Performing DTW clustering with k={config.n_clusters}...")

    model = TimeSeriesKMeans(
        n_clusters=config.n_clusters,
        metric="dtw",
        max_iter=50,
        n_init=3,
        random_state=config.random_state,
        verbose=1,
    )

    labels = model.fit_predict(X)

    # Extract centroids (remove trailing dimension)
    centroids = model.cluster_centers_[:, :, 0]  # (k, T)

    print(f"Clustering complete. Centroids shape: {centroids.shape}")

    return centroids, labels


def load_series_and_clusters(config: ExperimentConfig) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray]:
    """
    Load time series and perform clustering to get centroids and labels.

    Returns:
        (all_series, cluster_labels, centroids)
        all_series: List[np.ndarray] raw series (variable length)
        cluster_labels: (N,) int array
        centroids: (k, T) float array
    """
    # Load raw series
    all_series = load_raw_series(config)

    # Preprocess for clustering
    X = preprocess_series(all_series)

    # Perform clustering
    centroids, labels = perform_clustering(X, config)

    return all_series, labels, centroids


def get_cluster_members(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    cluster_id: int
) -> List[np.ndarray]:
    """
    Return all series assigned to given cluster_id.

    Returns:
        List[np.ndarray] of member series
    """
    indices = np.where(cluster_labels == cluster_id)[0]
    return [all_series[i] for i in indices]


def validate_centroids(centroids: np.ndarray, config: ExperimentConfig) -> Tuple[bool, Dict]:
    """
    Validate centroid shape and data quality.

    Returns:
        (passed, report)
    """
    k, T = centroids.shape

    has_nan = np.isnan(centroids).any()
    has_inf = np.isinf(centroids).any()
    k_valid = k == config.n_clusters

    report = {
        "shape": centroids.shape,
        "expected_k": config.n_clusters,
        "actual_k": k,
        "T": T,
        "has_nan": has_nan,
        "has_inf": has_inf,
        "k_valid": k_valid,
    }

    passed = k_valid and not has_nan and not has_inf
    report["passed"] = passed

    return passed, report
