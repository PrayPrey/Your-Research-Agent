"""
Main experiment script for Neural-Symbolic Repair
"""
import os
import sys
import logging
import time
import json
from typing import List, Dict

import config
from data import generate_problem_dataset, ProgrammingProblem
from model import CodeGenerationModel, FeedbackSynthesizer
from verification import CodeVerifier
from evaluation import Evaluator, ExperimentResult
from utils import setup_logging, log_experiment_start, log_experiment_end

logger = None

class NeuralSymbolicRepair:
    """Main Neural-Symbolic Repair framework"""

    def __init__(self, method: str = "veril_dynamic"):
        self.method = method
        self.code_model = CodeGenerationModel()
        self.verifier = CodeVerifier()
        self.feedback_synthesizer = FeedbackSynthesizer()

    def run_single_problem(self, problem: ProgrammingProblem) -> ExperimentResult:
        """Run the repair process on a single problem"""
        result = ExperimentResult(problem.problem_id, self.method)

        logger.info(f"\n{'='*60}")
        logger.info(f"Problem {problem.problem_id}: {problem.name}")
        logger.info(f"Method: {self.method}")
        logger.info(f"{'='*60}")

        # Step 1: Generate initial code
        logger.info("Generating initial code...")
        code = self.code_model.generate_code(
            problem.description,
            problem.function_signature
        )
        result.initial_code = code
        logger.info(f"Initial code generated ({len(code)} chars)")

        # Step 2: Iterative repair loop
        iteration = 0
        previous_code = ""

        while iteration < config.MAX_ITERATIONS:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")

            # Verify code
            verification_results, test_results = self.verifier.verify_code(
                code, problem.test_cases
            )

            # Record iteration
            result.num_iterations = iteration
            result.test_pass_rate = test_results["passed"] / test_results["total"]

            result.iteration_history.append({
                "iteration": iteration,
                "test_pass_rate": result.test_pass_rate,
                "verification_passed": all(v.passed for v in verification_results)
            })

            logger.info(f"Tests: {test_results['passed']}/{test_results['total']} passed")

            # Check if verification succeeded
            all_passed = all(v.passed for v in verification_results)
            tests_passed = test_results["failed"] == 0

            if all_passed and tests_passed:
                result.success = True
                result.final_code = code
                logger.info(f"✓ Problem solved successfully in {iteration} iterations!")
                break

            # Check for convergence (no change in code)
            if code == previous_code:
                result.converged = True
                result.final_code = code
                logger.info("✗ Convergence detected (code unchanged)")
                break

            # Generate feedback based on method
            if self.method == "no_feedback":
                # No feedback - just regenerate
                feedback = "The code has issues. Please generate a corrected version."
            elif self.method == "raw_feedback":
                # Raw verification output
                feedback = self.verifier.get_raw_feedback(verification_results, test_results)
            elif self.method == "veril_static":
                # Basic feedback synthesis (using verifier's synthesis)
                feedback = self.verifier.synthesize_feedback(
                    verification_results, test_results, code
                )
            elif self.method == "veril_dynamic":
                # Full VeriL with LLM-based feedback synthesis
                raw_feedback = self.verifier.get_raw_feedback(verification_results, test_results)
                feedback = self.feedback_synthesizer.synthesize_feedback(
                    raw_feedback, code, problem.description
                )
            else:
                feedback = self.verifier.synthesize_feedback(
                    verification_results, test_results, code
                )

            logger.info(f"Feedback generated ({len(feedback)} chars)")

            # Repair code
            previous_code = code
            code = self.code_model.repair_code(code, feedback, problem.description)
            logger.info(f"Code repaired ({len(code)} chars)")

            # Small delay to avoid rate limiting
            time.sleep(1)

        # Final check if not already successful
        if not result.success:
            result.final_code = code
            logger.info(f"✗ Problem not solved after {iteration} iterations")

        return result

