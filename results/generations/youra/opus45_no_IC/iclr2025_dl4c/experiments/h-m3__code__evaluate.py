"""Evaluation: pass@k metrics on HumanEval and MBPP."""

import os
import json
import random
import numpy as np
import torch
from typing import Dict, List, Any, Optional
from collections import defaultdict
from transformers import AutoModelForCausalLM, AutoTokenizer

from data import load_humaneval, load_mbpp, format_prompt, get_test_cases
from execution import compute_reward, check_compiles


def generate_samples(
    model,
    tokenizer,
    problems: List[Dict],
    n: int = 10,
    max_new_tokens: int = 256,
    temperature: float = 0.8,
    dataset: str = "humaneval",
) -> List[Dict]:
    """
    Generate n code samples per problem.

    Args:
        model: Language model
        tokenizer: Tokenizer
        problems: List of problems
        n: Number of samples per problem
        max_new_tokens: Max generation length
        temperature: Sampling temperature
        dataset: Dataset name for prompt formatting

    Returns:
        List of {task_id, completions: [str]*n}
    """
    samples = []

    for problem in problems:
        prompt = format_prompt(problem, dataset)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        completions = []
        for _ in range(n):
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    pad_token_id=tokenizer.pad_token_id,
                )

            response = outputs[0, inputs["input_ids"].shape[1]:]
            code = tokenizer.decode(response, skip_special_tokens=True)
            completions.append(code)

        samples.append({
            "task_id": problem["task_id"],
            "completions": completions,
        })

    return samples


def pass_at_k(n: int, c: int, k: int) -> float:
    """
    Compute unbiased pass@k estimator.

    Args:
        n: Total samples
        c: Correct samples
        k: k value

    Returns:
        pass@k estimate
    """
    if n - c < k:
        return 1.0

    from math import comb
    return 1.0 - comb(n - c, k) / comb(n, k)


def evaluate_samples(
    samples: List[Dict],
    problems_dict: Dict[str, Dict],
    dataset: str = "humaneval",
) -> Dict[str, float]:
    """
    Evaluate generated samples.

    Args:
        samples: List of {task_id, completions}
        problems_dict: Dict mapping task_id to problem
        dataset: Dataset name

    Returns:
        Dict with pass@1 and pass@10
    """
    results = []

    for sample in samples:
        task_id = sample["task_id"]
        completions = sample["completions"]
        problem = problems_dict.get(task_id)

        if problem is None:
            continue

        test_cases = get_test_cases(problem, dataset)
        n = len(completions)
        c = 0

        for code in completions:
            reward = compute_reward(code, test_cases, "test")
            if reward == 1.0:
                c += 1

        results.append({
            "task_id": task_id,
            "n": n,
            "c": c,
            "pass@1": pass_at_k(n, c, 1),
            "pass@10": pass_at_k(n, c, min(10, n)),
        })

    avg_pass1 = np.mean([r["pass@1"] for r in results])
    avg_pass10 = np.mean([r["pass@10"] for r in results])

    return {
        "pass@1": avg_pass1,
        "pass@10": avg_pass10,
        "num_problems": len(results),
        "details": results,
    }


def evaluate_condition(
    model_path: str,
    dataset: str = "humaneval",
    n_samples: int = 10,
) -> Dict[str, Any]:
    """
    Evaluate a trained condition checkpoint.

    Args:
        model_path: Path to model checkpoint
        dataset: "humaneval" or "mbpp"
        n_samples: Number of samples per problem

    Returns:
        Evaluation results dict
    """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    if dataset == "humaneval":
        problems = load_humaneval()
    else:
        problems = load_mbpp()

    problems_dict = {p["task_id"]: p for p in problems}

    samples = generate_samples(
        model, tokenizer, problems, n=n_samples, dataset=dataset
    )

    results = evaluate_samples(samples, problems_dict, dataset)
    results["model_path"] = model_path
    results["dataset"] = dataset
    results["n_samples"] = n_samples

    return results


def evaluate_all_conditions(
    results_dir: str,
    output_path: Optional[str] = None,
) -> Dict[str, Dict]:
    """
    Evaluate all 6 conditions.

    Args:
        results_dir: Directory containing condition subdirectories
        output_path: Path to save evaluation results

    Returns:
        Dict mapping condition_name to evaluation results
    """
    from config import CONDITIONS

    all_results = {}

    for condition_name, use_fgo, feedback_type in CONDITIONS:
        model_path = os.path.join(results_dir, condition_name, "final")

        if not os.path.exists(model_path):
            print(f"Skipping {condition_name}: checkpoint not found")
            continue

        print(f"\nEvaluating {condition_name}...")

        humaneval_results = evaluate_condition(model_path, "humaneval")
        mbpp_results = evaluate_condition(model_path, "mbpp")

        all_results[condition_name] = {
            "use_fgo": use_fgo,
            "feedback_type": feedback_type,
            "humaneval": {
                "pass@1": humaneval_results["pass@1"],
                "pass@10": humaneval_results["pass@10"],
            },
            "mbpp": {
                "pass@1": mbpp_results["pass@1"],
                "pass@10": mbpp_results["pass@10"],
            },
        }

        print(f" HumanEval: pass@1={humaneval_results['pass@1']:.3f}")
        print(f" MBPP: pass@1={mbpp_results['pass@1']:.3f}")

    if output_path:
        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2)

    return all_results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "outputs"

    results = evaluate_all_conditions(
        results_dir,
        output_path=os.path.join(results_dir, "evaluation_results.json")
    )

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    for cond, res in results.items():
        print(f"{cond}: HE={res['humaneval']['pass@1']:.3f}, MBPP={res['mbpp']['pass@1']:.3f}")
