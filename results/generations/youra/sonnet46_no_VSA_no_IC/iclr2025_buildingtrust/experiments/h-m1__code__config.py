"""H-M1 configuration: gate thresholds, paths, Winogrande scores."""
from pathlib import Path

# Gate thresholds
GATE_RHO: float = 0.4
GATE_P: float = 0.05
N_COMMON_MIN: int = 10

# Analysis parameters
RANDOM_SEED: int = 1
ALTERNATIVE: str = "greater"  # one-tailed H1: rho > 0

# Winogrande scores (Open LLM Leaderboard)
WINOGRANDE_SCORES: dict = {
    "LLaMA-2-7B": 0.674,
    "LLaMA-2-13B": 0.720,
    "LLaMA-2-70B": 0.783,
    "LLaMA-2-7B-Chat": 0.643,
    "LLaMA-2-13B-Chat": 0.699,
    "LLaMA-2-70B-Chat": 0.780,
    "Mistral-7B": 0.782,
    "Mistral-7B-Instruct": 0.747,
    "Falcon-7B": 0.662,
    "Falcon-40B": 0.823,
    "GPT-3.5-Turbo": 0.876,
    "GPT-4": 0.870,
    "Vicuna-13B": 0.702,
    "Alpaca-13B": 0.619,
}

_HERE = Path(__file__).parent.parent
DATA_DIR = _HERE / "data"
FIGURES_DIR = _HERE / "figures"
RESULTS_DIR = _HERE / "results"
