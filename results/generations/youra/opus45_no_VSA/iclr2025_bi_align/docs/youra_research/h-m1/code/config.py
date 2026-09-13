"""H-M1: Configuration for Adversarial BAI Probing."""
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ModelConfig:
    name: str
    dtype: str = "bfloat16"
    device: str = "cuda"


@dataclass
class OptimizerConfig:
    type: str = "adamw"
    lr: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 100


@dataclass
class TrainingConfig:
    batch_size: int = 32
    epochs: int = 3
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    grl_alpha_schedule: str = "dann_sigmoid"
    loss_lambda: float = 1.0
    checkpoint_every_epoch: bool = True


@dataclass
class DatasetConfig:
    hh_rlhf_subsets: list = field(default_factory=lambda: [
        "helpful-base", "helpful-online", "helpful-rejection-sampled", "harmless-base"
    ])
    val_dataset: str = "allenai/reward-bench"
    bai_label_source: str = "h-e1_agency_proxies"
    bai_binarize: str = "median_split"
    max_samples: int = 2000


@dataclass
class PathConfig:
    activation_cache_dir: str = "./cache/activations"
    checkpoint_dir: str = "./checkpoints"
    output_dir: str = "./outputs"


@dataclass
class ExperimentConfig:
    model: ModelConfig
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    paths: PathConfig = field(default_factory=PathConfig)


def load_config(path: str) -> ExperimentConfig:
    with open(path) as f:
        d = yaml.safe_load(f)
    return ExperimentConfig(
        model=ModelConfig(**d.get("model", {})),
        optimizer=OptimizerConfig(**d.get("optimizer", {})),
        training=TrainingConfig(**d.get("training", {})),
        dataset=DatasetConfig(**d.get("dataset", {})),
        paths=PathConfig(**d.get("paths", {})),
    )


MODELS = [
    "meta-llama/Meta-Llama-3-8B",
    "mistralai/Mistral-7B-v0.1",
    "Qwen/Qwen2-7B",
]

HIDDEN_DIMS = {
    "meta-llama/Meta-Llama-3-8B": 4096,
    "mistralai/Mistral-7B-v0.1": 4096,
    "Qwen/Qwen2-7B": 3584,
}
