"""Configuration for H-M3: LoRA Adaptation Efficiency vs Landscape Geometry"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-m2", "code"))

LORA_CONFIG = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj"],
    lora_dropout=0.0,
)

TRAIN_CONFIG = dict(
    lr=1e-4,
    epochs=5,
    batch_size=4,
    patience=2,
    weight_decay=0.01,
    grad_clip=1.0,
    warmup_pct=0.06,
    max_length=128,
    seed=42,
)

SHARPNESS_CONFIG = dict(
    sam_epsilon=0.05,
    max_batches=50,
)

RANK_CONFIG = dict(
    thresholds=[0.85, 0.90, 0.95],
    default_threshold=0.90,
)

BENCHMARKS = {
    "gsm8k": dict(
        hf_id="openai/gsm8k",
        subset="main",
        split="test",
        train_split="train",
        num_samples=1319,
        train_samples=1000,
        density=0.1,
    ),
    "nq": dict(
        hf_id="google-research-datasets/natural_questions",
        subset=None,
        split="validation",
        train_split="train",
        num_samples=500,
        train_samples=500,
        density=0.9,
    ),
}

SEEDS = [42, 123, 456]

GATE_THRESHOLD = 0.5

MODEL_ID = "state-spaces/mamba-2.8b-hf"

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M3_DIR = os.path.dirname(CODE_DIR)
CHECKPOINTS_DIR = os.path.join(H_M3_DIR, "checkpoints")
FIGURES_DIR = os.path.join(H_M3_DIR, "figures")
