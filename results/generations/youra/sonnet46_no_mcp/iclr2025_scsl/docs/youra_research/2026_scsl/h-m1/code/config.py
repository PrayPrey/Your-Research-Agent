from dataclasses import dataclass, field
from typing import List, Optional
import yaml
import os


@dataclass
class TrainConfig:
    dataset: str
    data_root: str
    checkpoint_dir: str
    epochs: int
    checkpoint_interval: int = 2
    batch_size: int = 64
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4


@dataclass
class GDRConfig:
    early_window_epochs: List[int] = field(default_factory=lambda: [2, 4, 6])
    p_threshold: float = 0.05
    min_seeds_pass: int = 2
    he1_delta_path: Optional[str] = None


@dataclass
class ExperimentConfig:
    train: TrainConfig
    gdr: GDRConfig
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./figures"


def load_config(config_path: str) -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    train_cfg = TrainConfig(**raw["train"])
    gdr_cfg = GDRConfig(**raw.get("gdr", {}))

    # Validation
    for e in gdr_cfg.early_window_epochs:
        if e % train_cfg.checkpoint_interval != 0:
            raise ValueError(f"early_window_epoch {e} not a multiple of checkpoint_interval {train_cfg.checkpoint_interval}")
    if not (0 < gdr_cfg.p_threshold <= 1.0):
        raise ValueError(f"p_threshold must be in (0, 1], got {gdr_cfg.p_threshold}")
    if not (1 <= gdr_cfg.min_seeds_pass <= len(train_cfg.seeds)):
        raise ValueError(f"min_seeds_pass must be in [1, {len(train_cfg.seeds)}]")
    if gdr_cfg.he1_delta_path is not None and not os.path.exists(gdr_cfg.he1_delta_path):
        raise ValueError(f"he1_delta_path not found: {gdr_cfg.he1_delta_path}")

    return ExperimentConfig(
        train=train_cfg,
        gdr=gdr_cfg,
        results_dir=raw.get("results_dir", "./results/h-m1"),
        figures_dir=raw.get("figures_dir", "./figures"),
    )
