"""H-M3 Experiment: Feedback-Guided Repair Loop — main entry point."""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add this code dir to path so 'src' imports work
_CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(_CODE_DIR))

import openai

from src.analyze import run_analysis
from src.load_h_m1 import load_failing_records
from src.repair_loop import RepairResult, run_repair_loop, verify_mechanism
from src.verifier_adapters import build_verifiers
from src.visualize import generate_all_figures
from src.write_results import write_records, write_summary

FIGURES_DIR = str(Path(__file__).parent.parent / "figures")
RESULTS_DIR = str(_CODE_DIR / "results" / "h-m3")
MAX_WORKERS = 4
MAX_ITERATIONS = 3
MODEL = "gpt-4o-mini"
REPAIR_TEMPERATURE = 0.0


def run_parallel_repair(
    failing_records: list,
    verifiers: dict,
    client,
    max_workers: int = MAX_WORKERS,
) -> list:
    """Run repair loop for all problems × all categories in parallel (problem-level)."""
    print(f"\nRunning repair loop: {len(failing_records)} problems × {len(verifiers)} categories")
    print(f"  Workers: {max_workers}, Max iterations: {MAX_ITERATIONS}")

    results = []
    total = len(failing_records)

    def repair_one_problem(record, idx):
        pid = record.get("task_id", "?")
        prob_results = []
        # Sequential per-category within each problem (controlled measurement)
        for cat, verifier in verifiers.items():
            r = run_repair_loop(
                problem=record,
                initial_solution=record["code"],
                verifier=verifier,
                model=MODEL,
                max_iterations=MAX_ITERATIONS,
                temperature=REPAIR_TEMPERATURE,
                client=client,
            )
            prob_results.append(r)
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{total} problems processed")
        return prob_results

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(repair_one_problem, rec, i): i
                   for i, rec in enumerate(failing_records)}
        for future in as_completed(futures):
            try:
                prob_results = future.result()
                results.extend(prob_results)
            except Exception as e:
                print(f"  Error in problem {futures[future]}: {e}")

    print(f"\nCompleted: {len(results)} (problem, category) repair sequences")
    return results


def print_gate_verdict(analysis: dict) -> None:
    rho = analysis["gate_rho"]
    gate_pass = analysis["gate_pass"]
    print("\n" + "="*60)
    print("H-M3 GATE VERDICT (SHOULD_WORK)")
    print("="*60)
    print(f"Spearman ρ (with Z3): {rho:.4f}")
    print(f"Gate condition: ρ > 0")
    print(f"Gate result: {'PASS ✓' if gate_pass else 'FAIL ✗'}")
    print()
    print("Per-category iter1 repair rates:")
    for cat, d in sorted(analysis["iter_rates"].items(), key=lambda x: x[1]["iter1_rate"], reverse=True):
        print(f"  {cat:12s}: {d['iter1_rate']:.3f}  (n={d['n']})")
    print("="*60)


def main():
    t0 = time.time()
    print("="*60)
    print("H-M3: Feedback-Guided Repair Loop Experiment")
    print("="*60)

    # Setup OpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    client = openai.OpenAI(api_key=api_key)

    # Step 1: Load H-M1 failing solutions
    print("\nStep 1: Loading H-M1 failing solutions...")
    failing_records = load_failing_records()
    if not failing_records:
        raise RuntimeError("No failing records found from H-M1")
    print(f"  Loaded {len(failing_records)} failing solutions")

    # Step 2: Build verifiers
    print("\nStep 2: Building verifier adapters...")
    verifiers = build_verifiers(client, model=MODEL)
    print(f"  Verifiers: {list(verifiers.keys())}")

    # Step 3: Mechanism verification (smoke test)
    print("\nStep 3: Mechanism verification...")
    verify_mechanism(failing_records[:3], verifiers, client)

    # Step 4: Parallel repair loop
    print("\nStep 4: Parallel repair loop...")
    results = run_parallel_repair(failing_records, verifiers, client)

    # Step 5: Statistical analysis
    print("\nStep 5: Statistical analysis...")
    analysis = run_analysis(results)

    # Step 6: Gate verdict
    print_gate_verdict(analysis)

    # Step 7: Visualization
    print("\nStep 7: Generating figures...")
    generate_all_figures(analysis["iter_rates"], results, FIGURES_DIR)

    # Step 8: Persist results
    print("\nStep 8: Persisting results...")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    write_records(results, os.path.join(RESULTS_DIR, "repair_records.jsonl"))
    write_summary(analysis, os.path.join(RESULTS_DIR, "summary.json"))

    elapsed = time.time() - t0
    print(f"\nExperiment complete in {elapsed:.1f}s")
    print(f"Gate: {'PASS' if analysis['gate_pass'] else 'FAIL'}, ρ={analysis['gate_rho']:.4f}")

    return analysis


if __name__ == "__main__":
    analysis = main()
    sys.exit(0 if analysis["gate_pass"] else 1)
