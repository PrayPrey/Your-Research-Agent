"""Configuration for H-M-Integrated Linguistic Mechanism Validation.

This module extends the h-e1 configuration with mechanism-specific parameters.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import Set, List

# Add h-e1 code path
h_e1_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
if h_e1_path not in sys.path:
    sys.path.insert(0, h_e1_path)

try:
    from config import Config as H_E1_Config
except ImportError:
    # Fallback if h-e1 config not available
    @dataclass
    class H_E1_Config:
        dataset_name: str = "Anthropic/hh-rlhf"
        splits: List[str] = field(default_factory=lambda: ["train", "test"])
        random_seed: int = 42
        spacy_model: str = "en_core_web_sm"
        hedging_markers: Set[str] = field(default_factory=lambda: {
            'perhaps', 'maybe', 'might', 'could', 'possibly',
            'probably', 'likely', 'seems', 'appears', 'suggests',
            'tend', 'often', 'sometimes', 'generally', 'typically'
        })
        alternative_patterns: List[str] = field(default_factory=lambda: [
            r'\byou (could|might|may)\b',
            r'\b(one|another) (option|approach|alternative|way)\b',
            r'\balternatively\b',
            r'\bon the other hand\b',
            r'\byou (can|have) the option\b'
        ])


@dataclass
class MechanismConfig:
    """Configuration for H-M-Integrated mechanism validation."""

    # Inherit h-e1 config
    base_config: H_E1_Config = field(default_factory=H_E1_Config)

    # Gate thresholds (from Phase 2B success criteria)
    cohens_d_threshold: float = 0.15
    p_value_threshold: float = 0.05
    cronbach_alpha_threshold: float = 0.7
    min_passing_splits: int = 2

    # Output paths
    output_dir: str = "."
    figures_dir: str = "figures"
    results_dir: str = "results"
    results_file: str = "results/statistics.json"
    validation_report: str = "04_validation.md"

    # Processing configuration
    batch_size: int = 1000
    random_seed: int = 42

    # Visualization configuration
    dpi: int = 300
    figsize_bar: tuple = (10, 6)
    figsize_forest: tuple = (8, 6)
    figsize_density: tuple = (12, 4)
    figsize_hist: tuple = (8, 6)
    figsize_heatmap: tuple = (8, 6)
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "Set2"
