"""H-E1 Experiment Configuration: Contamination-Correlation Analysis."""
import os
from dataclasses import dataclass, field


def _get_model_sizes():
    """Get model sizes based on TEST_MODE environment variable."""
    if os.environ.get("H_E1_TEST_MODE", "").lower() in ("1", "true"):
        return ["410m", "1b"]  # Minimal for testing
    return ["410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]


def _get_checkpoint_steps():
    """Get checkpoint steps based on TEST_MODE environment variable."""
    if os.environ.get("H_E1_TEST_MODE", "").lower() in ("1", "true"):
        return [1000, 10000, 143000]  # Minimal for testing
    return [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 143000]


@dataclass
class ExperimentConfig:
    model_sizes: list[str] = field(default_factory=_get_model_sizes)
    checkpoint_steps: list[int] = field(default_factory=_get_checkpoint_steps)
    tasks: list[str] = field(default_factory=lambda: [
        "mmlu", "arc_challenge", "hellaswag", "winogrande"
    ])
    wikitext_task: str = "wikitext"
    ngram_n: int = 13
    seed: int = 1
    hf_org: str = "EleutherAI"
    model_name_template: str = "{org}/pythia-{size}"
    gate_r_threshold: float = 0.2
    gate_p_threshold: float = 0.05

@dataclass
class PathsConfig:
    results_dir: str = "results"
    eval_cache_path: str = "results/eval_cache.json"
    contamination_cache_path: str = "results/contamination_cache.json"
    analysis_output_path: str = "results/analysis.json"
    figures_dir: str = "figures"

CONFIG = ExperimentConfig()
PATHS = PathsConfig()

def checkpoint_revision(step: int) -> str:
    return f"step{step}"

def model_id(org: str, size: str) -> str:
    return f"{org}/pythia-{size}"
