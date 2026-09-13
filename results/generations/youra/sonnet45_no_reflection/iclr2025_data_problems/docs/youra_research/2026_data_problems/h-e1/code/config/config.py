"""Configuration for H-E1 Contamination Detection Experiment"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainingConfig:
    """Training configuration"""
    model_name: str = "meta-llama/Llama-2-7b-hf"
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 1e-4
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 8
    max_length: int = 512
    num_runs: int = 20
    seed_base: int = 42
    device: str = "cuda"

@dataclass
class ContaminationConfig:
    """Contamination injection configuration"""
    rates: list = None
    paraphrase_method: str = "simple"  # "simple" or "gpt4"

    def __post_init__(self):
        if self.rates is None:
            self.rates = [0.0, 0.01, 0.05]  # 0%, 1%, 5%

@dataclass
class Tier1Config:
    """Tier 1 Detection Configuration"""
    temporal_cutoff: str = "2021-11-01"  # GSM8K release date
    lsh_num_perm: int = 128
    lsh_bands: int = 20
    lsh_rows: int = 5

@dataclass
class Tier2Config:
    """Tier 2 TSG Probes Configuration"""
    num_invariant_probes: int = 1000
    num_neighbor_probes: int = 1000
    num_broken_probes: int = 1000
    detection_threshold: float = 2.0  # 2σ threshold

@dataclass
class Tier3Config:
    """Tier 3 Geometric Detection Configuration"""
    gradient_overlap_threshold: float = 0.7
    hessian_concentration_threshold: float = 0.8
    cka_alignment_threshold: float = 0.6
    efficiency_zscore_threshold: float = 2.0
    min_metrics_required: int = 2  # ≥2 of 4 metrics

@dataclass
class EvaluationConfig:
    """Evaluation configuration"""
    target_detection_power: float = 0.80  # 80%
    max_false_positive_rate: float = 0.05  # 5%
    min_runs_for_stats: int = 20
