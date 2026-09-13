"""H-M2 configuration."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    k_max: int = 5
    benchmark: str = "humaneval+"  # HumanEval+ only (MBPP+ has 0 type-error problems)
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    checkpoint_path: str = "docs/youra_research/h-m2/results/checkpoint.json"
