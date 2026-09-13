"""
config.py — Fixed constants for H-E1 Residual Instability pipeline.

All values are EXISTENCE-tier defaults; no tuning is performed.
"""

from __future__ import annotations

# Reproducibility
SEED: int = 42

# Gate thresholds (from hypothesis specification)
SD_THRESHOLD: float = 0.05   # Gate 1: SD(AdvGLUE_drop) must exceed this
R2_THRESHOLD: float = 0.80   # Gate 2: R²_residualization must be below this

# PCA quality guard: PC1 must explain at least this fraction of variance
PC1_VAR_THRESHOLD: float = 0.70

# Multicollinearity guard: VIF must be below this value
VIF_THRESHOLD: float = 5.0

# Bootstrap confidence intervals
N_BOOTSTRAP: int = 10000

# Dataset size requirements
MIN_MODELS: int = 30    # Minimum number of LLMs required
MIN_FAMILIES: int = 3   # Minimum distinct model families required

# Capability columns fed into PCA (Open LLM Leaderboard v2 tasks)
# bbh=Big-Bench Hard, arc=ARC-Challenge, mmlu_pro=MMLU-Pro,
# math=MATH-Hard, gpqa=GPQA, musr=MuSR
CAP_COLS: list[str] = ["bbh", "arc_challenge", "mmlu_pro", "math_hard", "gpqa", "musr"]

# Output directories (relative to h-e1/code/)
RESULTS_DIR: str = "outputs"
FIGURES_DIR: str = "../figures"
