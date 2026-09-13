"""Main experiment runner for SpecBridge evaluation.

This script runs the complete experiment comparing:
1. Baseline: Direct LLM code generation
2. SpecBridge Static: Spec-guided generation without refinement
3. SpecBridge Dynamic: Spec-guided generation with counterexample refinement

Metrics evaluated:
- Pass@1: Percentage of problems solved on first attempt
- Verification Success Rate (VSR): Percentage passing all tests
- Specification Accuracy: Quality of generated specifications
- Ambiguity Detection: Precision/Recall of identifying ambiguous requirements
"""

import os
import sys
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import NUM_SAMPLES, NUM_SPEC_CANDIDATES, MAX_REFINEMENT_ITERATIONS, RESULTS_DIR, LOG_FILE
from data import get_benchmark_problems
from spec_inference import (
    generate_specification,
    generate_specification_ensemble,
    compute_disagreement_score,
    is_ambiguous,
    select_best_specification
)
from code_generation import (
    generate_code_baseline,
    generate_code_with_spec,
    refine_code_with_counterexample
)
from verification import verify_code_with_tests, VerificationResult

# Logging utility
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write(f"Experiment Log - {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")

def run_baseline(problems, logger):
    """Run baseline method: Direct LLM code generation."""
    logger.log("\n" + "=" * 60)
    logger.log("Running Baseline: Direct LLM Code Generation")
    logger.log("=" * 60)

    results = []
    for i, problem in enumerate(problems):
        logger.log(f"\nProblem {i+1}/{len(problems)}: {problem['name']}")

        start_time = time.time()

        # Generate code directly
        code = generate_code_baseline(problem['description'], problem['name'])

        # Verify
        success, passed, total, cex, error = verify_code_with_tests(
            code, problem['test_cases'], problem['name']
        )

        elapsed = time.time() - start_time

        result = {
            "problem_id": problem['id'],
            "problem_name": problem['name'],
            "difficulty": problem['difficulty'],
            "method": "baseline",
            "success": success,
            "passed": passed,
            "total": total,
            "pass_rate": passed / total if total > 0 else 0,
            "time": elapsed,
            "code": code,
            "error": error if not success else None
        }
        results.append(result)

        logger.log(f"  Result: {'PASS' if success else 'FAIL'} ({passed}/{total} tests)")

    return results

def run_specbridge_static(problems, logger):
    """Run SpecBridge Static: Spec-guided generation without refinement."""
    logger.log("\n" + "=" * 60)
    logger.log("Running SpecBridge Static: Spec-Guided Generation")
    logger.log("=" * 60)

    results = []
    spec_results = []

    for i, problem in enumerate(problems):
        logger.log(f"\nProblem {i+1}/{len(problems)}: {problem['name']}")

        start_time = time.time()

        # Generate specification
        spec = generate_specification(problem['description'])
        logger.log(f"  Spec: pre={spec['precondition'][:50]}...")

        # Generate code with specification
        code = generate_code_with_spec(problem['description'], spec, problem['name'])

        # Verify
        success, passed, total, cex, error = verify_code_with_tests(
            code, problem['test_cases'], problem['name']
        )

        elapsed = time.time() - start_time

        result = {
            "problem_id": problem['id'],
            "problem_name": problem['name'],
            "difficulty": problem['difficulty'],
            "method": "specbridge_static",
            "success": success,
            "passed": passed,
            "total": total,
            "pass_rate": passed / total if total > 0 else 0,
            "time": elapsed,
            "specification": spec,
            "code": code,
            "error": error if not success else None
        }
        results.append(result)

        spec_result = {
            "problem_id": problem['id'],
            "generated_spec": spec,
            "ground_truth_spec": problem['specification']
        }
        spec_results.append(spec_result)

        logger.log(f"  Result: {'PASS' if success else 'FAIL'} ({passed}/{total} tests)")

    return results, spec_results

