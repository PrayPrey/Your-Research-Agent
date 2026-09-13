#!/usr/bin/env python
"""Run experiment for H-E1: Reward Information Bandwidth.

PoC validation with reduced scale:
- 3 conditions: binary, categorical, high_bandwidth
- 3 seeds (reduced from 5 for PoC)
- 1 epoch (reduced from 3 for PoC)
- Full MBPP train set, periodic evaluation
"""
import os
import sys
import json
import random
import torch
import torch.nn.functional as F
import numpy as np
from datetime import datetime
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from tqdm import tqdm

# PoC reduced scale
POC_SEEDS = [0, 1, 2]
POC_EPOCHS = 1
EVAL_INTERVAL = 100
BATCH_SIZE = 4
MAX_NEW_TOKENS = 256
LEARNING_RATE = 1e-5

REWARD_CONDITIONS = ["binary", "categorical", "high_bandwidth"]


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def format_prompt(problem: dict) -> str:
    return f"""### Instruction:
Write a Python function to solve the following problem.

{problem['prompt']}

### Response:
"""


def compute_reward_internal(code: str, test_cases: list, condition: str) -> float:
    """Inline reward computation to avoid import issues."""
    import subprocess
    import tempfile

    results = []
    for test in test_cases:
        full_code = code + "\n" + test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(full_code)
            f.flush()
            try:
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=5.0
                )
                passed = result.returncode == 0
                if not passed:
                    if "SyntaxError" in result.stderr or "IndentationError" in result.stderr:
                        error_type = "syntax_error"
                    elif "AssertionError" in result.stderr:
                        error_type = "assertion_error"
                    else:
                        error_type = "runtime_error"
                else:
                    error_type = "passed"
                results.append((passed, error_type))
            except subprocess.TimeoutExpired:
                results.append((False, "runtime_error"))
            except Exception:
                results.append((False, "runtime_error"))
            finally:
                try:
                    os.unlink(f.name)
                except:
                    pass

    if condition == "binary":
        return 1.0 if all(r[0] for r in results) else 0.0

    ERROR_SCORES = {"passed": 1.0, "assertion_error": 0.5, "runtime_error": 0.25, "syntax_error": 0.0}

    if condition == "categorical":
        if all(r[0] for r in results):
            return 1.0
        worst = min(ERROR_SCORES.get(r[1], 0.0) for r in results if not r[0])
        return worst

    if condition == "high_bandwidth":
        cat_score = compute_reward_internal(code, test_cases, "categorical")
        pass_ratio = sum(1 for r in results if r[0]) / len(results) if results else 0.0
        return 0.5 * cat_score + 0.3 * pass_ratio + 0.2 * 0.0  # skip partial credit for speed

    return 0.0


def evaluate_pass_at_1(model, tokenizer, dataset, device) -> float:
    model.eval()
    passed = 0
    total = len(dataset)

    for item in dataset:
        prompt = format_prompt(item)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id
            )

        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = full_output.split("### Response:")[-1].strip() if "### Response:" in full_output else full_output

        try:
            r = compute_reward_internal(code, item["test_list"], "binary")
            if r == 1.0:
                passed += 1
        except Exception:
            pass

    model.train()
    return passed / total if total > 0 else 0.0


