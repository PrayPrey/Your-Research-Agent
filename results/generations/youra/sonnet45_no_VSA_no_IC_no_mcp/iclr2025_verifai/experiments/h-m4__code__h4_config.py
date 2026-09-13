"""Configuration for h-m4 final valid output selection."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    full_size: int = 164


@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"


@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 512
    temperature: float = 0.8


@dataclass
class GreedyConfig:
    num_beams: int = 1
    max_new_tokens: int = 512
    temperature: float = 0.8


@dataclass
class ScoringConfig:
    alpha: float = 0.7
    beta: float = 0.3


@dataclass
class SelectionConfig:
    strategy: Literal["argmax", "validity_first", "random_valid"] = "argmax"


@dataclass
class GateConfig:
    syntax_validity_rate_min: float = 0.60
    beam_better_than_greedy: bool = True
    selection_accuracy_min: float = 0.90


@dataclass
class OutputConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    final_outputs: str = "results/final_outputs.json"
    greedy_baseline: str = "results/greedy_baseline.json"
    error_comparison: str = "results/error_comparison.json"
    selection_quality: str = "results/selection_quality.json"
    strategy_comparison: str = "results/strategy_comparison.json"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    greedy: GreedyConfig = field(default_factory=GreedyConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    selection: SelectionConfig = field(default_factory=SelectionConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
