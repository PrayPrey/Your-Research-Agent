from __future__ import annotations
import os

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))   # h-m2/code/
_HM2_DIR  = os.path.dirname(_CODE_DIR)                   # h-m2/
_BASE     = os.path.dirname(_HM2_DIR)                    # research folder

# --- Paths ---
SCORE_MATRIX_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix.csv")
RESULTS_DIR: str       = os.path.join(_BASE, "h-m2", "results")
FIGURES_DIR: str       = os.path.join(_BASE, "h-m2", "figures")

# --- Bootstrap (inherited from H-M1) ---
N_BOOTSTRAP: int    = 10_000
BOOTSTRAP_SEED: int = 42

# --- Column definitions ---
REQUIRED_COLS: list[str] = [
    "model_id", "ECE", "Brier", "TruthfulQA_pct",
    "AdvGLUE_drop", "ANLI_drop", "MMLU_acc", "HumanEval_pass1",
]
COMPOSITE_COLS: list[str]  = ["ECE", "TruthfulQA_pct", "Brier"]
BASELINE_COLS: list[str]   = ["MMLU_acc"]
TARGET_COL: str            = "top_quartile_advglue"
PARTIAL_X: str             = "ECE"
PARTIAL_Y_ADV: str         = "AdvGLUE_drop"
PARTIAL_Y_ANLI: str        = "ANLI_drop"
COVARIATE: str             = "MMLU_acc"
MIN_MODELS: int            = 25

# --- Gate thresholds ---
AUC_THRESHOLD: float         = 0.70
DELTA_AUC_THRESHOLD: float   = 0.10
PARTIAL_RHO_THRESHOLD: float = 0.40
ANLI_RHO_THRESHOLD: float    = 0.30

# --- Logistic regression ---
LR_C: float      = 1.0
LR_MAX_ITER: int = 1000
TOP_QUARTILE: float = 0.75

# --- Figures ---
FIGURE_DPI: int    = 150
FIGURE_FORMAT: str = "png"
FIGURE_NAMES: dict = {
    "gate_metrics_comparison":          "fig1_gate_metrics_comparison.png",
    "roc_curves_comparison":            "fig2_roc_curves_comparison.png",
    "partial_correlation_comparison":   "fig3_partial_correlation_comparison.png",
    "advglue_drop_distribution":        "fig4_advglue_drop_distribution.png",
    "feature_importance":               "fig5_feature_importance.png",
    "epistemic_vs_adversarial_scatter": "fig6_epistemic_vs_adversarial_scatter.png",
}

# Figure display constants
SCATTER_ALPHA: float    = 0.75
SCATTER_SIZE: int       = 60
ROC_LINEWIDTH: float    = 2.0
ROC_DIAGONAL_STYLE: str = "--"
BAR_CAPSIZE: int        = 5
BAR_ALPHA: float        = 0.85
COEF_CI_ALPHA: float    = 0.05

# --- Test-only constants ---
TEST_N_MODELS: int    = 10
TEST_BOOTSTRAP_N: int = 100
TEST_SEED: int        = 42
