"""Configuration for H-C1: Transfer Gate Evaluation."""
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).parent


@dataclass
class ModelsConfig:
    checkpoints: dict[str, str] = field(default_factory=lambda: {
        "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
        "B2": "../h-m2/code/outputs/B2/final",
        "B3": "../h-m2/code/outputs/B3/final",
        "T1": "../h-m2/code/outputs/T1/final",
        "T2": "../h-m2/code/outputs/T2/final",
        "T3": "../h-m2/code/outputs/T3/final",
        "T4": "../h-m2/code/outputs/T4/final",
    })
    baselines: tuple[str, ...] = ("B1", "B2", "B3")
    treatments: tuple[str, ...] = ("T1", "T2", "T3", "T4")


@dataclass
class EvalConfig:
    tasks: tuple[str, ...] = ("truthfulqa_mc1", "truthfulqa_mc2", "bbq")
    batch_size: str = "auto:4"
    seed: int = 42
    num_fewshot: int = 0
    device: str = "cuda:0"
    ifeval_results_path: str = str(BASE_DIR / "../h-m2/code/outputs/eval_results.json")
    results_out_path: str = str(BASE_DIR / "results/safety_results.json")
    correlation_out_path: str = str(BASE_DIR / "results/correlation_analysis.json")


@dataclass
class GateConfig:
    threshold_pp: float = 0.02  # >=2pp gate
    primary_metrics: tuple[str, ...] = ("truthfulqa_mc1", "bbq")


# Default instances
MODELS = ModelsConfig()
EVAL = EvalConfig()
GATE = GateConfig()
