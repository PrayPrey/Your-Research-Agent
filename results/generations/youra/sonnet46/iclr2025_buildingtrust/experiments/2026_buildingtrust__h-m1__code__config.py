"""
config.py — H-M1 Base Calibration Verification
Single fixed config: paths, thresholds, constants.
"""

import os
from pathlib import Path

# ── Directory anchoring ───────────────────────────────────────────────────────
# h-m1/code/ is the CWD when run_experiment.py is executed
_CODE_DIR = Path(__file__).parent.resolve()
_H_M1_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M1_DIR.parent / "h-e1"

# ── External paths (h-e1 artifacts) ──────────────────────────────────────────
H_E1_VALIDATION_PATH: str = str(_H_E1_DIR / "04_validation.md")
H_E1_RESULTS_DIR: str = str(_H_E1_DIR / "code" / "results")
H_E1_CODE_DIR: str = str(_H_E1_DIR / "code")

# ── H-M1 output paths ─────────────────────────────────────────────────────────
H_M1_RESULTS_DIR: str = str(_CODE_DIR / "results")
H_M1_FIGURES_DIR: str = str(_H_M1_DIR / "figures")
H_M1_REPORT_PATH: str = str(_H_M1_DIR / "04_validation.md")
H_M1_EXPERIMENT_RESULTS_JSON: str = str(_H_M1_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M1_DIR.parent / "verification_state.yaml")

# ── Gate configuration ────────────────────────────────────────────────────────
GATE_THRESHOLD: float = 0.15   # ECE_base < 0.15 → PASS
BASE_SIZES: list = ["1.4b", "2.8b", "6.9b"]
N_BINS: int = 15
SEED: int = 42

# ── Model HuggingFace IDs ──────────────────────────────────────────────────────
BASE_MODEL_HF_IDS: dict = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

# ── lm-eval configuration (Path B fallback) ───────────────────────────────────
LMEVAL_TASKS: list = ["mmlu"]
LMEVAL_NUM_FEWSHOT: int = 0
LMEVAL_BATCH_SIZE: str = "auto"
LMEVAL_LOG_SAMPLES: bool = True
LMEVAL_TIMEOUT_SECONDS: int = 7200

# ── Figure configuration ───────────────────────────────────────────────────────
FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

# ── Report required fields ────────────────────────────────────────────────────
REPORT_REQUIRED_FIELDS = [
    "gate_result",
    "ece_table",
    "execution_path",
    "key_findings",
    "figure_paths",
]
