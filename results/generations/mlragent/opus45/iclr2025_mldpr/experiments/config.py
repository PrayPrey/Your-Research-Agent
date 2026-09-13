"""
Configuration for Dynamic Dataset Health Scores (DDHS) experiments
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ExperimentConfig:
    """Configuration for DDHS experiments"""

    # Data settings
    num_datasets: int = 100  # Number of synthetic datasets to simulate
    num_historical_snapshots: int = 12  # Monthly snapshots
    random_seed: int = 42

    # Health score weights (default)
    usi_weight: float = 0.2  # Usage Saturation Index
    fs_weight: float = 0.2   # Freshness Score
    dcs_weight: float = 0.2  # Documentation Completeness Score
    cri_weight: float = 0.2  # Community Responsiveness Index
    eas_weight: float = 0.2  # Ethical Alert System

    # USI parameters
    usi_alpha: float = 0.4  # Citation velocity weight
    usi_beta: float = 0.3   # Download concentration weight
    usi_gamma: float = 0.3  # Publication saturation weight

    # CRI parameters
    cri_omega1: float = 0.4  # Response score weight
    cri_omega2: float = 0.3  # Update frequency weight
    cri_omega3: float = 0.3  # Interaction quality weight

    # Freshness parameters
    freshness_threshold: float = 2.0  # KL divergence threshold

    # Output settings
    output_dir: str = "outputs"
    results_dir: str = "results"
    log_file: str = "log.txt"

    # Experiment settings
    deprecation_rate: float = 0.15  # Rate of datasets to simulate as deprecated
    use_llm_for_docs: bool = False  # Whether to use LLM for documentation scoring

    # Device settings
    device: str = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"

    def get_weights(self) -> Dict[str, float]:
        """Get all health dimension weights"""
        return {
            'USI': self.usi_weight,
            'FS': self.fs_weight,
            'DCS': self.dcs_weight,
            'CRI': self.cri_weight,
            'EAS': self.eas_weight
        }


@dataclass
class BaselineConfig:
    """Configuration for baseline methods"""

    # Simple heuristic baseline
    use_downloads_only: bool = True  # Only use download counts

    # Static scoring baseline
    use_static_weights: bool = True  # Use fixed equal weights

    # Data Shapley baseline (simplified)
    num_shapley_iterations: int = 50
    shapley_sample_size: int = 20


# Default configuration instance
DEFAULT_CONFIG = ExperimentConfig()
DEFAULT_BASELINE_CONFIG = BaselineConfig()
