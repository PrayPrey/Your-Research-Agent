"""Configuration for h-e1 DTW Time Series Clustering experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for DTW clustering experiment."""

    # Data collection
    min_downloads: int = 100
    min_months: int = 12
    target_n_datasets: int = 500

    # Clustering
    k_range: tuple = (3, 8)
    max_iter: int = 10
    n_init: int = 2
    random_state: int = 42

    # Bootstrap stability
    n_bootstrap: int = 100
    bootstrap_ratio: float = 0.8

    # Evaluation thresholds (gate criteria)
    silhouette_threshold: float = 0.25
    jaccard_threshold: float = 0.65

    # Output paths
    figures_dir: str = "h-e1/figures"
    output_path: str = "h-e1/04_validation.md"
