"""Configuration for H-M3 dose-response analysis."""
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class SweepConfig:
    thresholds: Tuple[int, ...] = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90)
    n_seeds: int = 3
    benchmark_tasks: Tuple[str, ...] = ("hellaswag", "arc_easy", "piqa", "winogrande")

@dataclass
class ModelSelectionConfig:
    polynomial_degrees: Tuple[int, ...] = (1, 2, 3)
    model_selection_criterion: str = "bic"

@dataclass
class BootstrapConfig:
    n_bootstrap: int = 1000
    ci_level: float = 0.95
    seed: int = 42

@dataclass
class SuccessCriteria:
    min_threshold: int = 20
    max_threshold: int = 80
    max_ci_width: float = 30.0

@dataclass
class PathConfig:
    sweep_data_path: str = "data/sweep_results.json"
    output_dir: str = "output/"
    figures_dir: str = "figures/"

@dataclass
class DoseResponseConfig:
    sweep: SweepConfig = field(default_factory=SweepConfig)
    model_selection: ModelSelectionConfig = field(default_factory=ModelSelectionConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    success: SuccessCriteria = field(default_factory=SuccessCriteria)
    paths: PathConfig = field(default_factory=PathConfig)
