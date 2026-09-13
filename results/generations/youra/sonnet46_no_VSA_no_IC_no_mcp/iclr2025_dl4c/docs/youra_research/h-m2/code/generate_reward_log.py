"""generate_reward_log.py — H-M2: Run RLEF training and generate reward_monitoring.jsonl.

Uses H-E1's SimpleGRPOTrainer with the full APPS dataset stratified by difficulty.
Runs enough steps to get statistically meaningful per-bucket reward fractions.
"""
import json
import sys
import time
from pathlib import Path

# H-E1 code must be importable
H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE))

import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from data_utils import load_apps_train
from grpo_trainer import SimpleGRPOTrainer
from reward import fraction_reward_fn


def run_rlef_monitoring(config_path: str, reward_log_path: str, max_steps: int = 62) -> None:
    """Run RLEF training and write reward_monitoring.jsonl.

    max_steps: gradient steps to run (62 matches H-E1 smoke run for reproducibility)
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    model_name = config["model_name"]
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )
    ref_model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )

    print("Loading APPS dataset...")
    rlef_dataset = load_apps_train(tokenizer)["rlef"]
    print(f"RLEF dataset size: {len(rlef_dataset)}")

    # Count difficulty distribution
    difficulty_counts = {}
    for sample in rlef_dataset:
        d = sample.get("difficulty", "interview")
        difficulty_counts[d] = difficulty_counts.get(d, 0) + 1
    print(f"Difficulty distribution: {difficulty_counts}")

    trainer = SimpleGRPOTrainer(
        model=model,
        ref_model=ref_model,
        tokenizer=tokenizer,
        reward_fn=fraction_reward_fn,
        dataset=rlef_dataset,
        output_dir=str(H_E1_CODE / "checkpoints" / "rlef_hm2_monitor"),
        lr=config["training"]["lr"],
        batch_size=config["training"]["batch_size"],
        grad_accum=config["training"]["grad_accum"],
        num_epochs=config["training"]["epochs"],
        G=config["grpo"]["num_generations"],
        beta=config["grpo"]["beta"],
        max_new_tokens=config["training"]["max_new_tokens"],
        temperature=config["grpo"]["temperature_rollout"],
        max_grad_norm=config["training"]["grad_clip"],
        seed=config["training"]["seed"],
        reward_log_path=reward_log_path,
    )

    print(f"Starting RLEF training (reward log -> {reward_log_path})...")
    start = time.time()
    trainer.train()
    elapsed = time.time() - start
    print(f"Training complete in {elapsed:.1f}s")

    log_path = Path(reward_log_path)
    if log_path.exists():
        lines = log_path.read_text().splitlines()
        print(f"Reward log: {len(lines)} records written to {reward_log_path}")
    else:
        print(f"WARNING: reward log not written to {reward_log_path}")


if __name__ == "__main__":
    config_path = str(H_E1_CODE / "config.yaml")
    reward_log_path = str(H_E1_CODE / "logs" / "reward_monitoring.jsonl")
    run_rlef_monitoring(config_path, reward_log_path)
    print("EXPERIMENT COMPLETE")
