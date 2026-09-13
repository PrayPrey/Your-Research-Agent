from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.8
    max_tokens: int = 1024

    seeds: list = field(default_factory=lambda: [42, 123, 456])
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])

    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])

    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")

    gate_pass: float = 0.10
    gate_borderline: float = 0.05

    @classmethod
    def from_yaml(cls, path: str = "docs/youra_research/h-e1/config.yaml") -> "ExperimentConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        data["results_dir"] = Path(data["results_dir"])
        data["figures_dir"] = Path(data["figures_dir"])
        return cls(**data)
