"""H-M3 Experiment Configuration - 2x3 Factorial: Objective x Length F1 Retention"""
from dataclasses import dataclass, field
from typing import List, Optional
import os

@dataclass
class ExperimentConfig:
    teacher_name: str = "microsoft/phi-1_5"
    student_base_name: str = "state-spaces/mamba-130m-hf"
    teacher_dim: int = 2048

    train_dataset: str = "allenai/c4"
    train_dataset_config: str = "en"
    tokens_per_condition: int = 10_000_000  # ponytail: 10M for PoC, 1.5B for full
    checkpoint_every_tokens: int = 5_000_000

    lengths: List[int] = field(default_factory=lambda: [1024, 2048, 4096])
    objectives: List[str] = field(default_factory=lambda: ["mohawk", "cab"])

    lr: float = 3e-4
    weight_decay: float = 0.1
    batch_size: int = 1
    grad_accum: int = 16
    dtype: str = "bfloat16"
    seed: int = 42

    longbench_tasks: List[str] = field(default_factory=lambda: [
        "narrativeqa", "qasper", "multifieldqa_en", "hotpotqa",
        "2wikimqa", "musique", "triviaqa"])
    samples_per_task: int = 200

    checkpoint_dir: str = "checkpoints"
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    smoke_mode: bool = True  # PoC mode
    smoke_tokens: int = 5_000
    smoke_eval_samples: int = 10

    def __post_init__(self):
        if self.smoke_mode:
            self.tokens_per_condition = self.smoke_tokens
            self.checkpoint_every_tokens = self.smoke_tokens

ANOVA_FORMULA: str = "f1 ~ C(objective) * C(length)"
SIGNIFICANCE_ALPHA: float = 0.05
GATE_P2_LENGTH: int = 2048
GATE_P2_MIN_DIFF: float = 3.0
GATE_P3_LENGTH: int = 4096
GATE_P3_MIN_DIFF: float = 5.0
CI_CONFIDENCE: float = 0.95

FIGURE_DPI: int = 150
FIGURE_SIZE = (8, 5)
PALETTE = {"mohawk": "#d62728", "cab": "#1f77b4"}
