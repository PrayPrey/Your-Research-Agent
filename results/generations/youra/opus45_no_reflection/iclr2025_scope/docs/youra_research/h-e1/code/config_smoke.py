"""H-E1 Smoke Test Configuration - Reduced scale for PoC validation"""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    teacher_name: str = "microsoft/phi-1_5"
    num_layers: int = 24
    hidden_size: int = 2048
    num_heads: int = 32
    d_head: int = 64
    d_state: int = 64
    seq_len: int = 512  # Reduced for smoke test
    vocab_size: int = 51200

    # Data
    dataset_name: str = "allenai/c4"
    dataset_subset: str = "en"
    batch_size: int = 4  # Reduced
    grad_accum: int = 2

    # Optimization
    lr_stage12: float = 1e-4
    lr_stage3: float = 5e-5
    warmup_steps: int = 100
    grad_clip: float = 1.0
    weight_decay: float = 0.0

    # Precision
    mixed_precision: str = "bf16"
    seed: int = 42

    # Token budgets - SMOKE TEST (1M total per objective)
    total_tokens: int = 1_000_000
    mohawk_stage1_tokens: int = 400_000
    mohawk_stage2_tokens: int = 400_000
    mohawk_stage3_tokens: int = 200_000
    cab_stage1_tokens: int = 600_000
    cab_stage2_tokens: int = 400_000

    # Logging
    log_every_steps: int = 100
    figures_dir: str = "figures/"
    output_dir: str = "outputs/"
