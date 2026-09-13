"""Configuration for H-M1 experiment."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DataConfig:
    resid_csv: str = "../../h-e1/outputs/residualized_matrix.csv"
    results_json: str = "../../h-e1/outputs/h_e1_results.json"
    paws_name: str = "google-research-datasets/paws"
    paws_config: str = "labeled_final"
    paws_split: str = "test"
    qqp_name: str = "nyu-mll/glue"
    qqp_config: str = "qqp"
    qqp_split: str = "validation"


@dataclass
class InferenceConfig:
    batch_size: int = 32
    max_seq_length: int = 256
    seed: int = 42


@dataclass
class StatisticsConfig:
    alpha: float = 0.05
    min_samples: int = 30


@dataclass
class OutputConfig:
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    statistics: StatisticsConfig = field(default_factory=StatisticsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def ensure_dirs(self):
        Path(self.output.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output.figures_dir).mkdir(parents=True, exist_ok=True)
