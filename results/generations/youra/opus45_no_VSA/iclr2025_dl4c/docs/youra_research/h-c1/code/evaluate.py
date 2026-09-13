"""Evaluation for H-C1 experiment."""
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

        tests = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in base_input if len(t) >= 2]

        if tests:
            pass_rate, _ = execute_and_get_feedback(code, tests)
            if pass_rate == 1.0:
                passed += 1
            total += 1

    return passed / max(1, total)


def run_condition_eval(model, tokenizer, problems: dict[str, Any], inference_mode: str, cfg: Config) -> float:
    """Evaluate one condition, return pass@1."""
    samples = generate_samples(model, tokenizer, problems, inference_mode, cfg)
    return compute_pass_at_1(samples, problems)


def compute_interaction(refine_pass1: float, single_pass1: float) -> float:
    """Interaction = gain from refinement."""
    return refine_pass1 - single_pass1


def gate_check(interaction_high: float, interaction_low: float) -> bool:
    """Gate passes if high-diversity has stronger interaction than low-diversity."""
    return interaction_high > interaction_low


def save_results(results: dict, cfg: Config):
    """Save results to JSON and CSV."""
    output_file = cfg.outputs_dir / "results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    csv_file = cfg.outputs_dir / "results.csv"
    with open(csv_file, "w") as f:
        f.write("condition,pass_at_1,entropy,interaction\n")
        for cond, data in results.get("conditions", {}).items():
            f.write(f"{cond},{data['pass_at_1']:.6f},{data.get('entropy', 0):.3f},{data.get('interaction', 0):.6f}\n")

    return output_file
