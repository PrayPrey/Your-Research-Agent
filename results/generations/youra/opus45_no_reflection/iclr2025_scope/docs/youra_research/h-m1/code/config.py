"""Configuration for H-M1 Attention Entropy Analysis."""
from dataclasses import dataclass, field
from typing import List

@dataclass
class AnalysisConfig:
    model_name: str = "microsoft/phi-1_5"
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    target_lengths: List[int] = field(default_factory=lambda: [256, 512, 1024, 1536, 2048])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])
    num_samples: int = 500
    min_doc_tokens: int = 2048
    top_k: int = 32
    entropy_clamp_min: float = 1e-10
    seed: int = 42
    output_dir: str = "results"
    figures_dir: str = "figures"

GATE_ENTROPY_INCREASE_PCT: float = 0.10
GATE_BASE_LENGTH: int = 256
GATE_TARGET_LENGTH: int = 2048
