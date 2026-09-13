"""Smoke test: verify training pipeline works with minimal compute."""
import os
import sys
import json
import torch
import numpy as np
import random
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
import torch.nn.functional as F

SMOKE_TRAIN_SAMPLES = 10
SMOKE_BATCH_SIZE = 2


def format_prompt(problem: dict) -> str:
    return f"""### Instruction:
Write a Python function to solve the following problem.

{problem['prompt']}

### Response:
"""


def run_smoke_test():
    print("="*60)
    print("SMOKE TEST: Verifying pipeline")
    print("="*60)

    # 1. Test data loading
    print("\n[1/5] Loading MBPP dataset...")
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="train")
    ds = ds.select(range(min(SMOKE_TRAIN_SAMPLES, len(ds))))
    print(f" Loaded {len(ds)} samples")

    # 2. Test model loading
    print("\n[2/5] Loading CodeLlama-7B-Instruct...")
    model_id = "codellama/CodeLlama-7b-Instruct-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    device = next(model.parameters()).device
    print(f" Model loaded on {device}")

    # 3. Test generation
    print("\n[3/5] Testing code generation...")
    prompt = format_prompt(ds[0])
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id
        )

    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f" Generated {len(outputs[0])} tokens")

    # 4. Test reward computation
    print("\n[4/5] Testing reward computation...")
    from reward import compute_reward

    code = "def add(a, b):\n    return a + b"
    tests = ["assert add(1, 2) == 3"]

    for cond in ["binary", "categorical", "high_bandwidth"]:
        r = compute_reward(code, tests, cond)
        print(f" {cond}: {r}")

    # 5. Test training step
    print("\n[5/5] Testing policy gradient training step...")
    optimizer = AdamW(model.parameters(), lr=1e-5)

    item = ds[0]
    prompt = format_prompt(item)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id
        )

    response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    code = full_response.split("### Response:")[-1].strip() if "### Response:" in full_response else response

    reward = compute_reward(code, item["test_list"], "high_bandwidth")
    print(f" Generated response, reward={reward:.3f}")

    # Compute loss
    full_text = prompt + response
    prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    full_ids = tokenizer(full_text, return_tensors="pt").input_ids.to(device)
    prompt_len = prompt_ids.shape[1]

    model_outputs = model(full_ids, labels=full_ids)
    logits = model_outputs.logits

    shift_logits = logits[:, prompt_len-1:-1, :]
    shift_labels = full_ids[:, prompt_len:]

    log_probs = F.log_softmax(shift_logits, dim=-1)
    selected_log_probs = log_probs.gather(2, shift_labels.unsqueeze(-1)).squeeze(-1)

    advantage = reward - 0.5
    loss = -selected_log_probs.mean() * advantage

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    print(f" Training step complete: loss={loss.item():.4f}")

    print("\n" + "="*60)
    print("SMOKE TEST PASSED")
    print("="*60)

    return True


if __name__ == "__main__":
    try:
        success = run_smoke_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nSMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
