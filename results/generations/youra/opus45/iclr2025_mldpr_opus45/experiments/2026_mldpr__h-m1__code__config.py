"""Configuration for h-m1 PELT Changepoint Detection experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for PELT changepoint detection experiment."""

    # Data (consistent with h-e1 for controlled comparison)
    min_series_length: int = 12
    target_n_series: int = 500
    random_state: int = 42

    # PELT parameters
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    # jump=1 evaluates all positions (ruptures default=5); needed for short series
    pelt_jump: int = 1

    # Penalty selection (CROPS-style BIC grid search)
    penalty_range: tuple = (1.0, 100.0)
    # 20 log-spaced values per CROPS methodology (Haynes et al. 2017)
    n_penalties: int = 20

    # Gate threshold
    detection_rate_threshold: float = 0.50

    # Output paths (absolute paths overridden in main.py at runtime)
    figures_dir: str = "h-m1/figures"
    output_path: str = "h-m1/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
