"""H-Z1 experiment configuration."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Z1Config:
    model: str = "gpt-4o-mini"
    gen_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: ["--ignore-missing-imports", "--no-strict-optional"])
    k_repair_rounds: int = 5
    z3_timeout: int = 10
    min_valid_z3_specs: int = 30
    results_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-z1/results"))
    figures_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-z1/figures"))
    h_e1_code_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-e1/code"))
