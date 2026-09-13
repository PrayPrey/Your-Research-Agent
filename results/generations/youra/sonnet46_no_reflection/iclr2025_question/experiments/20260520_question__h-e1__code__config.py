from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class SamplingConfig:
    n_samples: int = 10
    temperature: float = 1.0
    top_p: float = 0.9
    seed: int = 42
    max_new_tokens: int = 50
    n_few_shot: int = 5


@dataclass
class ModelConfig:
    hf_id: str = ""
    dtype: str = "bfloat16"
    quantization: Optional[str] = None
    device_map: str = "auto"


@dataclass
class DatasetConfig:
    name: str = ""
    hf_id: str = ""
    config: str = "default"
    split: str = "validation"
    size: int = 0


@dataclass
class EvaluationConfig:
    bootstrap_resamples: int = 1000
    alpha: float = 0.05
    batch_size_8b: int = 16
    batch_size_70b: int = 4
    checkpoint_every: int = 500


@dataclass
class OutputConfig:
    base_dir: str = "h-e1"
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
    code_dir: str = "h-e1/code"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    hypothesis_type: str = "EXISTENCE"
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    datasets_primary: List[DatasetConfig] = field(default_factory=list)
    datasets_secondary: List[DatasetConfig] = field(default_factory=list)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def load_config(path: str) -> ExperimentConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    sampling = SamplingConfig(**raw["sampling"])

    models = {}
    for key, val in raw["models"].items():
        if key == "entailment":
            models[key] = ModelConfig(hf_id=val["hf_id"])
        else:
            models[key] = ModelConfig(**{k: v for k, v in val.items()})

    datasets_primary = [DatasetConfig(**d) for d in raw["datasets"]["primary"]]
    datasets_secondary = [DatasetConfig(**d) for d in raw["datasets"].get("secondary", [])]

    evaluation = EvaluationConfig(**raw["evaluation"])
    output = OutputConfig(**raw["output"])

    return ExperimentConfig(
        hypothesis_id=raw["hypothesis_id"],
        hypothesis_type=raw["hypothesis_type"],
        sampling=sampling,
        models=models,
        datasets_primary=datasets_primary,
        datasets_secondary=datasets_secondary,
        evaluation=evaluation,
        output=output,
    )
