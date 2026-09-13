"""Configuration for H-M2 MECHANISM experiment."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    data_root: str = "/home/PrayPrey/YouRA_no_IC_opus45/TEST_scsl/docs/youra_research/h-e1/code/data/waterbirds"
    img_size: int = 224
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)
    batch_size: int = 128
    num_workers: int = 4
    num_classes: int = 2
    pretrained: bool = True
    device: str = "cuda"
    n_epochs: int = 100
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    feature_dim: int = 512
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    probe_solver: str = "lbfgs"
    peak_window: int = 5
    auc_range: tuple = (1, 20)
    ckpt_dir: str = "./checkpoints"
    cache_dir: str = "./feature_cache"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    metrics_path: str = "./outputs/metrics.json"
