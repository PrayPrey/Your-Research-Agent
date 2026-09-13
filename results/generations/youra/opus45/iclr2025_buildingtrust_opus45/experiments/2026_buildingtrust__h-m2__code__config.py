"""
Configuration for H-M2 Percentile-Normalized Monotonicity Attenuation Analysis.
Statistical reanalysis of H-E1 data - measures β_percentile slope attenuation.
"""

from pathlib import Path

# Reproducibility
SEED: int = 42

# Bootstrap parameters
BOOTSTRAP_N: int = 1000  # bootstrap iterations for CI and difference test

# Logistic regression parameters
LR_C: float = 1e6        # regularization (very weak, near unregularized)
LR_MAX_ITER: int = 1000  # max iterations for convergence

# Model families to analyze (llama excluded - gated in H-E1)
FAMILIES: list[str] = ["qwen", "mistral"]

# Gate configuration
GATE_TYPE: str = "MUST_WORK"
P_VALUE_THRESHOLD: float = 0.05

# H-E1 path resolution (resolved at import time)
CODE_DIR: Path = Path(__file__).parent
HYPOTHESIS_DIR: Path = CODE_DIR.parent
H_E1_CACHE_DIR: Path = HYPOTHESIS_DIR.parent / "h-e1" / "cache"

# H-M2 output paths
FIGURES_DIR: Path = HYPOTHESIS_DIR / "figures"
RESULTS_YAML: Path = HYPOTHESIS_DIR / "experiment_results.yaml"
VALIDATION_MD: Path = HYPOTHESIS_DIR / "04_validation.md"


def ensure_directories() -> None:
    """Create output directories if they don't exist."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
