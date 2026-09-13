"""Configuration for h-m3 Archetype Recovery experiment.

Implements ExperimentConfig dataclass with alignment threshold,
normalization ranges, and archetype profile definitions.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple


# Archetype profiles (normalized shape descriptor targets)
ARCHETYPE_PROFILES: Dict[str, Dict[str, float]] = {
    "sustained_growth": {
        "growth_ratio": 0.8,
        "peak_timing": 0.9,
        "changepoint_count": 0.2,
        "derivative_variance": 0.2,
    },
    "flash_in_pan": {
        "growth_ratio": 0.3,
        "peak_timing": 0.2,
        "changepoint_count": 0.8,
        "derivative_variance": 0.8,
    },
    "plateau": {
        "growth_ratio": 0.5,
        "peak_timing": 0.5,
        "changepoint_count": 0.2,
        "derivative_variance": 0.1,
    },
    "slow_burn": {
        "growth_ratio": 0.7,
        "peak_timing": 0.8,
        "changepoint_count": 0.1,
        "derivative_variance": 0.2,
    },
    "revival": {
        "growth_ratio": 0.4,
        "peak_timing": 0.6,
        "changepoint_count": 0.6,
        "derivative_variance": 0.5,
    },
}

DESCRIPTOR_ORDER = ["growth_ratio", "peak_timing", "changepoint_count", "derivative_variance"]


@dataclass
class ExperimentConfig:
    """Configuration for h-m3 archetype recovery experiment."""

    # Data parameters
    n_clusters: int = 4
    n_archetypes: int = 5
    random_state: int = 42

    # Alignment gate parameters
    alignment_threshold: float = 0.70
    min_archetypes_recovered: int = 3

    # Normalization ranges (from h-m2 observed values)
    norm_growth_ratio: Tuple[float, float] = (0.3, 0.6)
    norm_peak_timing: Tuple[float, float] = (0.0, 0.03)
    norm_changepoint_count: Tuple[float, float] = (0.0, 5.0)
    norm_derivative_variance: Tuple[float, float] = (0.1, 0.4)

    # Figure output settings
    figure_dpi: int = 300
    figure_format: str = "png"

    # Paths (overridden in main.py with absolute paths at runtime)
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"
    figures_dir: str = "h-m3/figures"
    output_path: str = "h-m3/04_validation.md"

    # h-m2 config params (needed for ShapeDescriptorAnalyzer)
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3

    def get_norm_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Return normalization ranges for all descriptors."""
        return {
            "growth_ratio": self.norm_growth_ratio,
            "peak_timing": self.norm_peak_timing,
            "changepoint_count": self.norm_changepoint_count,
            "derivative_variance": self.norm_derivative_variance,
        }
