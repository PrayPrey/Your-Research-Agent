"""H-M3 Config: Attribution Method Comparison"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    epochs: int = 3
    lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    gate_threshold: float = 0.10
    device: str = "cuda"
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"
    mislabel_fraction: float = 0.05
    seed: int = 42
    ekfac_strategies: List[str] = field(default_factory=lambda: ["identity", "diagonal", "kfac", "ekfac"])
    trak_proj_dims: List[int] = field(default_factory=lambda: [1024, 2048, 4096])
    trak_default_proj_dim: int = 2048
    trak_seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    tracin_checkpoint_epochs: List[int] = field(default_factory=lambda: [1, 2, 3])
    mislabeled_indices_path: str = "mislabeled_indices.json"

GATE_CONFIG = {"min_relative_diff": 0.10}

FIGURE_FILES = {
    "gate_comparison": "gate_comparison.png",
    "quality_heatmap": "quality_heatmap.png",
    "score_distributions": "score_distributions.png",
    "rank_correlation": "rank_correlation.png",
}
