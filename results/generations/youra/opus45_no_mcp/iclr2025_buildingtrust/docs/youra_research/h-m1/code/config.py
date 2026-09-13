"""Config: H-M1 CoT Reasoning Chain Detection"""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class APIConfig:
    model: str = "gpt-3.5-turbo"
    fallback_model: str = "meta-llama/Llama-2-70b-chat-hf"
    temperature: float = 0.0
    max_tokens: int = 1024
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    request_timeout: float = 60.0


@dataclass
class DatasetConfig:
    name: str = "truthful_qa"
    subset: str = "multiple_choice"
    split: str = "validation"
    num_examples: int = 817


@dataclass
class DetectionConfig:
    numbered_step_pattern: str = r"(?:^|\n)\s*(?:\d+[\.\)]|Step\s+\d+:)"
    ordinal_pattern: str = r"\b(First|Second|Third|Fourth|Fifth|Finally|Lastly|Next|Then)\b"
    logical_connector_pattern: str = r"\b(therefore|thus|hence|because|so|consequently)\b"
    answer_pattern: str = r"(?:answer|Answer)[:\s]+\(?([A-E])\)?"
    confidence_pattern: str = r"(?:confidence|Confidence)[:\s]+(\d*\.?\d+)%?"
    case_insensitive: bool = True


@dataclass
class GateConfig:
    min_reasoning_presence_rate: float = 0.90
    min_mean_step_count: float = 2.0
    min_rate_difference: float = 0.50


@dataclass
class PathConfig:
    results_dir: str = "results"
    cache_path: str = ".cache/responses.jsonl"
    figures_dir: str = "../figures"
    results_file: str = "results/h-m1_results.json"
    metrics_file: str = "results/h-m1_metrics.yaml"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M1"
    date: str = str(date.today())
    conditions: list = field(default_factory=lambda: ["baseline", "cot"])
    seed: int = 42
    api: APIConfig = field(default_factory=APIConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathConfig = field(default_factory=PathConfig)


CONFIG = ExperimentConfig()
