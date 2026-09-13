"""
Configuration for H-M1 Conditional Margin Inflation Analysis.
Statistical reanalysis of H-E1 data - no model inference required.
"""

from pathlib import Path

# Reproducibility
SEED: int = 42

# Statistical test parameters
PERMUTATION_N: int = 9999   # n_resamples for scipy.stats.permutation_test
BOOTSTRAP_N: int = 1000     # bootstrap CI iterations
N_KL_BINS: int = 100        # bins for KL divergence computation

# Model families to analyze (llama excluded - gated in H-E1)
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05

# H-E1 path resolution (resolved at import time)
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CODE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "code"
H_E1_CACHE_DIR: Path = H_E1_CODE_DIR.parent / "cache"
H_E1_RESULTS_JSON: Path = H_E1_CODE_DIR.parent / "experiment_results.json"

# H-M1 output paths
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
OUTPUTS_DIR: Path = CODE_DIR / "outputs"


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
