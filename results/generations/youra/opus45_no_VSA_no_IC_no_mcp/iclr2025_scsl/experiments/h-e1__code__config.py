from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    batch_size: int = 128
    lr: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_size: int = 20
    gamma: float = 0.1
    epochs: int = 50
    attribution_subset_size: int = 500
    data_root: str = "./data/waterbirds_v1.0"
    output_dir: str = "./results"
