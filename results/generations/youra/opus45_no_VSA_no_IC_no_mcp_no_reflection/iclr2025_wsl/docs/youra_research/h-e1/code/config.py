"""H-E1 Experiment Configuration."""
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    n_models_target: int = 100
    n_models_fetch: int = 150
    search_query: str = "vit"
    pipeline_tag: str = "image-classification"
    model_families: tuple = ("google/vit", "facebook/deit", "microsoft/swin")
    attention_name_pattern: str = "attention|qkv|query|key|value"
    sigma_gate_threshold: float = 0.5
    seed: int = 42
    results_path: str = "results.json"
    figures_dir: str = "figures/"
    max_runtime_hours: float = 4.0


CONFIG = ExperimentConfig()
