"""Dry-run integration test: 2 problems per benchmark, verify record shape and Spearman call."""

import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "code"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "h-e1/code"))

from openai import OpenAI
from pipeline import load_problems
from repair_loop import repair_loop_condition_b, run_mypy_with_output
from analysis import compute_mean_errors_per_round, compute_spearman, aggregate_results


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("OPENAI_API_KEY", "")
        except ImportError:
            pass
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    all_records = []
    for benchmark in ["mbpp+", "humaneval+"]:
        problems = load_problems(benchmark)
        items = list(problems.items())[:2]
        print(f"\n[{benchmark}] Testing {len(items)} problems...")
        for task_id, problem in items:
            records = repair_loop_condition_b(client, task_id, problem, benchmark, seed=42, k_max=3)
            print(f"  {task_id}: {len(records)} rounds")
            for r in records:
                assert "task_id" in r
                assert "benchmark" in r
                assert "round" in r
                assert "mypy_error_count" in r
                assert "exec_passed" in r
                assert "repaired" in r
            all_records.extend(records)

    print(f"\nTotal records: {len(all_records)}")

    # Test analysis
    for benchmark in ["mbpp+", "humaneval+"]:
        m = compute_mean_errors_per_round(all_records, benchmark, k_max=3)
        print(f"{benchmark} mean_errors: {m}")
        if len(m) >= 2:
            rho, pval = compute_spearman(m)
            print(f"  Spearman rho={rho:.3f} pval={pval:.3f}")

    summary = aggregate_results(all_records, k_max=3)
    print(f"\nSummary keys: {list(summary.keys())}")
    print("DRY RUN PASSED")


if __name__ == "__main__":
    main()
