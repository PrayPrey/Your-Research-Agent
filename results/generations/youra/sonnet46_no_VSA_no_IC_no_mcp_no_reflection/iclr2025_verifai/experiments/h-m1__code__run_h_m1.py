"""H-M1: Bug-type distribution of GPT-4o-mini failures on HumanEval+MBPP."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_problems
from src.generate import generate_solutions
from src.execute import execute_solution
from src.classify import classify_bug_type
from src.evaluate import compute_distribution, spot_check_agreement
from src.visualize import plot_bug_distribution, plot_stacked_bar, plot_spot_check

RESULTS_DIR = "results/h-m1"
FIGURES_DIR = "figures"
HE1_COMPLETIONS = os.path.join(
    os.path.dirname(__file__),
    "../../h-e1/code/results/completions.jsonl"
)
COMPLETIONS_PATH = os.path.join(RESULTS_DIR, "completions.jsonl")
RESULTS_PATH = os.path.join(RESULTS_DIR, "results.jsonl")
SUMMARY_PATH = os.path.join(RESULTS_DIR, "summary.json")
SPOT_CHECK_PATH = os.path.join(RESULTS_DIR, "spot_check.json")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # E1-T2: Load problems
    print("\n=== Loading problems ===")
    problems = load_problems()
    print(f"Total problems: {len(problems)}")

    # E2-T1/T2: Generate solutions (reuse h-e1 HumanEval completions)
    print("\n=== Generating solutions ===")
    completions = generate_solutions(
        problems,
        checkpoint_path=COMPLETIONS_PATH,
        he1_completions_path=HE1_COMPLETIONS,
    )

    # E2-T3 + E3-T1/T2: Execute and classify
    print("\n=== Executing and classifying ===")
    records = []

    # Load existing results
    existing_ids = set()
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    records.append(r)
                    existing_ids.add(r["id"])
        print(f"✓ Loaded {len(records)} existing results")

    with open(RESULTS_PATH, "a") as out:
        for i, problem in enumerate(problems):
            pid = problem.problem_id
            if pid in existing_ids:
                continue

            code = completions.get(pid, "")
            exec_result = execute_solution(code, problem)
            bug_type = classify_bug_type(exec_result.get("code", code), exec_result) if not exec_result["passed"] else "passed"

            record = {
                "id": pid,
                "source": problem.source,
                "passed": exec_result["passed"],
                "bug_type": bug_type if not exec_result["passed"] else None,
                "error": exec_result.get("error"),
                "error_type": exec_result.get("error_type"),
            }
            records.append(record)
            out.write(json.dumps(record) + "\n")
            out.flush()

            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(problems)}] processed...")

    print(f"✓ Total records: {len(records)}")

    # E4-T1: Compute distribution
    print("\n=== Computing distribution ===")
    summary = compute_distribution(records)
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n--- Distribution Summary ---")
    print(f"Total problems:  {summary['n_total']}")
    print(f"Passed:          {summary['n_passed']} ({summary['pass_rate']:.1%})")
    print(f"Failed:          {summary['n_failures']}")
    print(f"  type_error:    {summary['type_error']:.1%} (n={summary['counts'].get('type_error', 0)})")
    print(f"  runtime_error: {summary['runtime_error']:.1%} (n={summary['counts'].get('runtime_error', 0)})")
    print(f"  logic_error:   {summary['logic_error']:.1%} (n={summary['counts'].get('logic_error', 0)})")
    print(f"Max fraction:    {summary['max_fraction']:.1%}")
    print(f"Mixed (<80%):    {summary['mixed_distribution']}")

    # E3-T3: Spot-check
    print("\n=== Spot-check (n=50) ===")
    spot = spot_check_agreement(records, n=50)
    with open(SPOT_CHECK_PATH, "w") as f:
        json.dump({k: v for k, v in spot.items() if k != "details"}, f, indent=2)
    print(f"Agreement rate:  {spot['agreement_rate']:.1%} (passed: {spot['passed']})")

    # E4-T2/T3: Figures
    print("\n=== Generating figures ===")
    plot_bug_distribution(summary, FIGURES_DIR)
    plot_stacked_bar(summary, FIGURES_DIR)
    plot_spot_check(spot, FIGURES_DIR)

    # Gate check
    gate_passed = summary["mixed_distribution"] and spot["passed"]
    print(f"\n=== Gate Result ===")
    print(f"Mixed distribution: {summary['mixed_distribution']} (max={summary['max_fraction']:.1%} < 80%)")
    print(f"Classifier agreement: {spot['agreement_rate']:.1%} >= 70%: {spot['passed']}")
    print(f"GATE: {'PASS' if gate_passed else 'FAIL'}")

    return gate_passed, summary, spot


if __name__ == "__main__":
    main()
