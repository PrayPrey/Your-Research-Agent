"""
config.py — H-M2 Pre-Softmax Logit Margin Inflation
Single fixed config: paths, constants, model registry.
"""
from pathlib import Path

# ── Directory anchoring (same pattern as h-m1/code/config.py) ─────────────────
_CODE_DIR = Path(__file__).parent.resolve()
_H_M2_DIR = _CODE_DIR.parent
_H_E1_DIR = _H_M2_DIR.parent / "h-e1"
_H_M1_DIR = _H_M2_DIR.parent / "h-m1"

# ── External paths (h-e1 artifacts) ──────────────────────────────────────────
H_E1_RESULTS_DIR: str = str(_H_E1_DIR / "code" / "results")
H_E1_CODE_DIR: str = str(_H_E1_DIR / "code")
H_E1_VALIDATION_PATH: str = str(_H_E1_DIR / "04_validation.md")

# ── H-M2 output paths ─────────────────────────────────────────────────────────
H_M2_RESULTS_DIR: str = str(_CODE_DIR / "results")
H_M2_FIGURES_DIR: str = str(_H_M2_DIR / "figures")
H_M2_REPORT_PATH: str = str(_H_M2_DIR / "04_validation.md")
H_M2_EXPERIMENT_RESULTS_JSON: str = str(_H_M2_DIR / "experiment_results.json")
VERIFICATION_STATE_PATH: str = str(_H_M2_DIR.parent / "verification_state.yaml")

# ── Gate configuration ────────────────────────────────────────────────────────
GATE_TYPE: str = "SHOULD_WORK"
MIN_PPO_SIZES_PASSING: int = 2       # >= 2/3 PPO sizes must pass
N_BOOTSTRAP: int = 1000
SEED: int = 42
SIZES: list = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS: list = ["sft", "dpo", "ppo"]
N_ITEMS_EXPECTED: int = 14042        # MMLU full test set

# ── lm-eval Path B configuration ──────────────────────────────────────────────
LMEVAL_TASKS: list = ["mmlu"]
LMEVAL_NUM_FEWSHOT: int = 4          # Non-standard vs h-m1 (0): PRD requires 4-shot for MMLU
LMEVAL_BATCH_SIZE: str = "auto"
LMEVAL_LOG_SAMPLES: bool = True      # Required for per-item logprob extraction
LMEVAL_TIMEOUT_SECONDS: int = 7200

# ── Figure configuration ───────────────────────────────────────────────────────
FIGURE_DPI: int = 150
FIGURE_FORMAT: str = "png"

# ── Model Registry (12 models: 3 sizes × 4 alignments) ────────────────────────
# Key format: "{size}-{alignment}" — matches h-e1 load_lmeval_samples() glob pattern
# Note: h-m2 code uses "pythia-{size}-{alignment}" as model_id for load_lmeval_samples()
MODEL_REGISTRY: dict = {
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    "1.4b-sft":  "lomahony/pythia-1.4b-deduped-tldr",
    "1.4b-dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo",
    "1.4b-ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo",
    "2.8b-sft":  "lomahony/pythia-2.8b-deduped-tldr",
    "2.8b-dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo",
    "2.8b-ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo",
    "6.9b-sft":  "lomahony/pythia-6.9b-deduped-tldr",
    "6.9b-dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo",
    "6.9b-ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo",
}

BASE_MODEL_KEYS: list = [f"{s}-base" for s in SIZES]
ALIGNED_MODEL_KEYS: list = [f"{s}-{a}" for s in SIZES for a in ALIGNMENTS]
ALL_MODEL_KEYS: list = BASE_MODEL_KEYS + ALIGNED_MODEL_KEYS

# ── HuggingFace IDs by size/alignment (for Path B) ───────────────────────────
HF_MODEL_IDS: dict = {
    "1.4b": {
        "base": "EleutherAI/pythia-1.4b",
        "sft":  "lomahony/pythia-1.4b-deduped-tldr",
        "dpo":  "Leogrin/pythia-1.4b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-1.4b-sft-tldr-ppo",
    },
    "2.8b": {
        "base": "EleutherAI/pythia-2.8b",
        "sft":  "lomahony/pythia-2.8b-deduped-tldr",
        "dpo":  "Leogrin/pythia-2.8b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-2.8b-sft-tldr-ppo",
    },
    "6.9b": {
        "base": "EleutherAI/pythia-6.9b",
        "sft":  "lomahony/pythia-6.9b-deduped-tldr",
        "dpo":  "Leogrin/pythia-6.9b-sft-tldr-dpo",
        "ppo":  "usvsnsp/pythia-6.9b-sft-tldr-ppo",
    },
}
