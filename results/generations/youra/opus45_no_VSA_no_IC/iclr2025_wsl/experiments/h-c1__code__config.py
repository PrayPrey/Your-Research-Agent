"""Config for H-C1: 3-way convergence at N=5000 (Statistics vs MLP vs NFN)."""
from dataclasses import dataclass, field
from typing import List

@dataclass
class DataConfig:
    zoo_dir: str = "data/model_zoo"
    n_pool_models: int = 6000
    n_test: int = 500
    split_seed: int = 42

@dataclass
class NFNConfig:
    hidden_dim: int = 128
    num_layers: int = 3

@dataclass
class MLPConfig:
    hidden_dim: int = 256
    num_hidden_layers: int = 2

@dataclass
class StatsConfig:
    pass

@dataclass
class TrainConfig:
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 100
    seeds: List[int] = field(default_factory=lambda: list(range(10)))

N_GATE = 5000
R2_PAIR_DELTA_MAX = 0.03
R2_SANITY_MIN = 0.5

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    mlp: MLPConfig = field(default_factory=MLPConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    figures_dir: str = "figures"
    results_dir: str = "results"

CONFIG = Config()
