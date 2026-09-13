"""Configuration for h-m1 beam search mechanism validation."""

from dataclasses import dataclass, field
from typing import Literal
import yaml


@dataclass
class DatasetConfig:
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 3


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
class AblationConfig:
    k_values: list[int] = field(default_factory=lambda: [3, 5, 10])
    num_problems: int = 3


@dataclass
class MechanismGateConfig:
    beam_maintenance: float = 1.0
    diversity_ratio_min: float = 0.6


@dataclass
class OutputConfig:
    figures_dir: str = "figures"
    results_file: str = "outputs/ablation_results.json"
    log_file: str = "outputs/mechanism_log.txt"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    ablation: AblationConfig = field(default_factory=AblationConfig)
    gate: MechanismGateConfig = field(default_factory=MechanismGateConfig)
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
            ablation=AblationConfig(**config_dict.get('ablation', {})),
            gate=MechanismGateConfig(**config_dict.get('gate', {})),
            output=OutputConfig(**config_dict.get('output', {})),
            random_seed=config_dict.get('random_seed', 42)
        )
