"""
Configuration for H-E1: LoRA Adapter Geometric Signatures Existence Proof

This module contains all configuration constants for the experiment.
"""

import os

# ── Dataset registry ──────────────────────────────────────────────────────────
# Format: {short_name: (hf_dataset_id, config_name)}
# Note: Some datasets need alternative sources due to HF API changes
DATASETS = {
    "gsm8k":      ("gsm8k", "main"),
    "arc":        ("allenai/ai2_arc", "ARC-Challenge"),
    "logiqa":     ("hails/agieval-logiqa-en", None),  # Alternative source
    "strategyqa": ("ChilleD/StrategyQA", None),       # Alternative source
    "mnli":       ("nyu-mll/multi_nli", None),
    "qqp":        ("SetFit/qqp", None),
    "sst2":       ("SetFit/sst2", None),
    "mrpc":       ("SetFit/mrpc", None),
}

# Task category mapping for within/between cluster analysis
TASK_CATEGORIES = {
    "gsm8k": "reasoning",
    "arc": "reasoning",
    "logiqa": "reasoning",
    "strategyqa": "reasoning",
    "mnli": "nlu",
    "qqp": "nlu",
    "sst2": "nlu",
    "mrpc": "nlu",
}

# ── Base model ────────────────────────────────────────────────────────────────
# Note: Using TinyLlama (ungated) instead of Llama-3.2-1B-Instruct (gated)
# Both are ~1B parameter instruction-tuned models with similar architecture
BASE_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# ── LoRA config ───────────────────────────────────────────────────────────────
LORA_CONFIG = dict(
    r=32,
    lora_alpha=64,          # alpha=2r: standard scaling convention
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "up_proj", "down_proj", "gate_proj",
    ],
)

# ── Training config ───────────────────────────────────────────────────────────
TRAIN_CONFIG = dict(
    lr=2e-4,
    epochs=3,
    batch_size=8,
    warmup_ratio=0.1,
    weight_decay=0.01,
    max_length=512,
    max_samples=2000,       # per dataset, caps wall-time
    optimizer="adamw_torch",
    lr_scheduler_type="cosine",
    bf16=True,              # bfloat16 for Llama-3 on modern GPUs
    gradient_checkpointing=True,
)

# ── Experiment config ─────────────────────────────────────────────────────────
PRIMARY_SEED = 42
CONTROL_SEEDS = [42, 43, 44, 45, 46]
# PoC Mode: 5 seeds per task for faster validation (8 x 5 = 40 adapters)
# Full experiment: change to 20 for 160 adapters
ADAPTERS_PER_TASK = 5      # PoC: 8 tasks x 5 seeds = 40 adapters (~1.5 hours)

# ── Analysis thresholds (MUST_WORK gate) ──────────────────────────────────────
ANALYSIS_CONFIG = dict(
    p_threshold=0.05,
    cohens_d_threshold=0.5,
    ci_level=0.95,
    n_bootstrap=10000,
)

# ── Output paths ──────────────────────────────────────────────────────────────
# Use absolute path for reliability
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)  # Parent of code/
ADAPTER_DIR = os.path.join(HYPOTHESIS_FOLDER, "adapters")
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")

# Ensure output directories exist
for _dir in [ADAPTER_DIR, RESULTS_DIR, FIGURES_DIR]:
    os.makedirs(_dir, exist_ok=True)
