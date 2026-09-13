from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class TrainConfig:
    data_root: str = ".data_cache/datasets/waterbirds"
    checkpoint_dir: str = "./checkpoints"
    max_epochs: int = 30
    checkpoint_epochs: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3])
    num_workers: int = 4


@dataclass
class DFRConfig:
    C: float = 1.0
    max_iter: int = 1000
    class_weight: str = "balanced"
    solver: str = "lbfgs"
    dfr_seed: int = 42


@dataclass
class AnalysisConfig:
    t_star_mean: float = 2.0
    pearson_r_threshold: float = 0.7
    conditions: List[int] = field(default_factory=lambda: [1, 2, 10, 20, 30])


@dataclass
class PathConfig:
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    checkpoint_dir: str = "./checkpoints"


@dataclass
class ExperimentConfig:
    train: TrainConfig
    dfr: DFRConfig
    analysis: AnalysisConfig
    paths: PathConfig


def load_config(config_path: str = "configs/waterbirds.yaml") -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    train_cfg = TrainConfig(**raw.get("train", {}))
    dfr_cfg = DFRConfig(**raw.get("dfr", {}))
    analysis_cfg = AnalysisConfig(**raw.get("analysis", {}))
    paths_cfg = PathConfig(**raw.get("paths", {}))

    return ExperimentConfig(
        train=train_cfg,
        dfr=dfr_cfg,
        analysis=analysis_cfg,
        paths=paths_cfg,
    )
