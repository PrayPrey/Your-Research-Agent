import os
import yaml
from dataclasses import dataclass, field, fields
from typing import List


@dataclass
class AnalysisConfig:
    threshold: float = 0.02
    n_consecutive: int = 3
    checkpoint_interval: int = 2
    n_bootstrap: int = 10000
    bootstrap_seed: int = 42
    std_gate_threshold: float = 10.0
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    min_checkpoints: int = 15
    min_seeds: int = 3


@dataclass
class PathConfig:
    h_e1_results_dir: str = "../../h-e1/results"
    h_e1_checkpoint_dir: str = "../../h-e1/checkpoints"
    h_e1_json_filename: str = "h-e1_results.json"
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    results_dir: str = "./results"
    figures_dir: str = "./figures"


@dataclass
class ExperimentConfig:
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    hypothesis_id: str = "H-M3"
    device: str = "cpu"


def load_config(config_path: str = "configs/waterbirds.yaml") -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    analysis_dict = raw.get("analysis", {})
    paths_dict = raw.get("paths", {})
    meta = {k: v for k, v in raw.items() if k not in ("analysis", "paths")}

    analysis_field_names = {f.name for f in fields(AnalysisConfig)}
    paths_field_names = {f.name for f in fields(PathConfig)}

    for fld in fields(AnalysisConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            raw_val = os.environ[env_key]
            if fld.name == "seeds":
                analysis_dict[fld.name] = list(map(int, raw_val.split(",")))
            else:
                analysis_dict[fld.name] = type(getattr(AnalysisConfig(), fld.name))(raw_val)

    for fld in fields(PathConfig):
        env_key = f"H_M3_{fld.name.upper()}"
        if env_key in os.environ:
            paths_dict[fld.name] = os.environ[env_key]

    analysis_cfg = AnalysisConfig(**{k: v for k, v in analysis_dict.items() if k in analysis_field_names})
    paths_cfg = PathConfig(**{k: v for k, v in paths_dict.items() if k in paths_field_names})

    exp_field_names = {f.name for f in fields(ExperimentConfig)} - {"analysis", "paths"}
    return ExperimentConfig(
        analysis=analysis_cfg,
        paths=paths_cfg,
        **{k: v for k, v in meta.items() if k in exp_field_names},
    )


def validate_config(cfg: ExperimentConfig) -> None:
    a = cfg.analysis
    p = cfg.paths

    if not (0.0 < a.threshold < 1.0):
        raise ValueError(f"threshold must be in (0, 1), got {a.threshold}")

    if len(set(a.seeds)) != len(a.seeds):
        raise ValueError(f"seeds must be unique, got {a.seeds}")
    if len(a.seeds) < a.min_seeds:
        raise ValueError(f"Need at least {a.min_seeds} seeds, got {len(a.seeds)}")

    if a.n_bootstrap < 1:
        raise ValueError(f"n_bootstrap must be >= 1, got {a.n_bootstrap}")
    if a.n_consecutive < 1:
        raise ValueError(f"n_consecutive must be >= 1, got {a.n_consecutive}")
    if a.min_checkpoints < 1:
        raise ValueError(f"min_checkpoints must be >= 1, got {a.min_checkpoints}")

    if not os.path.isdir(p.h_e1_results_dir):
        raise FileNotFoundError(f"h_e1_results_dir not found: {p.h_e1_results_dir}")
