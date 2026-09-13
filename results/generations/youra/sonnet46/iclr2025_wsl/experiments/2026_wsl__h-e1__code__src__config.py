"""Configuration dataclasses for h-e1 experiment."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class DataConfig:
    dataset_url: str = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
    local_path: str = "data/unterthiner_mnist_zoo.pkl"
    min_samples: int = 500
    train_ratio: float = 0.8
    batch_size: int = 64
    seed: int = 42
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])


@dataclass
class NFTModelConfig:
    d_model: int = 128
    n_heads: int = 4
    n_layers: int = 2
    dropout: float = 0.0  # PoC: minimal regularization


@dataclass
class FlatMLPConfig:
    hidden_dim: int = 512
    n_hidden_layers: int = 3
    activation: str = "ReLU"


@dataclass
class TrainConfig:
    optimizer: str = "Adam"
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    seed: int = 42
    nan_recovery_lr: float = 1e-4  # Non-standard: fallback lr on NaN detection, retry once


@dataclass
class EvalConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.05
    holm_correction: bool = True
    flat_mlp_delta_threshold: float = 0.10
    nft_delta_threshold: float = 0.02
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])


@dataclass
class PathsConfig:
    figures_dir: str = "figures"
    checkpoints_dir: str = "checkpoints"
    results_dir: str = "results"


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    nft_model: NFTModelConfig = field(default_factory=NFTModelConfig)
    flat_mlp: FlatMLPConfig = field(default_factory=FlatMLPConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    device: str = "cuda"
    seed: int = 42
