from dataclasses import dataclass


@dataclass
class Config:
    seeds: tuple = (42, 123, 456)
    data_root: str = "../data/waterbirds_v1.0"
    image_size: int = 224
    batch_size: int = 128
    num_workers: int = 4
    num_classes: int = 2
    pretrained_weights: str = "IMAGENET1K_V1"
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_sizes: tuple = (60, 120)
    gamma: float = 0.1
    epochs: int = 50
    early_epoch_range: tuple = (1, 10)
    ratio_threshold: float = 1.5
    output_dir: str = "../results"
    figures_dir: str = "../figures"
