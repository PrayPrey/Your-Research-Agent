from dataclasses import dataclass, field
from typing import Literal
import yaml

@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 5

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    k: int = 5
    max_new_tokens: int = 256
    temperature: float = 1.0
    do_sample: bool = False

@dataclass
class ScoringConfig:
    alpha: float = 0.7
    beta: float = 0.3

@dataclass
class GateConfig:
    time_target_seconds: int = 1800
    latency_target_ms: int = 50

@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/results.json"
    log_file: str = "outputs/poc_log.txt"

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
    def from_yaml(cls, path: str) -> 'ExperimentConfig':
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
