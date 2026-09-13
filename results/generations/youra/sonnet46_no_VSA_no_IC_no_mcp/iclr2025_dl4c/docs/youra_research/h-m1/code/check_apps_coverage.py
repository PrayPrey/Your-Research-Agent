"""Task C: APPS competition-level coverage check via subprocess execution."""
import json
import subprocess
import tempfile
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm


def check_solution_passes(solution: str, test_cases: list, timeout: float = 5.0) -> bool:
    """Execute solution against all test cases in subprocess.
    Returns True iff ALL test cases pass. Returns False on any failure or timeout."""
    if not test_cases:
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(solution)
        tmp_path = f.name

    try:
        for tc in test_cases:
            try:
                proc = subprocess.run(
                    ["python", tmp_path],
                    input=tc.get("input", ""),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if proc.returncode != 0:
                    return False
                if proc.stdout.strip() != str(tc.get("output", "")).strip():
                    return False
            except subprocess.TimeoutExpired:
                return False
            except Exception:
                return False
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return True


def compute_coverage(
    dataset_name: str = "codeparrot/apps",
    difficulty: str = "competition",
    output_path: str = "results/h-m1/apps_hard_coverage.json",
    max_problems: int = None,
) -> dict:
    """Per-problem: solvable if ANY reference solution passes ALL test cases."""
    ds = load_dataset(dataset_name, split="train", trust_remote_code=True)
    problems = [ex for ex in ds if ex.get("difficulty") == difficulty]
    if max_problems:
        problems = problems[:max_problems]
    # ponytail: global cap via max_problems; full competition split ~600 problems is manageable

    solvable = 0
    for problem in tqdm(problems, desc=f"Checking {difficulty} coverage"):
        try:
            solns = json.loads(problem.get("solutions", "[]") or "[]")
        except (json.JSONDecodeError, TypeError):
            solns = []

        try:
            io_data = json.loads(problem.get("input_output", "{}") or "{}")
        except (json.JSONDecodeError, TypeError):
            io_data = {}

        inputs = io_data.get("inputs", [])
        outputs = io_data.get("outputs", [])
        test_cases = [{"input": i, "output": o} for i, o in zip(inputs, outputs)]

        if not solns or not test_cases:
            continue

        problem_solvable = False
        for soln in solns:
            if check_solution_passes(soln, test_cases):
                problem_solvable = True
                break
        if problem_solvable:
            solvable += 1

    total = len(problems)
    coverage_pct = round(solvable / total * 100, 2) if total > 0 else 0.0
    result = {
        "difficulty": difficulty,
        "total": total,
        "solvable": solvable,
        "coverage_pct": coverage_pct,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Coverage: {solvable}/{total} = {coverage_pct}%")
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/h-m1/apps_hard_coverage.json")
    parser.add_argument("--max_problems", type=int, default=None)
    args = parser.parse_args()

    result = compute_coverage(output_path=args.output, max_problems=args.max_problems)
    print(f"\nResult: {result}")
