"""H-M2: Main analysis pipeline - Behavioral error detection in static-clean code."""
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from config import CONFIG
from generate import load_problems, get_benchmark, generate_code
from static_analysis import run_static_analysis
from exec_analysis import run_execution_tests
from behavioral_errors import is_static_clean, categorize_test_failure
from behavioral_coverage import compute_behavioral_rate, failure_category_distribution, per_benchmark_breakdown
from evaluate import evaluate_gate
from visualize import generate_all_figures


def process_one(args: tuple) -> dict:
    """Process single problem: static analysis + test execution."""
    pid, problem = args

    code = generate_code(problem, pid, seed=CONFIG.seed)
    static_errors = run_static_analysis(code)

    is_clean = is_static_clean(static_errors)

    exec_errors = set()
    has_failure = False
    category = None

    if is_clean:
        exec_errors = run_execution_tests(pid, code, problem, timeout=CONFIG.exec_timeout_sec)
        has_failure = len(exec_errors) > 0
        category = categorize_test_failure(exec_errors) if has_failure else None

    return {
        "problem_id": pid,
        "benchmark": get_benchmark(pid),
        "static_errors": list(static_errors),
        "exec_errors": list(exec_errors),
        "is_static_clean": is_clean,
        "has_behavioral_failure": has_failure,
        "failure_category": category
    }


def main() -> dict:
    """Run full H-M2 analysis pipeline."""
    print("Loading 563 problems (HumanEval+ + MBPP+)...")
    problems = load_problems()
    print(f"Loaded {len(problems)} problems")

    os.makedirs(CONFIG.output_dir, exist_ok=True)

    print("Processing problems with static analysis + test execution...")
    results = []
    max_workers = min(8, os.cpu_count() or 4)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, (pid, p)): pid for pid, p in problems.items()}
        completed = 0
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                completed += 1
                if completed % 100 == 0:
                    print(f"  Processed {completed}/{len(problems)}")
            except Exception as e:
                pid = futures[future]
                print(f"  Error processing {pid}: {e}")

    print(f"Completed {len(results)} problems")

    # Compute metrics
    metrics = compute_behavioral_rate(results)
    category_dist = failure_category_distribution(results)
    benchmark_breakdown = per_benchmark_breakdown(results)
    gate_result = evaluate_gate(metrics["behavioral_rate"], CONFIG.behavioral_gate)

    print(f"\n=== H-M2 Results ===")
    print(f"Static-clean problems: {metrics['static_clean_count']}")
    print(f"Behavioral failures: {metrics['behavioral_failures']}")
    print(f"Behavioral rate: {metrics['behavioral_rate']:.1%}")
    print(f"Gate: {'PASS' if gate_result['passed'] else 'FAIL'} ({gate_result['message']})")
    print(f"\nCategory distribution: {category_dist}")
    print(f"HumanEval+: {benchmark_breakdown['humaneval_plus']['behavioral_rate']:.1%}")
    print(f"MBPP+: {benchmark_breakdown['mbpp_plus']['behavioral_rate']:.1%}")

    output = {
        "metrics": metrics,
        "gate_result": gate_result,
        "category_distribution": category_dist,
        "per_benchmark": benchmark_breakdown,
        "per_problem": results
    }

    # Save results
    with open(CONFIG.results_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {CONFIG.results_file}")

    # Generate figures
    generate_all_figures(output, CONFIG.figures_dir)

    return output


if __name__ == "__main__":
    main()
