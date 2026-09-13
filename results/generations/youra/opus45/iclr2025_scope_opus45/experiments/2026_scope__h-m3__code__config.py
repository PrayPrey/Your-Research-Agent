"""Configuration for H-M3: Eigenmode Energy Redistribution via Projection-Only LoRA.

This experiment validates that projection-only LoRA can redistribute state energy
toward slow eigenmodes (ΔE > 0.1 nats), effectively utilizing latent memory capacity
without changing eigenvalues.

SHOULD_WORK Gate: ΔE > 0.1 nats (energy shift toward slow eigenmodes)
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-M3 eigenmode energy redistribution experiment."""

    # Model (same as H-M1, H-M2)
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_train_sequences: int = 500  # Increased from H-M2 for energy stability
    num_eval_sequences: int = 1000  # For energy measurement
    max_seq_length: int = 256  # Matches H_spec
    seed: int = 42

    # H_spec (validated from H-M2)
    h_spec_known: float = 256.43

    # LoRA Parameters (identical to H-M2)
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["in_proj", "x_proj"]  # Projections only
    )
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    # Training Parameters (identical to H-M2)
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 10
    lr_scheduler_type: str = "cosine"

    # Energy Analysis (H-M3 specific)
    slow_mode_threshold: float = 0.99  # |λ| > 0.99 defines "slow" eigenmode
    delta_e_gate_threshold: float = 0.1  # ΔE must exceed 0.1 nats to pass gate
    num_energy_probe_sequences: int = 50  # Sequences for pre/post energy measurement
    num_layers: int = 48  # Mamba-1.4B layer count

    # Hardware
    device: str = "cuda"
    dtype: str = "float16"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"

    # Visualization settings
    fig_dpi: int = 150
    fig_format: str = "png"
    energy_hist_bins: int = 32
