"""Configuration for h-m3 invalid beam pruning tracking."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    full_size: int = 164


@dataclass
class ModelConfig:
    name: str = "Qwen/CodeQwen1.5-7B"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"


@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 512
    temperature: float = 0.8


@dataclass
class ScoringConfig:
    alpha: float = 0.7
    beta: float = 0.3


@dataclass
class BaselineConfig:
    alpha: float = 1.0
    beta: float = 0.0


@dataclass
class GateConfig:
    reduction_rate_mean: float = 0.50
    final_valid_proportion: float = 0.60
    final_valid_problems_pct: float = 0.70


@dataclass
class OutputConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    beam_validity_logs: str = "results/beam_validity_logs.csv"
    reduction_rates: str = "results/reduction_rates.json"
    final_validity: str = "results/final_validity.json"
    temporal_dynamics: str = "results/temporal_dynamics.json"
    baseline_comparison: str = "results/baseline_comparison.json"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
