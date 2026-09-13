"""Configuration for H-M2: Projection-Only LoRA Eigenvalue Preservation.

This experiment validates that projection-only LoRA preserves SSM eigenvalues
(|ΔH_spec| < 10%) after fine-tuning on WikiText-103.

MUST_WORK Gate: |ΔH_spec| < 10% (eigenvalues must be preserved)
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-M2 projection-only LoRA eigenvalue preservation."""

    # Model (same as H-M1)
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_eval_sequences: int = 100  # Minimal for PoC
    max_seq_length: int = 256  # Reduced for speed
    seed: int = 42

    # H_spec (validated from H-E1 and H-M1)
    h_spec_known: float = 256.18

    # LoRA Parameters (from ssm-peft research)
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["in_proj", "x_proj"]  # Projections only, NOT A_log (out_proj incompatible with PEFT Mamba)
    )
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    # Training Parameters (from ssm-peft, MambaPEFT)
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    num_epochs: int = 1  # Reduced for PoC without fast kernels
    batch_size: int = 2  # Reduced for memory
    gradient_accumulation_steps: int = 8  # Effective batch = 16
    warmup_steps: int = 10
    lr_scheduler_type: str = "cosine"

    # Training subset (for PoC speed - use subset of train data)
    num_train_sequences: int = 200  # Minimal for PoC

    # Gate Thresholds (MUST_WORK)
    delta_h_spec_threshold: float = 10.0  # |ΔH_spec| must be < 10%
    eigenvalue_corr_threshold: float = 0.95

    # Hardware
    device: str = "cuda"
    dtype: str = "float16"  # float16 for memory efficiency

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    checkpoint_dir: str = "checkpoints"
