"""Data loading for h-m3 Archetype Recovery experiment.

Loads time series from h-e1 cache, performs DTW clustering to get centroids,
and computes shape descriptors using h-m2's ShapeDescriptorAnalyzer.
"""

import sys
import os
import json
import numpy as np
from typing import Dict, List, Tuple

from config import ExperimentConfig


def load_raw_series(config: ExperimentConfig) -> List[np.ndarray]:
    """
    Load raw time series from h-e1 cache.

    Returns:
        List of numpy arrays, each containing a time series
    """
    cache_path = config.h_e1_cache_path

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
        verbose=0,
    )

    labels = model.fit_predict(X)

    # Extract centroids (remove trailing dimension)
    centroids = model.cluster_centers_[:, :, 0]  # (k, T)

    print(f"Clustering complete. Centroids shape: {centroids.shape}")

    return centroids, labels


def load_cluster_centroids(config: ExperimentConfig) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load h-e1 cache, preprocess, and DTW cluster to get centroids and labels.

    Returns:
        (centroids, labels)
        centroids: (k, T) float array
        labels: (N,) int array
    """
    # Load raw series
    raw_series = load_raw_series(config)

    # Preprocess for clustering
    X = preprocess_series(raw_series)

    # Perform clustering
    centroids, labels = perform_clustering(X, config)

    return centroids, labels


def compute_shape_descriptors(
    centroids: np.ndarray,
    config: ExperimentConfig
) -> Dict[int, Dict[str, float]]:
    """
    Compute shape descriptors per centroid using h-m2 ShapeDescriptorAnalyzer.

    Returns:
        Dict mapping cluster_id to {descriptor_name: value}
    """
    # Import ShapeDescriptorAnalyzer from h-m2 using importlib to avoid path conflicts
    import importlib.util
    h_m2_model_path = os.path.join(os.path.dirname(__file__), "../../h-m2/code/model.py")
    spec = importlib.util.spec_from_file_location("h_m2_model", h_m2_model_path)
    h_m2_model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h_m2_model)
    ShapeDescriptorAnalyzer = h_m2_model.ShapeDescriptorAnalyzer

    analyzer = ShapeDescriptorAnalyzer(config)

    profiles = {}
    for i in range(centroids.shape[0]):
        profiles[i] = analyzer.compute_descriptors(centroids[i])

    print(f"Computed shape descriptors for {len(profiles)} clusters")

    return profiles


def load_data(config: ExperimentConfig) -> Dict[int, Dict[str, float]]:
    """
    Top-level loader: returns cluster_profiles dict ready for archetype matching.

    Returns:
        cluster_profiles: {cluster_id: {descriptor: value, ...}}
    """
    # Load centroids
    centroids, labels = load_cluster_centroids(config)

    # Compute shape descriptors
    cluster_profiles = compute_shape_descriptors(centroids, config)

    return cluster_profiles


def validate_cluster_profiles(
    cluster_profiles: Dict[int, Dict[str, float]],
    config: ExperimentConfig
) -> Tuple[bool, dict]:
    """
    Validate k=4 clusters with 4 descriptors each.

    Returns:
        (passed, report)
    """
    expected_k = config.n_clusters
    expected_descriptors = ["growth_ratio", "peak_timing", "changepoint_count", "derivative_variance"]

    actual_k = len(cluster_profiles)
    k_valid = actual_k == expected_k

    descriptor_valid = True
    missing_descriptors = []
    for cluster_id, profile in cluster_profiles.items():
        for desc in expected_descriptors:
            if desc not in profile:
                descriptor_valid = False
                missing_descriptors.append(f"Cluster {cluster_id}: {desc}")

    report = {
        "expected_k": expected_k,
        "actual_k": actual_k,
        "k_valid": k_valid,
        "expected_descriptors": expected_descriptors,
        "descriptor_valid": descriptor_valid,
        "missing_descriptors": missing_descriptors,
    }

    passed = k_valid and descriptor_valid
    report["passed"] = passed

    return passed, report
