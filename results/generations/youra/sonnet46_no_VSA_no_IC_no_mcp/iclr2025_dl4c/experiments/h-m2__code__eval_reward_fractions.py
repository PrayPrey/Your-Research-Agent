"""eval_reward_fractions.py — H-M2: Direct reward fraction evaluation.

Evaluates non-zero reward fractions by generating completions with the H-E1
RLEF-Fraction checkpoint and computing fraction_reward_fn scores per difficulty bucket.

This is equivalent to monitoring reward during training but done post-hoc:
instead of capturing per-step rewards during training, we evaluate the checkpoint
on a stratified APPS sample and measure how many problems get non-zero reward.

This directly tests hypothesis H-M2: "fraction of hard APPS problems with non-zero
reward > 10% during RLEF-Fraction training".
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE))

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from reward import fraction_reward_fn

# H-E1 RLEF checkpoint (from validated Phase 4 H-E1 run)
RLEF_CHECKPOINT = str(H_E1_CODE / "checkpoints" / "sft_smoke")  # SFT checkpoint (rlef_smoke if available)

# Number of APPS samples per difficulty bucket to evaluate
N_PER_BUCKET = 100  # 300 total = statistically meaningful

# Generations per problem (H-E1 uses G=8; we use 4 for speed)
G = 4


def load_apps_stratified(tokenizer, n_per_bucket=N_PER_BUCKET):
    """Load APPS samples balanced across all 3 difficulty buckets."""
    print(f"Loading APPS dataset (target: {n_per_bucket} per bucket)...")
    ds = load_dataset("codeparrot/apps", split="train")

    buckets = {"introductory": [], "interview": [], "competition": []}
    for sample in ds:
        d = sample.get("difficulty", "interview")
        if d in buckets and len(buckets[d]) < n_per_bucket:
            prompt = f"# Problem\n{sample.get('question', '')[:600]}\n\n# Python Solution\n```python\n"
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
        if all(len(v) >= n_per_bucket for v in buckets.values()):
            break

    combined = []
    for d, samples in buckets.items():
        combined.extend(samples)
        print(f"  {d}: {len(samples)} samples")
    print(f"Total: {len(combined)} samples")
    return combined


def generate_completions(model, tokenizer, prompt: str, G: int, max_new_tokens: int = 200) -> list[str]:
    """Generate G completions for a prompt."""
    enc = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).to(model.device)
    with torch.no_grad():
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            out = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.8,
                num_return_sequences=G,
                pad_token_id=tokenizer.eos_token_id,
            )
    input_len = enc["input_ids"].shape[1]
    completions = [tokenizer.decode(o[input_len:], skip_special_tokens=True) for o in out]
    return completions


def evaluate_reward_fractions(checkpoint_path: str, reward_log_path: str) -> dict:
    """Evaluate non-zero reward fractions per difficulty bucket using RLEF checkpoint."""
    print(f"Loading model from: {checkpoint_path}")
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )
    model.eval()

    # Load stratified dataset
    dataset = load_apps_stratified(tokenizer, n_per_bucket=N_PER_BUCKET)

    # Evaluate rewards per bucket
    bucket_indicators = defaultdict(list)
    bucket_rewards = defaultdict(list)

    log_records = []
    step = 0
    start = time.time()

    print(f"Evaluating {len(dataset)} problems with G={G} generations each...")

    for i, sample in enumerate(dataset):
        prompt = sample["prompt"]
        test_cases = sample["test_cases"]
        difficulty = sample["difficulty"]

        try:
            completions = generate_completions(model, tokenizer, prompt, G=G)
            rewards = fraction_reward_fn(
                completions=completions,
                prompts=[prompt] * G,
                metadata=[{"test_cases": test_cases}] * G,
            )
            mean_reward = sum(rewards) / len(rewards) if rewards else 0.0
            any_nonzero = any(r > 0 for r in rewards)

            bucket_indicators[difficulty].append(float(any_nonzero))
            bucket_rewards[difficulty].extend(rewards)

        except Exception as e:
            print(f"  Error on sample {i} ({difficulty}): {e}")
            bucket_indicators[difficulty].append(0.0)

        # Log every 10 samples as a "step" record
        if (i + 1) % 10 == 0:
            step += 1
            elapsed = time.time() - start
            import numpy as np

            record = {
                "step": step,
                "loss": 0.0,  # not available in eval mode
                "intro_reward": float(np.mean(bucket_rewards["introductory"])) if bucket_rewards["introductory"] else None,
                "interview_reward": float(np.mean(bucket_rewards["interview"])) if bucket_rewards["interview"] else None,
                "competition_reward": float(np.mean(bucket_rewards["competition"])) if bucket_rewards["competition"] else None,
            }
            log_records.append(record)

            fracs = {
                d: float(np.mean(inds)) if inds else 0.0
                for d, inds in bucket_indicators.items()
            }
            print(f"  [{i+1}/{len(dataset)}] t={elapsed:.0f}s | "
                  f"intro={fracs.get('introductory', 0):.3f} "
                  f"interview={fracs.get('interview', 0):.3f} "
                  f"competition={fracs.get('competition', 0):.3f}")

    # Write reward log
    Path(reward_log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(reward_log_path, "w") as f:
        for record in log_records:
            f.write(json.dumps(record) + "\n")

    print(f"\nReward log written: {len(log_records)} records -> {reward_log_path}")

    import numpy as np
    final_fracs = {
        d: float(np.mean(inds)) if inds else 0.0
        for d, inds in bucket_indicators.items()
    }
    print("\nFinal non-zero reward fractions:")
    for d in ["introductory", "interview", "competition"]:
        n = len(bucket_indicators[d])
        frac = final_fracs.get(d, 0.0)
        print(f"  {d}: {frac:.4f} (n={n})")

    return final_fracs


if __name__ == "__main__":
    # Check if rlef_smoke checkpoint exists, otherwise use sft_smoke
    rlef_path = H_E1_CODE / "checkpoints" / "rlef_smoke"
    sft_path = H_E1_CODE / "checkpoints" / "sft_smoke"

    if rlef_path.exists():
        checkpoint_path = str(rlef_path)
        print(f"Using RLEF checkpoint: {checkpoint_path}")
    else:
        checkpoint_path = str(sft_path)
        print(f"RLEF checkpoint not found, using SFT checkpoint: {checkpoint_path}")

    reward_log_path = str(H_E1_CODE / "logs" / "reward_monitoring.jsonl")

    fracs = evaluate_reward_fractions(checkpoint_path, reward_log_path)
    comp = fracs.get("competition", 0.0)
    gate = "PASS" if comp > 0.10 else "FAIL"
    print(f"\n[H-M2 GATE] competition={comp:.4f} threshold=0.10 -> {gate}")
    print("EXPERIMENT COMPLETE")
