"""Training loop for h-e1 error-type gating experiment."""
import os
import sys
import json
import torch
import random
import numpy as np
from tqdm import tqdm
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SEED, LR, BATCH_SIZE, TOTAL_STEPS, WARMUP_STEPS,
    MAX_OUTPUT_LEN, PASS_THRESHOLD, get_config
)
from data import load_apps, APPSDataset, get_tokenizer
from model import PPOPolicy, ppo_step
from reward import (
    Token, compute_gated_reward, execute_code_safely,
    get_gating_stats, reset_gating_stats
)
from evaluate import (
    compute_pass_at_1, track_steps_to_threshold, save_final_results
)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def tokens_with_lines(code: str, tokenizer) -> List[Token]:
    """Convert code string to list of Tokens with line numbers."""
    tokens = []
    lines = code.split('\n')
    for line_num, line in enumerate(lines, 1):
        line_tokens = tokenizer.tokenize(line)
        for t in line_tokens:
            tokens.append(Token(text=t, line=line_num))
    return tokens


def run_condition(
    gating: str,
    train_data,
    test_data,
    out_dir: str,
    seed: int = SEED,
    total_steps: int = TOTAL_STEPS,
    eval_interval: int = 1000,
    device: str = "cuda",
) -> Dict:
    """Run training for one condition (fine_always or fine_gated)."""
    print(f"\n{'='*60}")
    print(f"Starting condition: {gating}")
    print(f"{'='*60}")

    set_seed(seed)
    reset_gating_stats()

    os.makedirs(f"{out_dir}/{gating}", exist_ok=True)

    policy = PPOPolicy().to(device)
    tokenizer = get_tokenizer()
    optimizer = torch.optim.AdamW(
        policy.parameters(),
        lr=LR,
        betas=(0.9, 0.999),
        weight_decay=0.01,
    )

    dataset = APPSDataset(train_data, tokenizer)
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True
    )

    pass_at_1_log = []
    step = 0
    epoch = 0

    while step < total_steps:
        epoch += 1
        for batch in dataloader:
            if step >= total_steps:
                break

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            with torch.no_grad():
                gen_ids = policy.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=MAX_OUTPUT_LEN,
                    do_sample=True,
                )

            old_log_probs = policy.get_logprobs(input_ids, gen_ids, attention_mask)

            rewards_list = []
            for i in range(gen_ids.shape[0]):
                code = tokenizer.decode(gen_ids[i], skip_special_tokens=True)

                test_cases_str = batch["test_cases"][i]
                try:
                    tc_data = json.loads(test_cases_str) if isinstance(test_cases_str, str) else test_cases_str
                    inputs = tc_data.get("inputs", [])
                    outputs = tc_data.get("outputs", [])
                    test_cases = [{"input": inp, "output": out} for inp, out in zip(inputs, outputs)]
                except:
                    test_cases = []

                result, traceback = execute_code_safely(code, test_cases)
                tokens = tokens_with_lines(code, tokenizer)

                if len(tokens) < gen_ids.shape[1]:
                    tokens.extend([Token("", tokens[-1].line if tokens else 1)] * (gen_ids.shape[1] - len(tokens)))
                tokens = tokens[:gen_ids.shape[1]]

                reward = compute_gated_reward(tokens, traceback, gating)
                rewards_list.append(reward)

            max_len = gen_ids.shape[1]
            rewards = torch.zeros(len(rewards_list), max_len, device=device)
            for i, r in enumerate(rewards_list):
                rewards[i, :len(r)] = r[:max_len] if len(r) > max_len else r

            metrics = ppo_step(
                policy=policy,
                optimizer=optimizer,
                input_ids=input_ids,
                attention_mask=attention_mask,
                old_decoder_ids=gen_ids,
                old_log_probs=old_log_probs,
                rewards=rewards,
            )

            step += 1

            if step % 100 == 0:
                print(f"[{gating}] Step {step}: loss={metrics['loss']:.4f}, reward={metrics['reward_mean']:.4f}")

            if step % eval_interval == 0:
                p1 = compute_pass_at_1(policy, test_data, device, max_samples=500)
                pass_at_1_log.append((step, p1))
                print(f"[{gating}] Step {step}: pass@1={p1:.4f}")

                torch.save(policy.state_dict(), f"{out_dir}/{gating}/checkpoint_{step}.pt")

    final_p1 = compute_pass_at_1(policy, test_data, device, max_samples=500)
    pass_at_1_log.append((step, final_p1))

    steps_to_threshold = track_steps_to_threshold(pass_at_1_log, PASS_THRESHOLD)
    gating_stats = get_gating_stats()

    results = save_final_results(
        condition=gating,
        pass_at_1_log=pass_at_1_log,
        steps_to_threshold=steps_to_threshold,
        gating_stats=gating_stats,
        out_dir=f"{out_dir}/{gating}",
    )

    print(f"\n[{gating}] Training complete:")
    print(f"  Final pass@1: {final_p1:.4f}")
    print(f"  Steps to {PASS_THRESHOLD*100:.0f}%: {steps_to_threshold}")
    print(f"  Gating stats: {gating_stats}")

    return results


def main():
    """Run both conditions and compare."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", default="outputs")
    parser.add_argument("--total_steps", type=int, default=TOTAL_STEPS)
    parser.add_argument("--eval_interval", type=int, default=1000)
    parser.add_argument("--train_size", type=int, default=5000)
    parser.add_argument("--test_size", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--smoke_test", action="store_true", help="Run minimal smoke test")
    args = parser.parse_args()

    if args.smoke_test:
        args.total_steps = 100
        args.eval_interval = 50
        args.train_size = 100
        args.test_size = 100

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    os.makedirs(args.out_dir, exist_ok=True)

    print("Loading APPS dataset...")
    train_data = load_apps("train", args.train_size)
    test_data = list(load_apps("test", args.test_size))
    print(f"Loaded {len(train_data)} train, {len(test_data)} test problems")

    results_fine_always = run_condition(
        gating="fine_always",
        train_data=train_data,
        test_data=test_data,
        out_dir=args.out_dir,
        seed=args.seed,
        total_steps=args.total_steps,
        eval_interval=args.eval_interval,
        device=device,
    )

    results_fine_gated = run_condition(
        gating="fine_gated",
        train_data=train_data,
        test_data=test_data,
        out_dir=args.out_dir,
        seed=args.seed,
        total_steps=args.total_steps,
        eval_interval=args.eval_interval,
        device=device,
    )

    steps_always = results_fine_always.get("steps_to_30pct")
    steps_gated = results_fine_gated.get("steps_to_30pct")

    if steps_always and steps_gated:
        efficiency_ratio = (steps_always - steps_gated) / steps_always
    else:
        efficiency_ratio = None

    combined_results = {
        "fine_always": results_fine_always,
        "fine_gated": results_fine_gated,
        "comparison": {
            "steps_fine_always": steps_always,
            "steps_fine_gated": steps_gated,
            "efficiency_ratio": efficiency_ratio,
            "gated_faster": steps_gated < steps_always if steps_always and steps_gated else None,
            "threshold_met": efficiency_ratio > 0.10 if efficiency_ratio else False,
        }
    }

    with open(f"{args.out_dir}/experiment_results.json", "w") as f:
        json.dump(combined_results, f, indent=2)

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Steps to 30% (fine_always): {steps_always}")
    print(f"Steps to 30% (fine_gated): {steps_gated}")
    print(f"Efficiency ratio: {efficiency_ratio}")
    print(f"Threshold met (>10% improvement): {combined_results['comparison']['threshold_met']}")

    return combined_results


if __name__ == "__main__":
    main()
