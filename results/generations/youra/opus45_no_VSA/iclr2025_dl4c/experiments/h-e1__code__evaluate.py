"""Evaluation for H-E1 experiment."""
import json
from pathlib import Path
from typing import Any, Callable

import torch
from tqdm import tqdm

from config import Config
from refine import single_shot, self_refine, execute_and_get_feedback


def generate_samples(
    model,
    tokenizer,
    problems: dict[str, Any],
    inference_fn: Callable,
    cfg: Config,
) -> dict[str, str]:
    """Generate code samples for all problems."""
    samples = {}
    device = next(model.parameters()).device
    model.eval()

    for task_id, problem in tqdm(problems.items(), desc="Generating"):
        prompt = problem["prompt"]
        entry_point = problem.get("entry_point", "solution")

        # Get test cases for refine mode
        base_input = problem.get("base_input", [])
        tests = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in base_input if len(t) >= 2]

        with torch.no_grad():
            if inference_fn == "single":
                code = single_shot(model, tokenizer, prompt, cfg)
            else:  # refine
                code = self_refine(model, tokenizer, prompt, tests, cfg)

        samples[task_id] = code

    return samples


def compute_pass_at_1(samples: dict[str, str], problems: dict[str, Any]) -> float:
    """Compute pass@1 by executing against test cases."""
    passed = 0
    total = 0

    for task_id, code in samples.items():
        if task_id not in problems:
            continue

        problem = problems[task_id]
        entry_point = problem.get("entry_point", "solution")
        base_input = problem.get("base_input", [])

        # Format tests
        tests = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in base_input if len(t) >= 2]

        if tests:
            pass_rate, _ = execute_and_get_feedback(code, tests)
            if pass_rate == 1.0:
                passed += 1
            total += 1

    return passed / max(1, total)


def run_2x2_eval(models: dict, problems: dict[str, Any], cfg: Config) -> dict[str, float]:
    """Run 2x2 factorial evaluation."""
    results = {}
    tokenizer = models["tokenizer"]

    conditions = [
        ("CE-Single", models["CE"], "single"),
        ("CE-Refine", models["CE"], "refine"),
        ("RL-Single", models["RL"], "single"),
        ("RL-Refine", models["RL"], "refine"),
    ]

    for name, model, inference_mode in conditions:
        print(f"\nEvaluating {name}...")
        samples = generate_samples(model, tokenizer, problems, inference_mode, cfg)
        pass_at_1 = compute_pass_at_1(samples, problems)
        results[name] = pass_at_1
        print(f"{name}: pass@1 = {pass_at_1:.4f}")

    return results


def interaction_effect(results: dict[str, float]) -> float:
    """Compute interaction effect: (RL-Refine - RL-Single) - (CE-Refine - CE-Single)."""
    rl_gain = results.get("RL-Refine", 0) - results.get("RL-Single", 0)
    ce_gain = results.get("CE-Refine", 0) - results.get("CE-Single", 0)
    return rl_gain - ce_gain


def save_results(results: dict[str, float], interaction: float, cfg: Config):
    """Save results to JSON file."""
    output = {
        "conditions": results,
        "interaction_effect": interaction,
        "pass_gate": interaction > 0,
    }

    output_file = cfg.outputs_dir / "results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    # Also save CSV for Phase 5
    csv_file = cfg.outputs_dir / "results.csv"
    with open(csv_file, "w") as f:
        f.write("condition,pass_at_1\n")
        for name, val in results.items():
            f.write(f"{name},{val:.6f}\n")

    return output_file