def run_condition(condition: str, seed: int, train_ds, val_ds) -> dict:
    set_seed(seed)

    print(f"\n{'='*60}")
    print(f"Training: condition={condition}, seed={seed}")
    print(f"{'='*60}")

    model = AutoModelForCausalLM.from_pretrained(
        "codellama/CodeLlama-7b-Instruct-hf",
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-Instruct-hf")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = next(model.parameters()).device
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    metric_log = []
    rewards_log = []
    n_samples = 0

    model.train()

    for epoch in range(POC_EPOCHS):
        print(f"\nEpoch {epoch + 1}/{POC_EPOCHS}")

        indices = list(range(len(train_ds)))
        random.shuffle(indices)

        pbar = tqdm(range(0, len(train_ds), BATCH_SIZE), desc=f"Epoch {epoch+1}")

        for batch_start in pbar:
            batch_indices = indices[batch_start:batch_start + BATCH_SIZE]
            batch_items = [train_ds[i] for i in batch_indices]

            batch_loss = 0.0
            batch_rewards = []

            for item in batch_items:
                prompt = format_prompt(item)
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=MAX_NEW_TOKENS,
                        do_sample=True,
                        top_p=0.9,
                        temperature=0.8,
                        pad_token_id=tokenizer.pad_token_id
                    )

                response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = full_output.split("### Response:")[-1].strip() if "### Response:" in full_output else response

                reward = compute_reward_internal(code, item["test_list"], condition)
                rewards_log.append(reward)
                batch_rewards.append(reward)

                # Policy gradient loss
                full_text = prompt + response
                prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
                full_ids = tokenizer(full_text, return_tensors="pt", truncation=True, max_length=2048).input_ids.to(device)
                prompt_len = min(prompt_ids.shape[1], full_ids.shape[1] - 1)

                model_out = model(full_ids, labels=full_ids)
                logits = model_out.logits

                if full_ids.shape[1] > prompt_len + 1:
                    shift_logits = logits[:, prompt_len-1:-1, :]
                    shift_labels = full_ids[:, prompt_len:]
                    log_probs = F.log_softmax(shift_logits, dim=-1)
                    selected_log_probs = log_probs.gather(2, shift_labels.unsqueeze(-1)).squeeze(-1)
                    advantage = reward - 0.5
                    loss = -selected_log_probs.mean() * advantage
                    batch_loss += loss

            if len(batch_items) > 0 and torch.is_tensor(batch_loss) and batch_loss != 0:
                batch_loss = batch_loss / len(batch_items)
                optimizer.zero_grad()
                batch_loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            n_samples += len(batch_items)

            pbar.set_postfix({
                "reward": f"{np.mean(batch_rewards):.3f}",
                "loss": f"{batch_loss.item():.4f}" if torch.is_tensor(batch_loss) else "0"
            })

            if n_samples % EVAL_INTERVAL == 0:
                p1 = evaluate_pass_at_1(model, tokenizer, val_ds, device)
                metric_log.append((n_samples, p1))
                print(f"\n [Eval] Samples: {n_samples}, pass@1: {p1:.4f}, mean_reward: {np.mean(rewards_log[-50:]):.4f}")
                model.train()

    # Final evaluation
    final_p1 = evaluate_pass_at_1(model, tokenizer, val_ds, device)

    # Cleanup
    del model
    torch.cuda.empty_cache()

    return {
        "condition": condition,
        "seed": seed,
        "metric_log": metric_log,
        "final_pass_at_1": final_p1,
        "rewards": rewards_log,
        "n_samples": n_samples
    }


def main():
    print("="*60)
    print("H-E1: Reward Information Bandwidth Experiment")
    print(f"Start time: {datetime.now().isoformat()}")
    print("="*60)
    print(f"Conditions: {REWARD_CONDITIONS}")
    print(f"Seeds: {POC_SEEDS}")
    print(f"Epochs: {POC_EPOCHS}")

    # Load datasets
    print("\nLoading datasets...")
    train_ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="train")
    val_ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="validation")
    val_ds = val_ds.select(range(min(50, len(val_ds))))
    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}")

    all_results = {}

    for condition in REWARD_CONDITIONS:
        all_results[condition] = {}
        for seed in POC_SEEDS:
            result = run_condition(condition, seed, train_ds, val_ds)
            all_results[condition][seed] = result

            # Save intermediate results
            os.makedirs("outputs", exist_ok=True)
            with open("outputs/results.json", "w") as f:
                json.dump(all_results, f, indent=2, default=str)

    # Summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)

    for condition in REWARD_CONDITIONS:
        p1s = [all_results[condition][s]["final_pass_at_1"] for s in POC_SEEDS]
        print(f"{condition}: pass@1 = {np.mean(p1s):.4f} ± {np.std(p1s):.4f}")

    # Gate check
    binary_mean = np.mean([all_results["binary"][s]["final_pass_at_1"] for s in POC_SEEDS])
    hb_mean = np.mean([all_results["high_bandwidth"][s]["final_pass_at_1"] for s in POC_SEEDS])

    print(f"\nGate check: high_bandwidth ({hb_mean:.4f}) vs binary ({binary_mean:.4f})")
    if hb_mean > binary_mean:
        print("GATE: PASSED (high_bandwidth > binary)")
    else:
        print("GATE: FAILED (high_bandwidth <= binary)")

    print(f"\nEnd time: {datetime.now().isoformat()}")

    return all_results


if __name__ == "__main__":
    main()
