"""Configuration for H-E1 FGO experiment."""

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class Config:
    """Fixed hyperparameters per PRD FR-4."""

    # Model
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    torch_dtype: str = "float16"

    # Optimizer (PRD FR-4.2)
    lr: float = 3e-6
    weight_decay: float = 0.01

    # Batch (PRD FR-4.3)
    batch_size: int = 64
    per_device_batch: int = 16
    grad_accum: int = 4

    # Training (PRD FR-4.4)
    episodes: int = 10_000
    checkpoint_every: int = 1000

    # PPO
    clip_eps: float = 0.2
    warmup_ratio: float = 0.1

    # Reward (StepCoder, PRD FR-4.5)
    reward_pass: float = 1.0
    reward_test_fail: float = -0.3
    reward_runtime_error: float = -0.6
    reward_compile_error: float = -1.0

    # Eval
    pass_at_k: Tuple[int, ...] = (1, 10)
    eval_n_samples: int = 10

    # Repro
    seed: int = 1

    # Paths
    checkpoint_dir: str = "checkpoints"
    log_dir: str = "logs"
    figure_dir: str = "figures"
    results_dir: str = "outputs"


# 2x3 factorial conditions (PRD FR-7)
CONDITIONS = [
    ("standard_compile", False, "compile"),
    ("standard_test", False, "test"),
    ("standard_combined", False, "combined"),
    ("fgo_compile", True, "compile"),
    ("fgo_test", True, "test"),
    ("fgo_combined", True, "combined"),
]
