"""Evaluation module for pass@1 and threshold tracking."""
import json
import torch
from typing import List, Dict, Tuple, Optional
from model import PPOPolicy
from reward import execute_code_safely
from data import get_tokenizer
from config import PASS_THRESHOLD


def compute_pass_at_1(
    policy: PPOPolicy,
    test_problems: List[Dict],
    device: str = "cuda",
    max_samples: int = None,
) -> float:
    """Compute pass@1 on test set via execution."""
    policy.eval()
    tokenizer = get_tokenizer()
    passed = 0
    total = 0

    problems = test_problems[:max_samples] if max_samples else test_problems

    with torch.no_grad():
        for item in problems:
            prompt = item.get("question", item.get("problem", ""))
            test_cases_str = item.get("input_output", "{}")

            try:
                tc_data = json.loads(test_cases_str) if isinstance(test_cases_str, str) else test_cases_str
                inputs = tc_data.get("inputs", [])
                outputs = tc_data.get("outputs", [])
                test_cases = [{"input": i, "output": o} for i, o in zip(inputs, outputs)]
            except:
                test_cases = []

            inputs = tokenizer(
                prompt,
                max_length=512,
                truncation=True,
                return_tensors="pt"
            ).to(device)

            gen_ids = policy.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                do_sample=False,
                max_new_tokens=256,
            )

            code = tokenizer.decode(gen_ids[0], skip_special_tokens=True)
            result, _ = execute_code_safely(code, test_cases)

            if result == "PASS":
                passed += 1
            total += 1

    policy.train()
    return passed / total if total > 0 else 0.0


def track_steps_to_threshold(
    pass_at_1_log: List[Tuple[int, float]],
    threshold: float = PASS_THRESHOLD,
) -> Optional[int]:
    """Find first step where pass@1 crosses threshold."""
    for step, p1 in pass_at_1_log:
        if p1 >= threshold:
            return step
    return None


def evaluate_checkpoint(
    policy: PPOPolicy,
    test_problems: List[Dict],
    step: int,
    out_dir: str,
    gating_stats: dict,
    device: str = "cuda",
    max_samples: int = 500,
):
    """Evaluate and save checkpoint metrics."""
    p1 = compute_pass_at_1(policy, test_problems, device, max_samples)

    metrics = {
        "step": step,
        "pass_at_1": p1,
        "gating_stats": gating_stats,
    }

    with open(f"{out_dir}/checkpoint_{step}.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return p1


def save_final_results(
    condition: str,
    pass_at_1_log: List[Tuple[int, float]],
    steps_to_threshold: Optional[int],
    gating_stats: dict,
    out_dir: str,
):
    """Save final evaluation results for a condition."""
    results = {
        "condition": condition,
        "pass_at_1_curve": pass_at_1_log,
        "steps_to_30pct": steps_to_threshold,
        "final_pass_at_1": pass_at_1_log[-1][1] if pass_at_1_log else 0.0,
        "gating_stats": gating_stats,
    }

    with open(f"{out_dir}/results_{condition}.json", "w") as f:
        json.dump(results, f, indent=2)

    return results
