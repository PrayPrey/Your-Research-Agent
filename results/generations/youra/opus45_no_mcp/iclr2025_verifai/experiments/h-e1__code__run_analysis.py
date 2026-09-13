"""A-6: Full pipeline orchestration (parallelized)."""
import json
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from generate import load_problems, generate_code, get_benchmark
from static_analysis import run_static_analysis
from exec_analysis import run_execution_tests
from jaccard import compute_jaccard, categorize
from evaluate import evaluate_gate
from visualize import generate_all_figures

def process_one(args):
    """Process single problem (for multiprocessing)."""
    pid, problem = args
    code = generate_code(problem, pid)
    static_errors = run_static_analysis(code)
    exec_errors = run_execution_tests(pid, code, problem, timeout=5)
    jac = compute_jaccard(static_errors, exec_errors)
    cat = categorize(static_errors, exec_errors)
    return {
        "problem_id": pid,
        "benchmark": get_benchmark(pid),
        "static_errors": list(static_errors),
        "exec_errors": list(exec_errors),
        "jaccard": jac,
        "category": cat
    }

def main():
    print("H-E1: Error Orthogonality Analysis")
    print("=" * 50)
    sys.stdout.flush()

    Path(CONFIG.output_dir).mkdir(parents=True, exist_ok=True)

    print("Loading problems...")
    sys.stdout.flush()
    problems = load_problems()
    print(f"Loaded {len(problems)} problems")
    sys.stdout.flush()

    results = {
        "per_problem": [],
        "jaccard_scores": [],
        "static_only": 0,
        "exec_only": 0,
        "both": 0,
        "neither": 0,
        "total_problems": len(problems),
    }

    workers = min(8, os.cpu_count() or 4)
    print(f"Processing with {workers} workers...")
    sys.stdout.flush()

    items = list(problems.items())
    completed = 0

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process_one, item): item[0] for item in items}
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0:
                print(f"Processed {completed}/{len(problems)}")
                sys.stdout.flush()
            try:
                r = future.result()
                results["per_problem"].append(r)
                results["jaccard_scores"].append(r["jaccard"])
                cat = r["category"]
                if cat == "static_only":
                    results["static_only"] += 1
                elif cat == "exec_only":
                    results["exec_only"] += 1
                elif cat == "both":
                    results["both"] += 1
                else:
                    results["neither"] += 1
            except Exception as e:
                print(f"Error: {e}")

    results["mean_jaccard"] = sum(results["jaccard_scores"]) / len(results["jaccard_scores"]) if results["jaccard_scores"] else 0.0
    non_overlap = results["static_only"] + results["exec_only"]
    results["non_overlapping_pct"] = non_overlap / len(problems) if problems else 0.0

    gate_passed, gate_msg = evaluate_gate(results)
    results["gate_passed"] = gate_passed
    results["gate_message"] = gate_msg

    results_path = Path(CONFIG.results_file)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_path}")

    print("Generating figures...")
    generate_all_figures(results, CONFIG.figures_dir)

    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total problems: {results['total_problems']}")
    print(f"Mean Jaccard: {results['mean_jaccard']:.4f}")
    print(f"Non-overlapping: {results['non_overlapping_pct']:.1%}")
    print(f"Categories: static_only={results['static_only']}, exec_only={results['exec_only']}, both={results['both']}, neither={results['neither']}")
    print(f"\nGATE: {results['gate_message']}")
    print(f"Gate Passed: {results['gate_passed']}")
    sys.stdout.flush()

    return results

if __name__ == "__main__":
    results = main()
