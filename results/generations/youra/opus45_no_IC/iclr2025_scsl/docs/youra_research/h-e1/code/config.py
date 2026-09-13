"""Configuration for H-E1 EXISTENCE PoC experiment."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    data_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    data_root: str = "./data/waterbirds"
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 64
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    n_epochs: int = 100
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    device: str = "cuda"
    onset_threshold: float = 0.1
    t_early: int = 5
    pr_curve_t_range: tuple = (1, 50)
    loss_traj_sample_n: int = 20
    alpha: float = 0.05
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    metrics_path: str = "./outputs/metrics.json"
