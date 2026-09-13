"""generate_reward_log_mini.py — H-M2: Mini RLEF run to generate reward_monitoring.jsonl.

Uses H-E1's SimpleGRPOTrainer with reduced settings for faster reward log generation.
Generates statistically meaningful data across all 3 APPS difficulty buckets.
"""
import json
import sys
import time
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE))

import torch
import yaml
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from grpo_trainer import SimpleGRPOTrainer
from reward import fraction_reward_fn


def load_apps_stratified(tokenizer, n_per_bucket=50):
    """Load APPS samples balanced across all 3 difficulty buckets."""
    print("Loading APPS dataset from cache...")
    ds = load_dataset("codeparrot/apps", split="train")

    buckets = {"introductory": [], "interview": [], "competition": []}
    for sample in ds:
        d = sample.get("difficulty", "interview")
        if d in buckets and len(buckets[d]) < n_per_bucket:
            # Format as H-E1 expects
            prompt = f"# Problem\n{sample.get('question', '')[:800]}\n\n# Solution\n"
            test_cases_raw = sample.get("input_output", "{}")
            try:
                io_data = json.loads(test_cases_raw) if isinstance(test_cases_raw, str) else test_cases_raw
                inputs = io_data.get("inputs", [])
                outputs = io_data.get("outputs", [])
                test_cases = [{"input": inp, "output": out} for inp, out in zip(inputs[:3], outputs[:3])]
            except Exception:
                test_cases = []

            buckets[d].append({
                "prompt": prompt,
                "test_cases": test_cases,
                "difficulty": d,
            })

    # Combine all buckets
    combined = []
    for d, samples in buckets.items():
        combined.extend(samples)
        print(f"  {d}: {len(samples)} samples")

    print(f"Total stratified dataset: {len(combined)} samples")
    return combined


def run_mini_rlef(reward_log_path: str) -> None:
    """Run 1 epoch of RLEF with small config to generate reward log."""
    with open(H_E1_CODE / "config.yaml") as f:
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

    # Load stratified dataset
    dataset = load_apps_stratified(tokenizer, n_per_bucket=60)

    # Mini config: smaller batches, lower G, 1 epoch, log every step
    trainer = SimpleGRPOTrainer(
        model=model,
        ref_model=ref_model,
        tokenizer=tokenizer,
        reward_fn=fraction_reward_fn,
        dataset=dataset,
        output_dir=str(H_E1_CODE / "checkpoints" / "rlef_hm2_mini"),
        lr=1e-5,
        batch_size=4,
        grad_accum=4,   # smaller grad_accum -> more frequent steps -> log sooner
        num_epochs=2,
        G=4,            # fewer generations -> faster
        beta=0.04,
        max_new_tokens=256,  # shorter outputs -> faster
        temperature=0.8,
        max_grad_norm=1.0,
        seed=42,
        reward_log_path=reward_log_path,
        logging_steps=5,  # log every 5 steps
    )

    print(f"Starting mini RLEF training (log every 5 steps)...")
    print(f"  dataset={len(dataset)}, batch=4, grad_accum=4, epochs=2, G=4")
    print(f"  Expected steps: {(len(dataset) // (4*4)) * 2}")
    start = time.time()
    trainer.train()
    elapsed = time.time() - start
    print(f"Training complete in {elapsed:.1f}s")

    log_path = Path(reward_log_path)
    if log_path.exists():
        lines = log_path.read_text().splitlines()
        print(f"Reward log: {len(lines)} records written to {reward_log_path}")
    else:
        print(f"WARNING: reward log not written")


if __name__ == "__main__":
    reward_log_path = str(H_E1_CODE / "logs" / "reward_monitoring.jsonl")
    run_mini_rlef(reward_log_path)
    print("EXPERIMENT COMPLETE")
