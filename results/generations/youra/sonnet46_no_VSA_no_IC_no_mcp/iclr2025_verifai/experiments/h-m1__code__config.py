"""H-M1 configuration dataclasses."""

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
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"


@dataclass
class VisualizationConfig:
    figures_dir: str = "docs/youra_research/h-m1/figures"
    dpi: int = 150
    figsize_bar: tuple = (10, 6)
    figsize_line: tuple = (10, 6)
    figsize_heatmap: tuple = (14, 8)
    figsize_box: tuple = (12, 6)
    color_mbpp: str = "#2196F3"
    color_humaneval: str = "#FF9800"
    rounds: list = field(default_factory=lambda: [1, 2, 3, 4, 5])
