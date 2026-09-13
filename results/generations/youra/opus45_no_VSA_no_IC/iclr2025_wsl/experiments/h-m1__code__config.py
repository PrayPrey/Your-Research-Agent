"""Config for H-M1 NFN experiment."""
from dataclasses import dataclass, field
from typing import List

@dataclass
class DataConfig:
    zoo_dir: str = "data/model_zoo"
    n_train: int = 2000  # Reduced for faster training
    n_test: int = 500
    split_seed: int = 42

@dataclass
class ModelConfig:
    hidden_dim: int = 64  # Smaller model
    num_layers: int = 2

@dataclass
class TrainConfig:
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 64  # Larger batch
    epochs: int = 30  # Fewer epochs
    early_stop_patience: int = 10
    lr_patience: int = 5
    seeds: List[int] = field(default_factory=lambda: [42])

@dataclass
class EvalConfig:
    equivariance_tol: float = 1e-5
    r2_target: float = 0.85

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    figures_dir: str = "figures"

CONFIG = Config()

ALPHAS = [0.01, 0.1, 1.0, 10.0]
CV_FOLDS = 5
