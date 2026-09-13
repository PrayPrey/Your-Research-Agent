from dataclasses import dataclass, field
from typing import List, Optional
import yaml
import os


@dataclass
class DataConfig:
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    celeba_root: str = ".data_cache/datasets/celeba"
    patch_size: int = 64
    batch_size: int = 256
    num_workers: int = 4
    celeba_samples_per_group: int = 5000
    use_segmentation_masks: bool = True


@dataclass
class MetricConfig:
    n_samples_list: List[int] = field(default_factory=lambda: [50, 100, 200, 500, 1000, 2000])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    alpha: float = 0.05
    min_patches_per_class: int = 100
    logistic_c: float = 1.0
    logistic_max_iter: int = 1000


@dataclass
class FigureConfig:
    figures_dir: str = "./figures"
    dpi: int = 150
    format: str = "png"
    n_fft_examples: int = 4
    pca_method: str = "pca"
    colormap: str = "viridis"
    figsize_default: tuple = (10, 6)

    def __post_init__(self):
        validate_figure_config(self)


def validate_figure_config(cfg: "FigureConfig") -> None:
    if not (72 <= cfg.dpi <= 300):
        raise ValueError(f"dpi must be in [72, 300], got {cfg.dpi}")
    if cfg.format not in ("png", "pdf", "svg"):
        raise ValueError(f"format must be png/pdf/svg, got {cfg.format}")
    if cfg.pca_method not in ("pca", "tsne"):
        raise ValueError(f"pca_method must be pca/tsne, got {cfg.pca_method}")
    os.makedirs(cfg.figures_dir, exist_ok=True)


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    metric: MetricConfig = field(default_factory=MetricConfig)
    figure: FigureConfig = field(default_factory=FigureConfig)
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    device: str = "cuda:0"

    def __post_init__(self):
        validate_config(self)


def validate_config(cfg: ExperimentConfig) -> None:
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    validate_figure_config(cfg.figure)


def load_config(config_path: str) -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    data_cfg = DataConfig(**raw.get("data", {}))
    metric_cfg = MetricConfig(**raw.get("metric", {}))
    fig_cfg = FigureConfig(figures_dir=raw.get("figures_dir", "./figures"))

    cfg = ExperimentConfig(
        data=data_cfg,
        metric=metric_cfg,
        figure=fig_cfg,
        results_dir=raw.get("results_dir", "./results"),
        figures_dir=raw.get("figures_dir", "./figures"),
        device=raw.get("device", "cuda:0"),
    )
    return cfg
