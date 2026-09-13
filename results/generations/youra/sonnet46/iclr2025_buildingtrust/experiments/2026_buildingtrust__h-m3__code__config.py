"""
config.py — H-M3 Mechanism Discrimination (H1 vs H2 vs H3)
Flat module-level constants pattern (inherited from h-m2).
"""
from pathlib import Path

# ── Directory anchoring ───────────────────────────────────────────────────────
_CODE_DIR: Path = Path(__file__).parent.resolve()
_H_M3_DIR: Path = _CODE_DIR.parent
_H_M2_DIR: Path = _H_M3_DIR.parent / "h-m2"
_H_E1_DIR: Path = _H_M3_DIR.parent / "h-e1"

# ── External paths ────────────────────────────────────────────────────────────
H_E1_RESULTS_DIR: str = str(_H_E1_DIR / "code" / "results")
H_E1_CODE_DIR: str = str(_H_E1_DIR / "code")
H_M2_RESULTS_DIR: str = str(_H_M2_DIR / "code" / "results")

# ── H-M3 output paths ─────────────────────────────────────────────────────────
H_M3_RESULTS_DIR: str = str(_CODE_DIR / "results")
H_M3_TRUTHFULQA_DIR: str = str(_CODE_DIR / "results" / "truthfulqa")
H_M3_FIGURES_DIR: str = str(_H_M3_DIR / "figures")
H_M3_REPORT_PATH: str = str(_H_M3_DIR / "04_validation.md")
H_M3_EXPERIMENT_RESULTS_JSON: str = str(_H_M3_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M3_DIR.parent / "verification_state.yaml")

# ── Gate thresholds ───────────────────────────────────────────────────────────
GATE_TYPE: str = "SHOULD_WORK"
H1_RHO_THRESHOLD: float = 0.9
H2_RHO_THRESHOLD: float = 0.85
H1_COHENS_D_THRESHOLD: float = 0.1

# ── Experiment constants ───────────────────────────────────────────────────────
SIZES: list = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042
N_TRUTHFULQA_EXPECTED: int = 817
N_BOOTSTRAP: int = 1000
SEED: int = 42
N_BINS: int = 15

# ── Model registry (same 12 models as h-e1) ───────────────────────────────────
MODEL_REGISTRY: dict = {
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "1.4b-sft":  "lomahony/pythia-1.4b-helpful-sft",
    "1.4b-dpo":  "Leogrin/eleuther-pythia1.4b-hh-dpo",
    "1.4b-ppo":  "lomahony/pythia-1.4b-helpful-sfted1-ppo-3epochs-old",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "2.8b-sft":  "lomahony/pythia-2.8b-helpful-sft",
    "2.8b-dpo":  "lomahony/eleuther-pythia2.8b-hh-dpo",
    "2.8b-ppo":  "usvsnsp/pythia-2.8b-ppo",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    "6.9b-sft":  "lomahony/eleuther-pythia6.9b-hh-sft",
    "6.9b-dpo":  "lomahony/eleuther-pythia6.9b-hh-dpo",
    "6.9b-ppo":  "usvsnsp/pythia-6.9b-ppo",
}

BASE_MODEL_KEYS: list = [f"{size}-base" for size in SIZES]
ALIGNED_MODEL_KEYS: list = [f"{size}-{a}" for size in SIZES for a in ALIGNMENTS]
ALL_MODEL_KEYS: list = BASE_MODEL_KEYS + ALIGNED_MODEL_KEYS

HF_MODEL_IDS: dict = {
    "1.4b": {
        "base": "EleutherAI/pythia-1.4b",
        "sft":  "lomahony/pythia-1.4b-helpful-sft",
        "dpo":  "Leogrin/eleuther-pythia1.4b-hh-dpo",
        "ppo":  "lomahony/pythia-1.4b-helpful-sfted1-ppo-3epochs-old",
    },
    "2.8b": {
        "base": "EleutherAI/pythia-2.8b",
        "sft":  "lomahony/pythia-2.8b-helpful-sft",
        "dpo":  "lomahony/eleuther-pythia2.8b-hh-dpo",
        "ppo":  "usvsnsp/pythia-2.8b-ppo",
    },
    "6.9b": {
        "base": "EleutherAI/pythia-6.9b",
        "sft":  "lomahony/eleuther-pythia6.9b-hh-sft",
        "dpo":  "lomahony/eleuther-pythia6.9b-hh-dpo",
        "ppo":  "usvsnsp/pythia-6.9b-ppo",
    },
}

# ── lm-eval config ────────────────────────────────────────────────────────────
LMEVAL_NUM_FEWSHOT_MMLU: int = 4
LMEVAL_NUM_FEWSHOT_TQA: int = 0
LMEVAL_BATCH_SIZE: str = "auto"
LMEVAL_LOG_SAMPLES: bool = True
LMEVAL_TIMEOUT_SECONDS: int = 7200

# ── Figure config ─────────────────────────────────────────────────────────────
FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

# ── verification_state.yaml field mappings ────────────────────────────────────
VERIFICATION_STATE_H_M3_KEY: str = "h-m3"
VERIFICATION_STATE_FIELDS: dict = {
    "gate_pass": "gate_pass",
    "dominant_mechanism": "dominant_mechanism",
    "mean_rho_min": "mean_rho_min",
    "cohens_d_shared_max": "cohens_d_shared_max",
    "h3_flag": "h3_flag",
}
