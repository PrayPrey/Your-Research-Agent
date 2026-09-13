"""Configuration for spatial gradient regularization experiments."""

from dataclasses import dataclass


@dataclass
class MNISTConfig:
    """Configuration for MNIST+Color experiments."""

    lr: float = 0.01
    batch_size: int = 128
    epochs: int = 50
    lambda_init: float = 0.01
    percentile_threshold: int = 75
    momentum: float = 0.9
    weight_decay: float = 1e-4
    patience: int = 10
    num_workers: int = 4
    seed: int = 0
    correlation: float = 0.9
    device: str = "cuda"


@dataclass
class WaterbirdsConfig:
    """Configuration for Waterbirds experiments."""

    lr: float = 0.001
    batch_size: int = 128
    epochs: int = 300
    lambda_init: float = 0.01
    percentile_threshold: int = 75
    momentum: float = 0.9
    weight_decay: float = 1e-4
    patience: int = 20
    num_workers: int = 4
    seed: int = 0
    device: str = "cuda"
    data_root: str = "./datasets/waterbirds"
    pretrained: bool = True
