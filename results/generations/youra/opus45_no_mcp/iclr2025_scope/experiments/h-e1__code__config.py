"""Configuration for H-E1: Task-Dependent Adaptation Transformation Exists"""

LORA_CONFIG_TRANSFORMER = dict(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.0,
)

LORA_CONFIG_MAMBA = dict(
    r=16,
    lora_alpha=32,
    target_modules=["in_proj", "out_proj"],
    lora_dropout=0.0,
)

TRAIN_CONFIG = dict(
    lr=2e-4,
    weight_decay=0.01,
    betas=(0.9, 0.999),
    warmup_steps=100,
    batch_size=4,
    grad_accum=4,
    epochs=3,
    seed=42,
)

BENCHMARKS = {
    "gsm8k": dict(
        hf_id="openai/gsm8k",
        subset="main",
        split="test",
        metric="exact_match",
        density=0.1,
    ),
    "nq": dict(
        hf_id="google-research-datasets/natural_questions",
        subset=None,
        split="validation",
        metric="f1",
        density=0.9,
    ),
    "mmlu": dict(
        hf_id="cais/mmlu",
        subset="all",
        split="test",
        metric="accuracy",
        density=0.5,
    ),
    "hotpotqa": dict(
        hf_id="hotpot_qa",
        subset="fullwiki",
        split="validation",
        metric="f1",
        density=0.7,
    ),
}

GATE_THRESHOLDS = dict(
    gsm8k_delta_min=-0.05,
    nq_delta_max=-0.15,
    spearman_min=0.5,
)

MODEL_ID_BASELINE = "meta-llama/Llama-2-7b-hf"
