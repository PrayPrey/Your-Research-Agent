"""H-E1 Experiment Configuration (EXISTENCE PoC)"""
from dataclasses import dataclass
from typing import Tuple
import os


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    output_dir: str = "results/"
    figures_dir: str = "figures/"
    results_file: str = "results.json"


@dataclass
class DataConfig:
    dataset_name: str = "pwc-archive/evaluation-tables"
    date_start: str = "2018-01-01"
    date_end: str = "2024-12-31"
    aggregation: str = "monthly"


@dataclass
class PELTConfig:
    model: str = "rbf"
    min_size: int = 3
    penalty: float = None  # computed at runtime: log(n) * variance(signal)


@dataclass
class EvaluationConfig:
    alpha: float = 0.05
    target_window: Tuple[int, int] = (2019, 2022)


EXPERIMENT = ExperimentConfig()
DATA = DataConfig()
PELT = PELTConfig()
EVAL = EvaluationConfig()


def setup_dirs():
    os.makedirs(EXPERIMENT.output_dir, exist_ok=True)
    os.makedirs(EXPERIMENT.figures_dir, exist_ok=True)


if __name__ == "__main__":
    setup_dirs()
    print(f"Config loaded: {EXPERIMENT.hypothesis_id}")
