"""Task B: APPS difficulty-stratified SFT training loss via forward pass."""
import json
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model_and_tokenizer(checkpoint_path: str, device: str = "cuda"):
    """Load model in eval mode. Returns (model, tokenizer)."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    except ValueError:
        # Checkpoint tokenizer_config has unknown class; fall back to base model tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            "deepseek-ai/deepseek-coder-7b-base", trust_remote_code=True
        )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map=device if device == "cuda" else None,
        trust_remote_code=True,
    )
    model.eval()
    return model, tokenizer


def compute_per_example_loss(
    model,
    tokenizer,
    example: dict,
    max_length: int = 2048,
    device: str = "cuda",
) -> float:
    """Forward pass on one APPS example. Returns scalar cross-entropy loss (nats).
    Returns None if example['solutions'] is empty or unparseable."""
    try:
        solns = json.loads(example.get("solutions", "[]") or "[]")
    except (json.JSONDecodeError, TypeError):
        return None
    if not solns:
        return None

    solution_str = solns[0]
    problem_text = example.get("problem", "")
    text = problem_text + "\n" + solution_str

    enc = tokenizer(text, max_length=max_length, truncation=True, return_tensors="pt")
    input_ids = enc["input_ids"].to(device)
    T = input_ids.shape[1]

    labels = input_ids.clone()
    problem_enc = tokenizer(problem_text, max_length=max_length, truncation=True, return_tensors="pt")
    problem_len = problem_enc["input_ids"].shape[1]

    if problem_len >= T:
        # Entire input is problem tokens, no solution signal
        return None

    labels[:, :problem_len] = -100  # mask problem tokens

    with torch.no_grad():
        out = model(input_ids=input_ids, labels=labels)
    return out.loss.item()


def compute_difficulty_stratified_loss(
    checkpoint_path: str,
    dataset_name: str = "codeparrot/apps",
    split: str = "train",
    output_path: str = "results/h-m1/apps_difficulty_loss.json",
    max_examples_per_bucket: int = 500,
    device: str = "cuda",
) -> dict:
    """Stratified loss computation. Returns full results dict (also written to output_path)."""
    model, tokenizer = load_model_and_tokenizer(checkpoint_path, device)
    ds = load_dataset(dataset_name, split=split, trust_remote_code=True)

    buckets: dict[str, list] = {"introductory": [], "interview": [], "competition": []}

    for example in tqdm(ds, desc="Computing per-example loss"):
        diff = example.get("difficulty", "")
        if diff not in buckets:
            continue
        if len(buckets[diff]) >= max_examples_per_bucket:
            continue
        # ponytail: global cap per bucket; per-bucket stratified sampling if class imbalance matters
        loss = compute_per_example_loss(model, tokenizer, example, device=device)
        if loss is not None:
            buckets[diff].append(loss)

    results = {}
    for diff, losses in buckets.items():
        if losses:
            arr = np.array(losses)
            results[diff] = {"mean": float(arr.mean()), "std": float(arr.std()), "count": len(arr)}
        else:
            results[diff] = {"mean": None, "std": None, "count": 0}

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved loss results to {output_path}")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/sft_baseline/")
    parser.add_argument("--output", default="results/h-m1/apps_difficulty_loss.json")
    parser.add_argument("--max_per_bucket", type=int, default=500)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    results = compute_difficulty_stratified_loss(
        args.checkpoint, output_path=args.output,
        max_examples_per_bucket=args.max_per_bucket, device=args.device
    )
    print("\nResults:")
    for diff, stats in results.items():
        print(f"  {diff}: mean={stats['mean']:.4f if stats['mean'] is not None else 'N/A'}, "
              f"count={stats['count']}")
