from dataclasses import dataclass


@dataclass
class Config:
    data_root: str = "./data/waterbirds"
    img_size: int = 224
    batch_size: int = 128
    imagenet_mean: tuple = (0.485, 0.456, 0.406)
    imagenet_std: tuple = (0.229, 0.224, 0.225)
    minority_groups: tuple = (1, 2)
    majority_groups: tuple = (0, 3)
    num_classes: int = 2
    pretrained: bool = True
    num_power_iter: int = 20
    seeds: tuple = (0,)

    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    epochs: int = 2
    early_stop_patience: int = 10
    variants: tuple = ("baseline", "full_parity")
    partial_scale: float = 0.5
    full_scale: float = 1.0
    sr_eval_epoch: int = 1
    num_groups: int = 4
    results_path: str = "results/summary.json"
    figure_dir: str = "figures/"

    SR_THRESHOLD_PASS: float = 1.1
    SR_THRESHOLD_BASELINE: float = 1.2
    P_VALUE_THRESHOLD: float = 0.05


CONFIG = Config()
