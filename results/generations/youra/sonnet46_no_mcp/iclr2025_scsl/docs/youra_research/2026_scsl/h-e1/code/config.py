from dataclasses import dataclass, field
from typing import List, Optional
import yaml
import os


@dataclass
class TrainConfig:
    dataset: str                    # "waterbirds" | "celeba"
    data_root: str
    checkpoint_dir: str
    epochs: int                     # 300 (waterbirds) | 50 (celeba)
    checkpoint_interval: int = 2
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    num_workers: int = 4


@dataclass
class ProbeConfig:
    C: float = 1.0
    max_iter: int = 1000
    solver: str = "lbfgs"
    random_state: int = 42


@dataclass
class GateConfig:
    min_window_fraction: float = 0.10
    p_threshold: float = 0.05
    min_seeds: int = 3
    t_star_delta_threshold: float = 0.02
    t_star_consecutive: int = 3


@dataclass
class DatasetPathConfig:
    waterbirds_root: str = "./data/waterbirds"
    celeba_root: str = "./data"
    waterbirds_metadata_csv: str = "metadata.csv"
    waterbirds_spurious_col: str = "place"
    waterbirds_core_col: str = "y"
    celeba_spurious_attr: str = "Blond_Hair"
    celeba_core_attr: str = "Male"
    waterbirds_splits: Optional[dict] = None
    celeba_splits: Optional[dict] = None

    def __post_init__(self):
        if self.waterbirds_splits is None:
            self.waterbirds_splits = {"train": "train", "val": "val", "test": "test"}
        if self.celeba_splits is None:
            self.celeba_splits = {"train": "train", "val": "valid", "test": "test"}


@dataclass
class ExperimentConfig:
    train: TrainConfig
    probe: ProbeConfig
    gate: GateConfig
    paths: DatasetPathConfig
    results_dir: str = "./results/h-e1"


def load_config(config_path: str) -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    train_cfg = TrainConfig(**raw["train"])
    probe_cfg = ProbeConfig(**raw.get("probe", {}))
    gate_cfg = GateConfig(**raw.get("gate", {}))
    paths_raw = raw.get("paths", {})
    paths_cfg = DatasetPathConfig(**paths_raw)

    return ExperimentConfig(
        train=train_cfg,
        probe=probe_cfg,
        gate=gate_cfg,
        paths=paths_cfg,
        results_dir=raw.get("results_dir", "./results/h-e1"),
    )