def run_baseline_experiment(method: str, problems: List[ProgrammingProblem]) -> List[ExperimentResult]:
    """Run experiment for a baseline method"""
    logger.info(f"\n{'#'*80}")
    logger.info(f"Running baseline: {method}")
    logger.info(f"{'#'*80}")

    framework = NeuralSymbolicRepair(method=method)
    results = []

    for i, problem in enumerate(problems):
        logger.info(f"\nProgress: {i+1}/{len(problems)}")
        try:
            result = framework.run_single_problem(problem)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing problem {problem.problem_id}: {e}")
            # Create a failed result
            result = ExperimentResult(problem.problem_id, method)
            result.success = False
            result.num_iterations = 0
            results.append(result)

        # Save intermediate results
        if (i + 1) % 5 == 0:
            save_intermediate_results(results, method)

    return results

def save_intermediate_results(results: List[ExperimentResult], method: str):
    """Save intermediate results"""
    filename = f"{method}_intermediate_results.json"
    with open(filename, 'w') as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    logger.info(f"Intermediate results saved to {filename}")

def main():
    """Main experiment entry point"""
    global logger
    logger = setup_logging("log.txt")

    # Log experiment configuration
    config_dict = {
        "LLM_MODEL": config.LLM_MODEL,
        "MAX_ITERATIONS": config.MAX_ITERATIONS,
        "NUM_PROBLEMS": config.NUM_PROBLEMS,
        "BASELINES": config.BASELINES,
        "RANDOM_SEED": config.RANDOM_SEED
    }
    log_experiment_start(logger, config_dict)

    # Generate problem dataset
    logger.info("\nGenerating problem dataset...")
    problems = generate_problem_dataset(config.NUM_PROBLEMS, config.RANDOM_SEED)
    logger.info(f"Generated {len(problems)} problems")

    # Save dataset
    with open("problems_dataset.json", 'w') as f:
        json.dump([p.to_dict() for p in problems], f, indent=2)

    # Initialize evaluator
    evaluator = Evaluator()

    # Run experiments for each baseline
    all_results = {}
    for method in config.BASELINES:
        results = run_baseline_experiment(method, problems)
        all_results[method] = results

        # Add to evaluator
        for result in results:
            evaluator.add_result(result)

        # Save method-specific results
        with open(f"{method}_results.json", 'w') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)

    # Save all results
    logger.info("\nSaving final results...")
    evaluator.save_results("all_results.json")

    # Compute and display metrics
    logger.info("\n" + "="*80)
    logger.info("FINAL RESULTS")
    logger.info("="*80)

    all_metrics = evaluator.compute_all_metrics()
    for method, metrics in all_metrics.items():
        logger.info(f"\n{method}:")
        logger.info(f"  Repair Success Rate: {metrics['repair_success_rate']:.3f}")
        logger.info(f"  Average Repair Iterations: {metrics['average_repair_iterations']:.2f}")
        logger.info(f"  Average Test Pass Rate: {metrics['avg_test_pass_rate']:.3f}")
        logger.info(f"  Convergence Rate: {metrics['convergence_rate']:.3f}")

    # Save metrics
    with open("baseline_results.json", 'w') as f:
        json.dump(all_metrics, f, indent=2)

    # Method comparisons
    logger.info("\n" + "="*80)
    logger.info("METHOD COMPARISONS")
    logger.info("="*80)

    # Compare VeriL dynamic with other methods
    for method in ["no_feedback", "raw_feedback", "veril_static"]:
        if method in config.BASELINES and "veril_dynamic" in config.BASELINES:
            comparison = evaluator.compare_methods("veril_dynamic", method)
            logger.info(f"\nVeriL Dynamic vs {method}:")
            logger.info(f"  Success advantage: {comparison['success_advantage']}")
            logger.info(f"  Avg iteration difference: {comparison['avg_iteration_difference']:.2f}")

    log_experiment_end(logger)
    logger.info("\nExperiment completed successfully!")
    logger.info("Results saved to: all_results.json, baseline_results.json")

if __name__ == "__main__":
    main()
