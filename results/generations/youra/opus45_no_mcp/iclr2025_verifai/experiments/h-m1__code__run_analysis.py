"""H-M1: Main analysis pipeline for structural error detection."""
import sys
import os
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
from config import CONFIG
from generate import load_problems, generate_code, get_benchmark
from static_analysis import run_static_analysis
from exec_analysis import run_execution_tests
from structural_errors import categorize_static_errors, has_structural_error, STRUCTURAL_ERROR_CODES
from coverage import compute_structural_coverage, error_category_distribution, per_benchmark_breakdown
from evaluate import evaluate_gate
from visualize import generate_all_figures

def process_one(args: tuple) -> dict:
    """Process single problem: generate code, run analysis, categorize errors."""
    pid, problem = args
    try:
        code = generate_code(problem, pid, seed=CONFIG.seed)
        static_errors = run_static_analysis(code)
        exec_errors = run_execution_tests(pid, code, problem, timeout=CONFIG.exec_timeout_sec)
        structural, other = categorize_static_errors(static_errors)

        return {
            "problem_id": pid,
            "benchmark": get_benchmark(pid),
            "static_errors": list(static_errors),
            "exec_errors": list(exec_errors),
            "structural": structural,
            "other": other,
            "has_structural": len(structural) > 0,
        }
    except Exception as e:
        return {
            "problem_id": pid,
            "benchmark": get_benchmark(pid),
            "static_errors": [],
            "exec_errors": ["exec:error"],
            "structural": [],
            "other": [],
            "has_structural": False,
            "error": str(e),
        }

def verify_mechanism(per_problem: list, dist: dict) -> bool:
    """Verify H-M1 mechanism: structural errors detected + categories valid."""
    total_structural = sum(len(r.get("structural", [])) for r in per_problem)
    assert total_structural > 0, "No structural errors detected - mechanism not working"

    valid_categories = set(STRUCTURAL_ERROR_CODES.values())
    for r in per_problem[:10]:
        for code, category in r.get("structural", []):
            assert category in valid_categories, f"Unknown category {category}"

    print(f"✓ Mechanism verified: {total_structural} structural errors categorized")
    return True

def main() -> dict:
    """Run H-M1 structural error analysis on 563 problems."""
    print("Loading problems...")
    problems = load_problems()
    print(f"Loaded {len(problems)} problems")

    workers = min(8, os.cpu_count() or 4)
    per_problem = []

    print(f"Processing with {workers} workers...")
    with ProcessPoolExecutor(workers) as pool:
        futures = {pool.submit(process_one, item): item[0] for item in problems.items()}
        done = 0
        for f in as_completed(futures):
            result = f.result()
            per_problem.append(result)
            done += 1
            if done % 100 == 0:
                print(f"Progress: {done}/{len(problems)}")

    print("Computing metrics...")
    cov = compute_structural_coverage(per_problem)
    dist = error_category_distribution(per_problem)
    breakdown = per_benchmark_breakdown(per_problem)
    gate = evaluate_gate(cov["structural_coverage"], CONFIG.structural_gate)

    verify_mechanism(per_problem, dist)

    results = {
        "per_problem": per_problem,
        "coverage": cov,
        "category_distribution": dist,
        "per_benchmark": breakdown,
        "gate": gate,
        "total_problems": len(problems),
    }

    # Save results
    output_dir = Path(__file__).parent / CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_dir}/results.json")

    # Generate figures
    figures_dir = Path(__file__).parent / CONFIG.figures_dir
    generate_all_figures(results, str(figures_dir))

    # Print summary
    print("\n" + "="*60)
    print("H-M1 Results Summary")
    print("="*60)
    print(f"Total problems: {len(problems)}")
    print(f"Test-failing problems: {cov['n_failing']}")
    print(f"With structural errors: {cov['n_structural']}")
    print(f"Structural coverage: {cov['structural_coverage']:.1%}")
    print(f"Gate threshold: >{CONFIG.structural_gate:.0%}")
    print(f"Gate result: {'PASS' if gate['passed'] else 'FAIL'}")
    print("="*60)

    return results

if __name__ == "__main__":
    main()
