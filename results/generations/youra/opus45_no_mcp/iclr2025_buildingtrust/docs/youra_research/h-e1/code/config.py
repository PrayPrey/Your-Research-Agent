"""Configuration for H-E1 ECE Measurability Validation."""
import os
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    model_name: str = "gpt-3.5-turbo-0125"
    temperature: float = 0.0
    max_tokens: int = 512


@dataclass
class DatasetConfig:
    dataset_name: str = "truthful_qa"
    subset: str = "multiple_choice"
    split: str = "validation"


@dataclass
class ExperimentConfig:
    conditions: list = field(default_factory=lambda: [
        "baseline", "cot_only", "confidence_only", "cot_confidence", "token_padding"
    ])
    n_bins: int = 15
    seed: int = 42
    confidence_regex: str = r"Confidence:\s*(\d+)%"
    answer_regex: str = r"Answer:\s*([A-Z])"
    extraction_rate_threshold: float = 0.95


@dataclass
class APIConfig:
    api_key_env: str = "OPENAI_API_KEY"
    requests_per_minute: int = 500
    max_retries: int = 5
    retry_backoff_base: float = 2.0
    retry_on_status: tuple = (429, 500, 502, 503, 529)
    cache_enabled: bool = True
    cache_path: str = "cache/responses.jsonl"


@dataclass
class OutputConfig:
    results_dir: str = "results"
    results_path: str = "results/results.json"
    figures_dir: str = "../figures"
    reliability_fig_pattern: str = "../figures/reliability_{condition}.png"
    ece_comparison_fig: str = "../figures/ece_comparison.png"
    extraction_rate_fig: str = "../figures/extraction_rate.png"


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    api: APIConfig = field(default_factory=APIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def __post_init__(self):
        self.model.model_name = os.getenv("HE1_MODEL_NAME", self.model.model_name)
        rpm = os.getenv("HE1_RPM")
        if rpm:
            self.api.requests_per_minute = int(rpm)


CONFIG = Config()
