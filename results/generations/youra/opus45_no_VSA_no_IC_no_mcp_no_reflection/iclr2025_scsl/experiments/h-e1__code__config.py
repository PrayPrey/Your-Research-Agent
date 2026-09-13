"""Configuration for H-E1 experiment."""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    data_root: str = "./data/waterbirds"
    batch_size: int = 128
    num_workers: int = 4
    image_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    num_classes: int = 2
    pretrained: bool = True
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_milestones: tuple = (60, 75)
    gamma: float = 0.1
    num_epochs: int = 90
    accumulation_epochs: int = 10
    subspace_rank: int = 50
    log_epochs: tuple = (5, 10, 45)
    checkpoint_dir: str = "./checkpoints"
    figures_dir: str = "./figures"
    csv_log_path: str = "./logs/alignment.csv"
    spurious_gate: float = 0.70
    core_gate: float = 0.30

CONFIG = ExperimentConfig()
