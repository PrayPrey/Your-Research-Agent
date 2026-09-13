"""Re-export h-e1 config for import compatibility"""

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

MODEL_ID_BASELINE = "meta-llama/Llama-2-7b-hf"
