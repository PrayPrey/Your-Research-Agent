"""EvalPlus correctness evaluation for H-E1."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

from evalplus.data import get_human_eval_plus, get_mbpp_plus
from evalplus.evaluate import evaluate

EVALPLUS_PARAMS = dict(
    max_as_limit=30,
    max_data_limit=30,
    max_stack_limit=10,
    min_time_limit=1,
    gt_time_limit_factor=4.0,
)

COVERAGE_MIN = 0.95
N_SMOKE = 5

MODEL_SHORT_NAMES = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}


def load_problems(benchmark: str) -> dict:
    """Load problem dict for given benchmark.
    benchmark: "humaneval" | "mbpp"
    Returns: problem dict
    """
    if benchmark == "humaneval":
        return get_human_eval_plus()
    elif benchmark == "mbpp":
        return get_mbpp_plus()
    else:
        raise ValueError(f"Unknown benchmark: {benchmark}")


def compute_coverage_rate(
    evaluated_ids: set,
    total_ids: set,
) -> float:
    """Compute fraction of total_ids that were successfully evaluated.
    Returns: float in [0.0, 1.0]  # target >= 0.95
    """
    if not total_ids:
        return 0.0
    return len(evaluated_ids & total_ids) / len(total_ids)


def save_correctness(correctness: dict, output_path: str) -> None:
    """Save {task_id: [bool × k]} as JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(correctness, f)


def solutions_to_evalplus_jsonl(solutions: dict, problems_he: dict, problems_mbpp: dict) -> str:
    """Convert solutions dict to EvalPlus JSONL format.
    solutions: {task_id: [str × k]}
    Returns: temp JSONL file path
    """
    tmpfile = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for task_id, sol_list in solutions.items():
        # Use the first solution or all k solutions
        for sol in sol_list:
            # Get the prompt for this task
            if task_id in problems_he:
                prompt = problems_he[task_id].get("prompt", "")
            elif task_id in problems_mbpp:
                prompt = problems_mbpp[task_id].get("prompt", "")
            else:
                prompt = ""
            # solution = prompt + completion
            tmpfile.write(json.dumps({"task_id": task_id, "solution": prompt + sol}) + "\n")
    tmpfile.close()
    return tmpfile.name


def evaluate_all_solutions(
    solutions: dict,
    problems_he: dict,
    problems_mbpp: dict,
    output_dir: str,
    model_short: str = "model",
) -> dict:
    """Evaluate all k solutions for all tasks using evalplus evaluate().
    solutions: {task_id: [str × k]}
    Returns: {task_id: [bool × k]}
    """
    os.makedirs(output_dir, exist_ok=True)

    # Separate solutions by benchmark
    he_solutions = {tid: sols for tid, sols in solutions.items() if tid in problems_he}
    mbpp_solutions = {tid: sols for tid, sols in solutions.items() if tid in problems_mbpp}

    correctness: dict[str, list[bool]] = {}

    for benchmark, bench_solutions, problems in [
        ("humaneval", he_solutions, problems_he),
        ("mbpp", mbpp_solutions, problems_mbpp),
    ]:
        if not bench_solutions:
            continue

        # Write evalplus-format JSONL: one entry per (task_id, solution_index)
        # EvalPlus expects {"task_id": ..., "solution": prompt + completion}
        jsonl_path = os.path.join(output_dir, f"solutions_{model_short}_{benchmark}_tmp.jsonl")
        with open(jsonl_path, "w") as f:
            for task_id, sol_list in bench_solutions.items():
                prompt = problems[task_id].get("prompt", "")
                for sol in sol_list:
                    f.write(json.dumps({"task_id": task_id, "solution": prompt + sol}) + "\n")

        # Run evalplus evaluate
        print(f"  Evaluating {len(bench_solutions)} {benchmark} problems...")
        result_file = jsonl_path.replace(".jsonl", "_eval_results.json")
        eval_results = evaluate(
            dataset=benchmark,
            samples=jsonl_path,
            min_time_limit=EVALPLUS_PARAMS["min_time_limit"],
            gt_time_limit_factor=EVALPLUS_PARAMS["gt_time_limit_factor"],
            parallel=4,
        )

        # evaluate() returns None when loading from cached results file
        # In that case, read directly from the _eval_results.json file
        if eval_results is None and os.path.exists(result_file):
            with open(result_file) as rf:
                eval_results = json.load(rf)

        # Parse results: eval_results["eval"] = {task_id: [{status, ...}]}
        if eval_results and "eval" in eval_results:
            for task_id, task_results in eval_results["eval"].items():
                correctness[task_id] = []
                for res in task_results:
                    if isinstance(res, dict):
                        base_ok = res.get("base_status", "fail") == "pass"
                        plus_ok = res.get("plus_status", "fail") == "pass"
                        passed = base_ok and plus_ok
                    elif isinstance(res, (list, tuple)) and len(res) >= 2:
                        base_ok = res[0][0] == "pass" if res[0] else False
                        plus_ok = res[1][0] == "pass" if res[1] else False
                        passed = base_ok and plus_ok
                    else:
                        passed = False
                    correctness[task_id].append(passed)

        # Cleanup tmp file
        try:
            os.remove(jsonl_path)
            if os.path.exists(result_file):
                os.remove(result_file)
        except Exception:
            pass

    return correctness


def load_solutions_jsonl(path: str) -> dict:
    """Load solutions JSONL {task_id: [str × k]}."""
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                result[obj["task_id"]] = obj["solutions"]
    return result


def main(args=None) -> None:
    """Entry point: evaluate solutions for one model."""
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate EvalPlus solutions")
    parser.add_argument("--solutions_path", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="results")
    parser.add_argument("--smoke_test", action="store_true")
    if args is None:
        args = parser.parse_args()

    solutions = load_solutions_jsonl(args.solutions_path)
    if args.smoke_test:
        solutions = dict(list(solutions.items())[:N_SMOKE])

    problems_he = load_problems("humaneval")
    problems_mbpp = load_problems("mbpp")

    model_short = os.path.basename(args.solutions_path).replace("solutions_", "").replace(".jsonl", "")
    output_path = os.path.join(args.output_dir, f"correctness_{model_short}.json")

    correctness = evaluate_all_solutions(solutions, problems_he, problems_mbpp, args.output_dir, model_short)

    # Compute coverage
    all_ids = set(problems_he.keys()) | set(problems_mbpp.keys())
    coverage_rate = compute_coverage_rate(set(correctness.keys()), all_ids)
    print(f"Coverage rate: {coverage_rate:.4f} ({len(correctness)}/{len(all_ids)})")

    if coverage_rate < COVERAGE_MIN:
        print(f"WARNING: Coverage {coverage_rate:.4f} < {COVERAGE_MIN}")

    save_correctness(correctness, output_path)
    print(f"Saved correctness to {output_path}")


if __name__ == "__main__":
    main()
