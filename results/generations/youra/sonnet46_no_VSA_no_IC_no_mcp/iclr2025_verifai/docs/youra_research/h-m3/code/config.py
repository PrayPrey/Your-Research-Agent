"""H-M3 configuration: multi-seed, dual-dataset, execution+mypy vs execution-only."""
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    k_max: int = 5
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    datasets: list = field(default_factory=lambda: ["humaneval+", "mbpp+"])
    conditions: list = field(default_factory=lambda: ["A", "B"])
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
        "--no-error-summary",
    ])
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    results_dir: str = "docs/youra_research/h-m3/results"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    checkpoint_path: str = "docs/youra_research/h-m3/results/checkpoint.json"
    checkpoint_path: str = "docs/youra_research/h-m3/results/checkpoint.json"
