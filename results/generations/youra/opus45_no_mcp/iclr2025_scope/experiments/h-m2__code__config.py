"""Configuration for H-M2: Task-Specific Sharpness Comparison"""

LORA_CONFIG = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj"],
    lora_dropout=0.0,
)

TRAIN_CONFIG = dict(
    lr=2e-4,
    epochs=3,
    batch_size=4,
    warmup_pct=0.06,
    max_length=128,
    seed=42,
)

SHARPNESS_CONFIG = dict(
    sam_epsilon=0.05,
    max_batches=100,
)

BENCHMARKS = {
    "gsm8k": dict(
        hf_id="openai/gsm8k",
        subset="main",
        split="test",
        num_samples=1319,
        density=0.1,
    ),
    "nq": dict(
        hf_id="google-research-datasets/natural_questions",
        subset=None,
        split="validation",
        num_samples=500,
        density=0.9,
    ),
}

GATE_THRESHOLD = 0.8

MODEL_ID = "state-spaces/mamba-2.8b-hf"
