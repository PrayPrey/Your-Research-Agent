"""H-C1 configuration constants."""
import os
from pathlib import Path

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_ID = "deepseek-ai/deepseek-coder-7b-base"
DTYPE = "bfloat16"
ATTN_IMPL = "flash_attention_2"
# DEVICE_MAP = None  # DeepSpeed manages placement when using torchrun

# ── Experiment ─────────────────────────────────────────────────────────────────
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]
BENCHMARKS = ["humaneval", "mbpp"]

# ── Hyperparameters (identical to H-E2 for controlled comparison) ──────────────
FIXED_HPARAMS = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
    "dataset_text_field": "text",
}

EPOCHS_PER_CONDITION = {
    "humaneval_only": 6,
    "mbpp_only": 3,
    "leetcode_only": 1,
    "equal_mix": 2,
}

# ── Data ───────────────────────────────────────────────────────────────────────
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent.parent.parent  # TEST_dl4c

H_E2_DATASETS_DIR = str(_REPO_ROOT / "docs/youra_research/h-e2/data/sft_sources")
H_E2_RESULTS_CSV = str(_REPO_ROOT / "docs/youra_research/h-e2/results/all_results.csv")

# ── Paths ──────────────────────────────────────────────────────────────────────
CHECKPOINT_DIR = str(_REPO_ROOT / "docs/youra_research/h-c1/checkpoints")
RESULTS_DIR = str(_REPO_ROOT / "docs/youra_research/h-c1/results")
RESULTS_JSON = str(_REPO_ROOT / "docs/youra_research/h-c1/results/results.json")
RESULTS_CSV = str(_REPO_ROOT / "docs/youra_research/h-c1/results/results.csv")
REPORT_PATH = str(_REPO_ROOT / "docs/youra_research/h-c1/results/statistical_report.txt")
FIGURES_DIR = str(_REPO_ROOT / "docs/youra_research/h-c1/figures")
EVALPLUS_OUTPUT_DIR = str(_REPO_ROOT / "docs/youra_research/h-c1/results")

# ── H-E2 η² reference (from ANOVA F=11.37, df_between=3, df_within=8) ─────────
H_E2_REF_ETA_SQ = {
    "humaneval": (11.37 * 3) / (11.37 * 3 + 8),  # ≈ 0.810
    "mbpp": None,  # Not available from H-E2 partial results
}

# ── LoRA fallback ───────────────────────────────────────────────────────────────
LORA_ENABLED = False  # ponytail: set True only if full fine-tune OOM on 4x H100 80GB
LORA_CONFIG = {
    "r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}

# ── Run matrix ──────────────────────────────────────────────────────────────────
ALL_RUNS = [
    {"condition": c, "seed": s}
    for c in CONDITIONS
    for s in SEEDS
]  # 12 total

# ── Analysis thresholds ─────────────────────────────────────────────────────────
N_COMPARISONS = 12
ALPHA = 0.05
MIN_CONTRAST_PP = 2.0
