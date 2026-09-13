"""Configuration for h-m2 combined scoring mechanism."""

from dataclasses import dataclass, field
from typing import Literal
import yaml


@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3
    full_size: int = 164
    ablation_size: int = 20


@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"


@dataclass
class BeamSearchConfig:
    k: int = 3
    max_new_tokens: int = 64
    temperature: float = 0.8


@dataclass
class ScoringConfig:
    alpha_default: float = 0.7
    beta_default: float = 0.3
    weight_pairs: list = field(default_factory=lambda: [
        (0.5, 0.5),
        (0.6, 0.4),
        (0.7, 0.3),
        (0.8, 0.2)
    ])


@dataclass
class GateConfig:
    ast_latency_mean_ms: float = 50.0
    ast_latency_p95_ms: float = 100.0
    ranking_correctness_min: float = 0.8
    syntax_error_rate_max: float = 0.64


@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/h-m2_results.json"
    log_file: str = "outputs/h-m2_log.txt"
    ast_latency_file: str = "results/ast_latency_stats.json"
    beam_ranking_file: str = "results/beam_ranking_logs.csv"
    ablation_file: str = "results/ablation_results.json"
    baseline_file: str = "results/baseline_comparison.json"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)

        return cls(
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            model=ModelConfig(**config_dict.get('model', {})),
            beam_search=BeamSearchConfig(**config_dict.get('beam_search', {})),
            scoring=ScoringConfig(**config_dict.get('scoring', {})),
            gate=GateConfig(**config_dict.get('gate', {})),
            output=OutputConfig(**config_dict.get('output', {})),
            random_seed=config_dict.get('random_seed', 42)
        )
