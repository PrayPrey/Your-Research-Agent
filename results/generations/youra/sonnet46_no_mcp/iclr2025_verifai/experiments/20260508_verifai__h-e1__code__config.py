from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    device_map: str = "auto"
    torch_dtype: str = "float16"


@dataclass
class GenerationConfig:
    temperature: float = 0.8
    max_new_tokens: int = 256
    n_samples: int = 20
    seeds: List[int] = field(default_factory=lambda: list(range(20)))


@dataclass
class SynCodeConfig:
    grammar: str = "python"
    mode: str = "grammar_mask"


@dataclass
class Z3Config:
    timeout_ms: int = 2000
    theory: str = "LIA"


@dataclass
class MypyConfig:
    flags: List[str] = field(default_factory=lambda: ["--ignore-missing-imports"])
    sample_size: int = 50


@dataclass
class ThresholdConfig:
    delta_ast_min: float = 0.0
    z3_eligibility_min: float = 0.15
    mypy_structured_rate_min: float = 0.90


@dataclass
class OutputConfig:
    data_dir: str = "h-e1/data/"
    results_dir: str = "h-e1/results/"
    figures_dir: str = "h-e1/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    z3_eligibility_file: str = "z3_eligibility.json"
    mypy_results_file: str = "mypy_results.json"
    metrics_file: str = "metrics.json"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    seed: int = 1
    output_dir: str = "h-e1/"
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    syncode: SynCodeConfig = field(default_factory=SynCodeConfig)
    z3: Z3Config = field(default_factory=Z3Config)
    mypy: MypyConfig = field(default_factory=MypyConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    humaneval_size: int = 164
    mbpp_size: int = 374
