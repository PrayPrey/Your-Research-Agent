"""Configuration for H-E1 Linguistic Marker Extraction.

This module defines all configuration parameters for the linguistic marker
extraction and analysis pipeline.
"""

from dataclasses import dataclass, field
from typing import Set, List


@dataclass
class Config:
    """Global configuration for H-E1 linguistic marker extraction and analysis."""

    # Dataset Configuration
    dataset_name: str = "Anthropic/hh-rlhf"
    splits: List[str] = field(default_factory=lambda: ["train", "test"])
    random_seed: int = 42

    # NLP Processing
    spacy_model: str = "en_core_web_sm"

    # Linguistic Marker Definitions
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

    # Gate Criteria
    gate_threshold_cv: float = 0.3
    gate_threshold_precision: float = 0.9

    # Output Configuration
    output_dir: str = "."
    features_file: str = "h_e1_features.csv"
    statistics_file: str = "h_e1_statistics.json"
    figures_dir: str = "figures"
    validation_report: str = "04_validation.md"

    # Processing Configuration
    normalize_per_n_words: int = 100
    min_word_count: int = 1
    batch_size: int = 1000

    # Visualization Configuration
    dpi: int = 300
    figsize_bar: tuple = (8, 6)
    figsize_hist: tuple = (10, 6)
    figsize_box: tuple = (12, 6)
    figsize_scatter: tuple = (8, 8)
    style: str = "seaborn-v0_8-darkgrid"
    palette: str = "Set2"
