"""Configuration for h-m2 Shape Descriptor Differentiation experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for shape descriptor differentiation experiment."""

    # Data (consistent with h-e1 for controlled comparison)
    n_clusters: int = 4  # Use k=4 for more nuanced analysis (k=3 was optimal in h-e1)
    n_series: int = 500
    random_state: int = 42

    # Shape descriptor parameters
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3

    # Bootstrap parameters
    n_bootstrap: int = 100
    bootstrap_seed: int = 42

    # Gate threshold
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2

    # Output paths (overridden in main.py at runtime)
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"

    # h-e1 data paths
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"
