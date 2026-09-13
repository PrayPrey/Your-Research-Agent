"""Configuration for H-M1: Loss Landscape Geometry Analysis"""

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

MODEL_ID_BASELINE = "meta-llama/Llama-2-7b-hf"

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
}

LANDSCAPE_CONFIG = dict(
    sam_epsilon=0.05,
    hessian_top_k=50,
    num_bins=50,
    kl_eps=1e-10,
    batch_size=16,
    grad_accum=4,
    max_length=512,
    seed=42,
    eval_samples=500,
)

GATE_THRESHOLDS = dict(
    sharpness_delta_pct_min=0.10,
    kl_divergence_min=0.1,
)
