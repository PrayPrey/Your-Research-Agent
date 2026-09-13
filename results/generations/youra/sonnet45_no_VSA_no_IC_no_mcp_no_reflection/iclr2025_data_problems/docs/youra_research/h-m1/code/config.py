"""Configuration for H-M1 experiment: Data Curation → Information Density"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DatasetConfig:
    name: str = "allenai/c4"
    split: str = "en"
    subset_size_gb: int = 50
    num_conditions: int = 9
    cache_dir: str = "data/curated/"


@dataclass
class DeduplicationConfig:
    method: str = "minhash_lsh"
    num_perm: int = 128
    jaccard_threshold: float = 0.8


@dataclass
class FilteringConfig:
    model_name: str = "gpt2"
    batch_size: int = 128
    levels: Dict[int, str] = None

    def __post_init__(self):
        if self.levels is None:
            self.levels = {
                0: None,
                1: "median",
                2: "top25"
            }


@dataclass
class DomainMixConfig:
    strategies: Dict[int, str] = None

    def __post_init__(self):
        if self.strategies is None:
            self.strategies = {
                0: "uniform",
                1: "quality_weighted"
            }


@dataclass
class CurationCondition:
    name: str
    dedup_ratio: float
    filter_level: int
    domain_mix: int


@dataclass
class CurationConfig:
    dedup: DeduplicationConfig = None
    filtering: FilteringConfig = None
    domain_mix: DomainMixConfig = None
    conditions: List[CurationCondition] = None

    def __post_init__(self):
        if self.dedup is None:
            self.dedup = DeduplicationConfig()
        if self.filtering is None:
            self.filtering = FilteringConfig()
        if self.domain_mix is None:
            self.domain_mix = DomainMixConfig()
        if self.conditions is None:
            self.conditions = [
                CurationCondition("baseline", 0.0, 0, 0),
                CurationCondition("dedup_low", 0.5, 0, 0),
                CurationCondition("dedup_high", 0.95, 0, 0),
                CurationCondition("filter_med", 0.0, 1, 0),
                CurationCondition("filter_high", 0.0, 2, 0),
                CurationCondition("mix_only", 0.0, 0, 1),
                CurationCondition("dedup_filter", 0.95, 2, 0),
                CurationCondition("dedup_mix", 0.95, 0, 1),
                CurationCondition("full_curation", 0.95, 2, 1)
            ]


@dataclass
class TrainingConfig:
    model_name: str = "gpt2"
    batch_size: int = 256
    micro_batch_size: int = 32
    gradient_accumulation_steps: int = 8
    learning_rate: float = 6e-4
    warmup_steps: int = 2000
    total_steps: int = 50000
    optimizer: str = "adamw"
    adam_beta1: float = 0.9
    adam_beta2: float = 0.95
    adam_eps: float = 1e-8
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    dropout: float = 0.1
    seed: int = 42
    log_interval: int = 100
    checkpoint_interval: int = 5000
    device: str = "cuda"
    output_dir: str = "results/checkpoints/"


@dataclass
class DensityMetricsConfig:
    compute_entropy: bool = True
    compute_fisher: bool = True
    log_interval: int = 100
    vocab_size: int = 50257


@dataclass
class EvaluationConfig:
    entropy_reduction_threshold: float = 0.20
    fisher_increase_threshold: float = 0.15
    monotonicity_required: bool = True
    output_dir: str = "results/"
    plots_dir: str = "results/plots/"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = None
    curation: CurationConfig = None
    training: TrainingConfig = None
    density_metrics: DensityMetricsConfig = None
    evaluation: EvaluationConfig = None

    def __post_init__(self):
        if self.dataset is None:
            self.dataset = DatasetConfig()
        if self.curation is None:
            self.curation = CurationConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.density_metrics is None:
            self.density_metrics = DensityMetricsConfig()
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()


CONFIG = ExperimentConfig()
