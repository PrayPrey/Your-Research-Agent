"""Configuration for H-M2 Hidden State Drift Analysis."""
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class AnalysisConfig:
    # Models
    teacher_name: str = "microsoft/phi-1_5"
    mohawk_name: str = "goombalab/phi-mamba"
    cab_name: str = "wph6/CAB"
    teacher_dim: int = 2048

    # Dataset
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    min_doc_chars: int = 8192
    num_samples: int = 500

    # Analysis grid
    target_lengths: List[int] = field(default_factory=lambda: [512, 1024, 1536, 2048])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])

    # Runtime
    batch_size: int = 8
    seed: int = 42
    device: str = "cuda"
    dtype: str = "float16"

    # Output
    output_dir: str = "results"
    figures_dir: str = "figures"
    results_filename: str = "drift_results.json"


def validate_config(cfg: AnalysisConfig) -> None:
    """Validate config and create output directories."""
    assert cfg.target_lengths == sorted(cfg.target_lengths), "target_lengths must be sorted"
    assert cfg.teacher_dim > 0, "teacher_dim must be positive"
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
