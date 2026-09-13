"""Training and evaluation orchestration for H-C1 comparison."""

import os
import sys

# Setup paths for h-e1 imports
H_E1_CODE = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
sys.path.insert(0, H_E1_CODE)
sys.path.insert(0, os.path.join(H_E1_CODE, "config"))

from transformers import GPT2Tokenizer

from h_c1_config import CPDR_CONFIG, REDPAJAMA_CONFIG, TRAIN_CONFIG, EVAL_CONFIG, CKPT_ROOT, SEEDS
from data.data_pipeline import build_dataset
from train.trainer import build_model, train
from eval.evaluator import evaluate


def run_single_seed(seed: int, ckpt_root: str = None) -> dict:
    """Train + eval CPDR and RP configs for one seed.
    Returns {'cpdr': {task: score}, 'redpajama': {task: score}}.
    """
    if ckpt_root is None:
        ckpt_root = CKPT_ROOT

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    result = {}

    for key, cfg in [("cpdr", CPDR_CONFIG), ("redpajama", REDPAJAMA_CONFIG)]:
        print(f"\n{'='*60}")
        print(f"Running {key.upper()} config (seed={seed})")
        print(f"{'='*60}")

        data_iter = build_dataset(cfg, tokenizer, TRAIN_CONFIG["total_tokens"])
        model = build_model(seed=seed)
        ckpt_dir = os.path.join(ckpt_root, f"{cfg.config_id}_seed{seed}")
        model_path = train(model, data_iter, ckpt_dir, cfg.config_id)
        result[key] = evaluate(model_path, tasks=EVAL_CONFIG["tasks"], batch_size=EVAL_CONFIG["batch_size"])
        print(f"{key.upper()} scores: {result[key]}")

    return result


def run_comparison_experiment(seeds: list = None, ckpt_root: str = None) -> dict:
    """Loop seeds, collect per-seed scores."""
    if seeds is None:
        seeds = SEEDS
    if ckpt_root is None:
        ckpt_root = CKPT_ROOT

    per_seed = []
    completed = []

    for seed in seeds:
        try:
            scores = run_single_seed(seed, ckpt_root)
            per_seed.append(scores)
            completed.append(seed)
        except Exception as e:
            print(f"[WARN] seed {seed} failed: {e}")
            import traceback
            traceback.print_exc()

    return {"per_seed": per_seed, "seeds_completed": completed}


if __name__ == "__main__":
    results = run_comparison_experiment()
    print("\nExperiment results:", results)
