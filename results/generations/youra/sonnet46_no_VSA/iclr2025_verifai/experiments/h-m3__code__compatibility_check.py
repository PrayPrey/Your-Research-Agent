"""Pre-experiment compatibility check for icontract-hypothesis filter rates."""
import random
import numpy as np
from experiment_b_runner import run_triple


def run_compatibility_precheck(
    tasks: dict,
    corpus: dict,
    n_tasks: int = 20,
    seed: int = 42,
    min_valid: int = 100,
    max_filter_rate: float = 0.95,
) -> dict:
    rng = random.Random(seed)
    sample_ids = rng.sample(list(tasks.keys()), min(n_tasks, len(tasks)))

    results = {}
    for task_id in sample_ids:
        llm_code = None
        for model_corpus in corpus.values():
            programs = model_corpus.get(task_id, [])
            if programs:
                llm_code = programs[0]
                break
        if llm_code is None:
            results[task_id] = {"filter_rate": 1.0, "n_valid": 0, "passed": False, "error": "no_program"}
            continue

        triple = run_triple(
            llm_code=llm_code,
            contracteval_task=tasks[task_id],
            task_id=task_id,
            model="precheck",
            program_idx=0,
            budget=500,
            timeout_secs=30,
        )
        passed = triple.n_valid >= min_valid and triple.filter_rate <= max_filter_rate
        results[task_id] = {
            "filter_rate": triple.filter_rate,
            "n_valid": triple.n_valid,
            "passed": passed,
            "error": triple.error,
        }
    return results


def check_precheck_gate(precheck_results: dict, min_passing: int = 15) -> tuple[bool, dict]:
    n_total = len(precheck_results)
    n_passed = sum(1 for r in precheck_results.values() if r["passed"])
    gate_passed = n_passed >= min_passing

    filter_rates = [r["filter_rate"] for r in precheck_results.values()]
    summary = {
        "n_total": n_total,
        "n_passed": n_passed,
        "n_failed": n_total - n_passed,
        "gate_passed": gate_passed,
        "failed_tasks": [tid for tid, r in precheck_results.items() if not r["passed"]],
        "mean_filter_rate": float(np.mean(filter_rates)) if filter_rates else 0.0,
    }
    return gate_passed, summary