def run_specbridge_dynamic(problems, logger):
    """Run SpecBridge Dynamic: Spec-guided generation with refinement."""
    logger.log("\n" + "=" * 60)
    logger.log("Running SpecBridge Dynamic: Spec-Guided with Refinement")
    logger.log("=" * 60)

    results = []
    ambiguity_results = []

    for i, problem in enumerate(problems):
        logger.log(f"\nProblem {i+1}/{len(problems)}: {problem['name']}")

        start_time = time.time()

        # Generate ensemble of specifications
        candidates = generate_specification_ensemble(problem['description'], NUM_SPEC_CANDIDATES)

        # Compute disagreement
        disagreement = compute_disagreement_score(candidates)
        is_ambig = is_ambiguous(candidates)

        ambiguity_results.append({
            "problem_id": problem['id'],
            "disagreement_score": disagreement,
            "detected_ambiguous": is_ambig,
            "num_candidates": len(candidates)
        })

        logger.log(f"  Disagreement: {disagreement:.3f}, Ambiguous: {is_ambig}")

        # Select best specification
        spec = select_best_specification(candidates)

        # Generate initial code
        code = generate_code_with_spec(problem['description'], spec, problem['name'])

        # Verification loop with refinement
        iteration = 0
        success, passed, total, cex, error = verify_code_with_tests(
            code, problem['test_cases'], problem['name']
        )

        while not success and iteration < MAX_REFINEMENT_ITERATIONS and cex is not None:
            iteration += 1
            logger.log(f"  Refinement iteration {iteration}")

            code = refine_code_with_counterexample(
                problem['description'], spec, code, error, cex, problem['name']
            )

            success, passed, total, cex, error = verify_code_with_tests(
                code, problem['test_cases'], problem['name']
            )

        elapsed = time.time() - start_time

        result = {
            "problem_id": problem['id'],
            "problem_name": problem['name'],
            "difficulty": problem['difficulty'],
            "method": "specbridge_dynamic",
            "success": success,
            "passed": passed,
            "total": total,
            "pass_rate": passed / total if total > 0 else 0,
            "time": elapsed,
            "refinement_iterations": iteration,
            "disagreement_score": disagreement,
            "is_ambiguous": is_ambig,
            "specification": spec,
            "code": code,
            "error": error if not success else None
        }
        results.append(result)

        logger.log(f"  Result: {'PASS' if success else 'FAIL'} ({passed}/{total} tests) after {iteration} refinements")

    return results, ambiguity_results

def compute_metrics(results, method_name):
    """Compute aggregate metrics for a set of results."""
    if not results:
        return {}

    total = len(results)
    successes = sum(1 for r in results if r['success'])
    avg_pass_rate = sum(r['pass_rate'] for r in results) / total
    avg_time = sum(r['time'] for r in results) / total

    # By difficulty
    by_difficulty = {}
    for diff in ['easy', 'medium', 'hard']:
        diff_results = [r for r in results if r.get('difficulty') == diff]
        if diff_results:
            by_difficulty[diff] = {
                'total': len(diff_results),
                'success': sum(1 for r in diff_results if r['success']),
                'success_rate': sum(1 for r in diff_results if r['success']) / len(diff_results)
            }

    return {
        'method': method_name,
        'total_problems': total,
        'successes': successes,
        'success_rate': successes / total,
        'avg_pass_rate': avg_pass_rate,
        'avg_time': avg_time,
        'by_difficulty': by_difficulty
    }

def main():
    """Run the complete experiment."""
    # Setup
    os.makedirs(RESULTS_DIR, exist_ok=True)
    logger = Logger(LOG_FILE)

    logger.log("SpecBridge Experiment")
    logger.log(f"Date: {datetime.now().isoformat()}")
    logger.log(f"Number of samples: {NUM_SAMPLES}")
    logger.log(f"Specification candidates (K): {NUM_SPEC_CANDIDATES}")
    logger.log(f"Max refinement iterations: {MAX_REFINEMENT_ITERATIONS}")

    # Load problems
    problems = get_benchmark_problems(NUM_SAMPLES)
    logger.log(f"\nLoaded {len(problems)} benchmark problems")

    # Run experiments
    all_results = {}

    # Baseline
    baseline_results = run_baseline(problems, logger)
    all_results['baseline'] = baseline_results

    # SpecBridge Static
    specbridge_static_results, spec_results = run_specbridge_static(problems, logger)
    all_results['specbridge_static'] = specbridge_static_results
    all_results['specifications'] = spec_results

    # SpecBridge Dynamic
    specbridge_dynamic_results, ambiguity_results = run_specbridge_dynamic(problems, logger)
    all_results['specbridge_dynamic'] = specbridge_dynamic_results
    all_results['ambiguity'] = ambiguity_results

    # Compute metrics
    logger.log("\n" + "=" * 60)
    logger.log("RESULTS SUMMARY")
    logger.log("=" * 60)

    metrics = {}
    metrics['baseline'] = compute_metrics(baseline_results, 'Baseline (Direct LLM)')
    metrics['specbridge_static'] = compute_metrics(specbridge_static_results, 'SpecBridge Static')
    metrics['specbridge_dynamic'] = compute_metrics(specbridge_dynamic_results, 'SpecBridge Dynamic')

    for method, m in metrics.items():
        logger.log(f"\n{m['method']}:")
        logger.log(f"  Success Rate: {m['success_rate']*100:.1f}% ({m['successes']}/{m['total_problems']})")
        logger.log(f"  Avg Pass Rate: {m['avg_pass_rate']*100:.1f}%")
        logger.log(f"  Avg Time: {m['avg_time']:.2f}s")

    # Save results
    results_file = os.path.join(RESULTS_DIR, 'experiment_results.json')
    with open(results_file, 'w') as f:
        json.dump({
            'config': {
                'num_samples': NUM_SAMPLES,
                'num_spec_candidates': NUM_SPEC_CANDIDATES,
                'max_refinement_iterations': MAX_REFINEMENT_ITERATIONS
            },
            'results': all_results,
            'metrics': metrics
        }, f, indent=2)

    logger.log(f"\nResults saved to {results_file}")
    logger.log("\nExperiment completed successfully!")

    return all_results, metrics

if __name__ == "__main__":
    main()
