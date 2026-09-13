"""H-E1 Experiment Configuration."""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.0
    max_tokens: int = 512
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 10
    jaccard_gate: float = 0.3
    non_overlap_gate: float = 0.7
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"

CONFIG = ExperimentConfig()
