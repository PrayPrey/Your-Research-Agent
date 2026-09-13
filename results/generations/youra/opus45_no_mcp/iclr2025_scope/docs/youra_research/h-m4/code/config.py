"""Configuration for H-M4: Task-Dependent Transformation Emergence"""
import os

MODEL_CONFIG = dict(
    d_model=512,
    n_layers=4,
    n_heads=8,
    d_state=16,
    vocab_size=50304,
)

LORA_CONFIG_TRANSFORMER = dict(
    r=16,
    lora_alpha=32,
    lora_dropout=0.0,
    target_modules=["q_proj", "v_proj"],
)

LORA_CONFIG_MAMBA = dict(
    r=16,
    lora_alpha=32,
    lora_dropout=0.0,
    target_modules=["in_proj"],
)

TRAIN_CONFIG = dict(
    lr=1e-4,
    batch_size=4,
    epochs=5,
    max_length=512,
    warmup_pct=0.1,
    weight_decay=0.01,
    grad_clip=1.0,
    seed=42,
)

BENCHMARKS = {
    "gsm8k": dict(hf_id="openai/gsm8k", subset="main", split="test", num_samples=1319, retrieval_density=0.1, train_split="train", train_samples=500),
    "mmlu": dict(hf_id="cais/mmlu", subset="all", split="test", num_samples=1000, retrieval_density=0.5, train_split="validation", train_samples=500),
    "hotpotqa": dict(hf_id="hotpot_qa", subset="fullwiki", split="validation", num_samples=1000, retrieval_density=0.7, train_split="train", train_samples=500),
    "nq": dict(hf_id="google-research-datasets/natural_questions", subset=None, split="validation", num_samples=1000, retrieval_density=0.9, train_split="train", train_samples=500),
}

SHARPNESS_CONFIG = dict(
    sam_epsilon=0.05,
    max_batches=50,
)

RANK_CONFIG = dict(
    default_threshold=0.90,
)

GATE_THRESHOLD = dict(
    min_spearman_rho=0.7,
    max_p_value=0.01,
)

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M4_DIR = os.path.dirname(CODE_DIR)
CHECKPOINTS_DIR = os.path.join(H_M4_DIR, "checkpoints")
FIGURES_DIR = os.path.join(H_M4_DIR, "figures")
