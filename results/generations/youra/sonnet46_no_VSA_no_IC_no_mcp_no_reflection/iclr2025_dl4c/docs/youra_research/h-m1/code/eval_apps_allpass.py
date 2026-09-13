import os
import random
import sys
from dataclasses import dataclass
from typing import List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.append(os.path.join(_THIS_DIR, "../../h-e1/code"))
from rewards import execute_code
from evaluate import generate_completion
from data import format_prompt


def stratify_apps_val(dataset, n: int = 500, difficulty_key: str = "difficulty"):
    """Sample n problems stratified by difficulty from APPS validation split."""
    difficulty_groups = {}
    for ex in dataset:
        d = ex.get(difficulty_key, "unknown")
        difficulty_groups.setdefault(d, []).append(ex)

    total = len(dataset)
    sampled = []
    for d, group in difficulty_groups.items():
        proportion = len(group) / total
        k = max(1, round(proportion * n))
        sampled.extend(random.sample(group, min(k, len(group))))

    # Trim to exactly n
    random.shuffle(sampled)
    return sampled[:n]


@dataclass
class AppsAllPassResult:
    allpass_fraction: float
    per_problem_rates: List[float]
    n_problems: int


def evaluate_apps_allpass(
    checkpoint_path: str,
    model_name: str,
    apps_val_dataset: list,
    sandbox_timeout: float = 3.0,
) -> AppsAllPassResult:
    """Evaluate checkpoint on APPS validation all-pass rate."""
    import json

    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading checkpoint: {checkpoint_path}")
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    per_problem_rates = []
    for i, problem in enumerate(apps_val_dataset):
        # Parse test cases from APPS format
        try:
            inputs_raw = problem.get("input_output", "{}")
            if isinstance(inputs_raw, str):
                io_data = json.loads(inputs_raw)
            else:
                io_data = inputs_raw or {}
            inputs_list = io_data.get("inputs", [])
            outputs_list = io_data.get("outputs", [])
            test_cases = [
                {"input": str(inp), "output": str(out)}
                for inp, out in zip(inputs_list, outputs_list)
            ]
        except Exception:
            test_cases = []

        if not test_cases:
            per_problem_rates.append(0.0)
            continue

        question = problem.get("question", "")
        prompt = format_prompt(question, tokenizer, max_tokens=512)
        completion = generate_completion(model, tokenizer, prompt, max_new_tokens=512)

        k = sum(
            execute_code(completion, tc["input"], tc["output"], int(sandbox_timeout))
            for tc in test_cases
        )
        n = len(test_cases)
        rate = k / n if n > 0 else 0.0
        per_problem_rates.append(rate)

        if (i + 1) % 50 == 0:
            allpass_so_far = sum(r == 1.0 for r in per_problem_rates) / len(per_problem_rates)
            print(f"  [{i+1}/{len(apps_val_dataset)}] allpass so far: {allpass_so_far:.3f}")

    del model
    torch.cuda.empty_cache()

    allpass_fraction = sum(r == 1.0 for r in per_problem_rates) / len(per_problem_rates)
    return AppsAllPassResult(
        allpass_fraction=allpass_fraction,
        per_problem_rates=per_problem_rates,
        n_problems=len(per_problem_rates),
    )
