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
    max_new_tokens: int = 512
    n_samples: int = 20
    top_p: float = 0.95
    do_sample: bool = True


@dataclass
class BootstrapConfig:
    n_bootstrap: int = 10000
    alpha: float = 0.05


@dataclass
class ThresholdConfig:
    delta_ast_min: float = 0.0
    ci_lower_min: float = 0.0
    constraint_active_rate_min: float = 0.3


@dataclass
class FMDConfig:
    mypy_timeout: int = 30
    evalplus_timeout: int = 10
    category_priority: List[str] = field(
        default_factory=lambda: ["syntax", "type", "functional", "success"]
    )
    mypy_flags: List[str] = field(
        default_factory=lambda: ["--ignore-missing-imports"]
    )
    cleanup_temp_files: bool = True


@dataclass
class OutputConfig:
    data_dir: str = "h-m1/data/"
    results_dir: str = "h-m1/results/"
    figures_dir: str = "h-m1/figures/"
    baseline_pool_file: str = "baseline_pool.jsonl"
    syncode_pool_file: str = "syncode_pool.jsonl"
    progress_file: str = "progress.json"
    h_e1_baseline_pool: str = "h-e1/data/baseline_pool.jsonl"
    ast_failure_rates_file: str = "ast_failure_rates.json"
    bootstrap_ci_file: str = "bootstrap_ci.json"
    fmd_results_file: str = "fmd_results.json"
    transitions_file: str = "F_SynCode_success_transitions.json"
    mechanism_verification_file: str = "mechanism_verification.json"
    metrics_file: str = "metrics.json"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m1"
    n_problems: int = 164
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    fmd: FMDConfig = field(default_factory=FMDConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
