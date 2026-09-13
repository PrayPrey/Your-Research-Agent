"""Configuration for H-M1: SSM Eigenvalue Memory Horizon Empirical Validation.

This experiment validates that eigenvalue-derived H_spec predicts actual
perplexity degradation on real text (WikiText-103).
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ExperimentConfig:
    """Configuration for H-M1 perplexity degradation measurement."""

    # Model
    model_id: str = "state-spaces/mamba-1.4b"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 1000
    max_seq_length: int = 1024
    seed: int = 42

    # H_spec (validated from H-E1)
    h_spec_known: float = 256.18
    context_length_multipliers: Tuple[float, ...] = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)

    # Gate (MUST_WORK)
    degradation_ratio_threshold: float = 1.1
    baseline_ppl_expected: float = 16.3
    baseline_ppl_tolerance: float = 0.2  # ±20%

    # Hardware
    device: str = "cuda"
    dtype: str = "float32"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
