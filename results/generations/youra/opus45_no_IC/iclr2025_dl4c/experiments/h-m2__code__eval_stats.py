"""Evaluation and statistical testing for H-M2 experiment."""

import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional
from scipy import stats
import numpy as np


def execute_code_with_tests(code: str, tests: str, timeout: float = 5.0) -> bool:
    """Execute code with test cases in isolated subprocess."""
    full_code = code + "\n" + tests

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(full_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ['python', temp_path],
            capture_output=True,
            timeout=timeout,
            text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


def pass_at_k(n: int, c: int, k: int = 1) -> float:
    """Compute pass@k metric."""
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def evaluate_model_pass_at_1(
    model,
    tokenizer,
    problems: List[Dict],
    num_samples: int = 1,
    max_new_tokens: int = 256
) -> Dict[str, Any]:
    """
    Evaluate model on pass@1 metric.

    Args:
        model: Policy model
        tokenizer: Tokenizer
        problems: List of problems with 'prompt' and 'test' keys
        num_samples: Samples per problem
        max_new_tokens: Max generation length

    Returns:
        Evaluation results
    """
    results = []
    passed = 0
    total = 0

    for problem in problems:
        prompt = problem.get("prompt", "")
        tests = problem.get("test", "")
        if isinstance(tests, list):
            tests = "\n".join(tests)

        input_ids = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).input_ids
        input_ids = input_ids.to(model.pretrained_model.device)

        sample_passed = 0
        for _ in range(num_samples):
            try:
                output = model.generate(
                    input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.8,
                    pad_token_id=tokenizer.pad_token_id,
                )
                generated = tokenizer.decode(output[0, input_ids.shape[1]:], skip_special_tokens=True)

                if execute_code_with_tests(generated, tests):
                    sample_passed += 1
            except Exception:
                pass

        p1 = pass_at_k(num_samples, sample_passed, k=1)
        results.append({
            "id": problem.get("id", f"problem_{total}"),
            "passed": sample_passed,
            "total": num_samples,
            "pass_at_1": p1
        })

        passed += sample_passed
        total += num_samples

    overall_pass_at_1 = sum(r["pass_at_1"] for r in results) / len(results) if results else 0.0

    return {
        "num_problems": len(problems),
        "num_samples": num_samples,
        "overall_pass_at_1": overall_pass_at_1,
        "total_passed": passed,
        "total_samples": total,
        "per_problem": results
    }


def paired_ttest_conditions(
    trace_scores: List[float],
    random_scores: List[float]
) -> Dict[str, Any]:
    """
    Paired t-test comparing trace vs random masking.

    Args:
        trace_scores: pass@1 scores for trace condition across seeds
        random_scores: pass@1 scores for random condition across seeds

    Returns:
        Dict with t-stat, p-value, and significance
    """
    if len(trace_scores) != len(random_scores):
        raise ValueError("Score lists must have same length")

    if len(trace_scores) < 2:
        return {
            "t_stat": float("nan"),
            "p_value": 1.0,
            "significant": False,
            "error": "Need at least 2 samples for t-test"
        }

    t_stat, p_value = stats.ttest_rel(trace_scores, random_scores)

    # One-sided test: trace > random
    p_one_sided = p_value / 2 if t_stat > 0 else 1 - p_value / 2

    return {
        "t_stat": float(t_stat),
        "p_value_two_sided": float(p_value),
        "p_value_one_sided": float(p_one_sided),
        "significant": p_one_sided < 0.05,
        "trace_mean": float(np.mean(trace_scores)),
        "random_mean": float(np.mean(random_scores)),
        "trace_std": float(np.std(trace_scores)),
        "random_std": float(np.std(random_scores)),
        "improvement": float(np.mean(trace_scores) - np.mean(random_scores))
    }


def compute_gate_verdict(
    experiment_results: Dict[str, Any],
    eval_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute MUST_WORK gate verdict for H-M2.

    Gate conditions:
    1. Trace-based > Random-based pass@1 (p < 0.05)
    2. Gradient exclusion verified (masked tokens have zero gradient)

    Args:
        experiment_results: Training results with gradient verification
        eval_results: Evaluation results with pass@1 scores

    Returns:
        Gate verdict dict
    """
    # Extract pass@1 scores per seed
    trace_scores = []
    random_scores = []
    none_scores = []

    for mode in ["none", "random", "trace"]:
        if mode in eval_results:
            scores = [r["pass_at_1"] for r in eval_results[mode]]
            if mode == "trace":
                trace_scores = scores
            elif mode == "random":
                random_scores = scores
            elif mode == "none":
                none_scores = scores

    # Statistical test
    if trace_scores and random_scores:
        stat_test = paired_ttest_conditions(trace_scores, random_scores)
        trace_better = stat_test["significant"] and stat_test["improvement"] > 0
    else:
        stat_test = {"error": "Missing scores"}
        trace_better = False

    # Gradient verification
    grad_verified = True
    grad_checks = []

    if "results_by_condition" in experiment_results:
        for condition_results in experiment_results["results_by_condition"].get("trace", []):
            for gv in condition_results.get("grad_verification", []):
                grad_checks.append(gv)
                if not gv.get("verified", False):
                    grad_verified = False

    # Overall gate
    gate_pass = trace_better and grad_verified

    return {
        "gate_type": "MUST_WORK",
        "gate_pass": gate_pass,
        "conditions": {
            "trace_better_than_random": {
                "pass": trace_better,
                "details": stat_test
            },
            "gradient_exclusion_verified": {
                "pass": grad_verified,
                "num_checks": len(grad_checks),
                "all_verified": grad_verified
            }
        },
        "summary": {
            "none_mean": float(np.mean(none_scores)) if none_scores else None,
            "random_mean": float(np.mean(random_scores)) if random_scores else None,
            "trace_mean": float(np.mean(trace_scores)) if trace_scores else None,
        },
        "verdict": "PASS" if gate_pass else "FAIL"
    }
