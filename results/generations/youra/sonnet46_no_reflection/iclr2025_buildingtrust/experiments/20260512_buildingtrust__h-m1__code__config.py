"""config.py — Fixed constants for H-M1 RI→ECE Mechanism Verification pipeline."""
from __future__ import annotations

# ── Inherited from H-E1 ───────────────────────────────────────────────────────
SEED: int = 42
N_BOOTSTRAP: int = 10000
VIF_THRESHOLD: float = 5.0
MIN_MODELS: int = 30
CAP_COLS: list[str] = ["bbh", "arc_challenge", "mmlu_pro", "math_hard", "gpqa", "musr"]

# ── H-M1 gate thresholds ──────────────────────────────────────────────────────
RHO_THRESHOLD: float = 0.4
P_THRESHOLD: float = 0.05
FAMILY_SIGN_THRESHOLD: int = 2

# ── Family analysis ───────────────────────────────────────────────────────────
TARGET_FAMILIES: list[str] = ["LLaMA", "Mistral", "Qwen"]
MIN_FAMILY_SIZE: int = 5

# ── I/O paths (relative to h-m1/code/) ───────────────────────────────────────
H_E1_OUTPUTS_DIR: str = "../h-e1/code/outputs"
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"

# ── Visualizer constants ──────────────────────────────────────────────────────
FIGURE_DPI: int = 300
FIGURE_SIZE_SCATTER: tuple[float, float] = (6.0, 5.0)
FIGURE_SIZE_FAMILY: tuple[float, float] = (12.0, 4.0)
FIGURE_SIZE_BAR: tuple[float, float] = (5.0, 4.5)
FIGURE_SIZE_RELIABILITY: tuple[float, float] = (7.0, 5.5)
SEABORN_THEME: str = "whitegrid"
COLOR_PALETTE: list[str] = ["#4C72B0", "#DD8452", "#55A868"]

FIG1_FILENAME: str = "fig1_ri_ece_scatter.png"
FIG2_FILENAME: str = "fig2_residuals_scatter.png"
FIG3_FILENAME: str = "fig3_family_subplots.png"
FIG4_FILENAME: str = "fig4_reliability_diagram.png"
FIG5_FILENAME: str = "fig5_rho_comparison_bar.png"
FIG6_FILENAME: str = "fig6_gate_summary.png"

# ── Test suite constants ──────────────────────────────────────────────────────
TEST_N_MODELS: int = 30
TEST_SEED: int = 42
TEST_MODEL_FAMILIES: list[str] = ["LLaMA"] * 12 + ["Mistral"] * 10 + ["Qwen"] * 8
TEST_COVERAGE_MIN: float = 0.80
