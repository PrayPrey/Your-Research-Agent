from __future__ import annotations
import os

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))  # h-m1/code/
_HM1_DIR = os.path.dirname(_CODE_DIR)                   # h-m1/
_BASE = os.path.dirname(_HM1_DIR)                       # research folder (contains h-e1/ and h-m1/)

SCORE_MATRIX_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix.csv")
SCORE_MATRIX_T07_PATH: str = os.path.join(_BASE, "h-e1", "results", "score_matrix_t07.csv")
RESULTS_DIR: str = os.path.join(_BASE, "h-m1", "results")
FIGURES_DIR: str = os.path.join(_BASE, "h-m1", "figures")

N_BOOTSTRAP: int = 10_000
BOOTSTRAP_SEED: int = 42

PRIMARY_X: str = "ECE"
PRIMARY_Y: str = "TruthfulQA_pct"
DISCRIMINANT_Y: str = "HumanEval_pass1"
COVARIATE: str = "MMLU_acc"
INTERNAL_X: str = "ECE"
INTERNAL_Y: str = "Brier"

REQUIRED_COLS: list[str] = [
    "model_id", "ECE", "Brier", "TruthfulQA_pct",
    "AdvGLUE_drop", "ANLI_drop", "MMLU_acc", "HumanEval_pass1",
]
GATE_COLS: list[str] = ["ECE", "TruthfulQA_pct", "MMLU_acc", "HumanEval_pass1", "Brier"]
MIN_MODELS: int = 25

PRIMARY_THRESHOLD: float = 0.40
INTERNAL_THRESHOLD: float = 0.30
DISCRIMINANT_THRESHOLD: float = 0.20
DECODING_INVARIANCE_THRESHOLD: float = 0.30

FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"
FIGURE_NAMES: dict = {
    "gate_bar":            "fig1_gate_bar.png",
    "raw_vs_partial":      "fig2_raw_vs_partial.png",
    "ece_brier_scatter":   "fig3_ece_brier_scatter.png",
    "discriminant":        "fig4_discriminant_validity.png",
    "decoding_invariance": "fig5_decoding_invariance.png",
}
