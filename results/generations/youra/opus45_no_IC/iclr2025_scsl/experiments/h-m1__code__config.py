"""Configuration for H-M1 MECHANISM experiment."""
from dataclasses import dataclass
import os

@dataclass
class Config:
    seed: int = 42
    data_root: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "data", "waterbirds")
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 64
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    device: str = "cuda"

    n_epochs: int = 50
    checkpoint_epochs: tuple = (5, 20, 50)
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4

    feature_dim: int = 512
    probe_lr: float = 0.01
    probe_epochs: int = 10

    ckpt_dir: str = "./checkpoints"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    metrics_path: str = "./outputs/metrics.json"
