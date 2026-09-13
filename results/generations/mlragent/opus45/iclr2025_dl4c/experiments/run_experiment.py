"""
Main Experiment Runner for ExePlay
Execution-Guided Self-Play for Code Agent Alignment
"""
import os
import sys
import json
import random
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODEL_NAME, DEVICE, EQS_WEIGHTS, TRAINING_CONFIG,
    DPO_CONFIG, EXPERIMENT_CONFIG, BASE_DIR, RESULTS_DIR
)
from data_loader import create_synthetic_tasks, prepare_dataset
from execution_feedback import (
    execute_code_with_tests,
    compute_execution_quality_score,
    ExecutionResult
)
from exeplay_framework import ExePlayFramework, PreferencePair
from baselines import run_all_baselines, BaselineResult
from visualization import create_all_visualizations

# Setup logging
def setup_logging(log_file: str):
    """Setup logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_exeplay_experiment(
    framework: ExePlayFramework,
    tasks: List[Dict[str, Any]],
    num_iterations: int = 3,
    samples_per_task: int = 4,
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Run the ExePlay experiment for multiple iterations.

    Args:
        framework: ExePlayFramework instance
        tasks: List of task dictionaries
        num_iterations: Number of self-play iterations
        samples_per_task: Number of samples per task
        logger: Logger instance

    Returns:
        Dictionary with experiment results
    """
    results = {
        "iterations": [],
        "total_pairs": 0,
        "final_pass_rate": 0.0,
        "final_avg_eqs": 0.0
    }

    for iteration in range(num_iterations):
        if logger:
            logger.info(f"\n{'='*50}")
            logger.info(f"ExePlay Iteration {iteration + 1}/{num_iterations}")
            logger.info(f"{'='*50}")

        pairs, stats = framework.run_iteration(
            tasks,
            samples_per_task=samples_per_task,
            temperature=TRAINING_CONFIG['temperature'],
            max_length=EXPERIMENT_CONFIG['max_generation_length']
        )

        iteration_result = {
            "iteration": iteration + 1,
            "total_solutions": stats['total_solutions'],
            "passed_solutions": stats['passed_solutions'],
            "pass_rate": stats['pass_rate'],
            "avg_eqs": stats['avg_eqs'],
            "pairs_generated": stats['pairs_generated']
        }
        results['iterations'].append(iteration_result)
        results['total_pairs'] += len(pairs)

        if logger:
            logger.info(f"Solutions: {stats['total_solutions']}, Passed: {stats['passed_solutions']}")
            logger.info(f"Pass Rate: {stats['pass_rate']:.4f}, Avg EQS: {stats['avg_eqs']:.4f}")
            logger.info(f"Preference Pairs Generated: {len(pairs)}")

    # Final stats
    if results['iterations']:
        results['final_pass_rate'] = results['iterations'][-1]['pass_rate']
        results['final_avg_eqs'] = results['iterations'][-1]['avg_eqs']

    return results


def evaluate_on_test_set(
    framework: ExePlayFramework,
    test_tasks: List[Dict[str, Any]],
    num_samples: int = 4,
    logger: logging.Logger = None
) -> Dict[str, Any]:
    """
    Evaluate the model on a held-out test set.

    Args:
        framework: ExePlayFramework instance
        test_tasks: List of test task dictionaries
        num_samples: Number of samples per task
        logger: Logger instance

    Returns:
        Dictionary with evaluation results
    """
    if logger:
        logger.info("\n" + "="*50)
        logger.info("Evaluating on Test Set")
        logger.info("="*50)

    total = 0
    passed = 0
    eqs_scores = []
    task_results = []

    for task in test_tasks:
        solutions = framework.generate_solutions(
            task,
            num_samples=num_samples,
            temperature=0.3,  # Lower temperature for evaluation
            max_length=EXPERIMENT_CONFIG['max_generation_length']
        )

        scored_solutions = framework.execute_and_score(solutions, task)

        task_passed = any(res.passed for _, res, _ in scored_solutions)
        task_eqs = max(eqs for _, _, eqs in scored_solutions) if scored_solutions else 0

        total += 1
        if task_passed:
            passed += 1
        eqs_scores.append(task_eqs)

        task_results.append({
            "task_id": str(task.get('id', '')),
            "passed": task_passed,
            "best_eqs": task_eqs
        })

    results = {
        "total_tasks": total,
        "passed_tasks": passed,
        "pass_rate": passed / total if total > 0 else 0,
        "avg_eqs": np.mean(eqs_scores) if eqs_scores else 0,
        "task_results": task_results
    }

    if logger:
        logger.info(f"Test Set Results:")
        logger.info(f"  Pass Rate: {results['pass_rate']:.4f}")
        logger.info(f"  Avg EQS: {results['avg_eqs']:.4f}")

    return results


def main():
    """Main experiment runner."""
    parser = argparse.ArgumentParser(description="ExePlay Experiment")
    parser.add_argument("--num_tasks", type=int, default=30, help="Number of tasks to use")
    parser.add_argument("--num_iterations", type=int, default=3, help="Number of ExePlay iterations")
    parser.add_argument("--samples_per_task", type=int, default=4, help="Samples per task")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--dataset", type=str, default="synthetic", help="Dataset to use")
    args = parser.parse_args()

    # Create output directories
    os.makedirs(RESULTS_DIR, exist_ok=True)
    log_file = os.path.join(RESULTS_DIR, "log.txt")
    logger = setup_logging(log_file)

    logger.info("="*60)
    logger.info("ExePlay: Execution-Guided Self-Play for Code Agent Alignment")
    logger.info("="*60)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Configuration:")
    logger.info(f"  Model: {MODEL_NAME}")
    logger.info(f"  Dataset: {args.dataset}")
    logger.info(f"  Number of Tasks: {args.num_tasks}")
    logger.info(f"  Iterations: {args.num_iterations}")
    logger.info(f"  Samples per Task: {args.samples_per_task}")
    logger.info(f"  Seed: {args.seed}")

    # Set seed
    set_seed(args.seed)

    # Load data
    logger.info("\nLoading dataset...")
    try:
        if args.dataset == "synthetic":
            all_tasks = create_synthetic_tasks(args.num_tasks)
        else:
            all_tasks = prepare_dataset(args.dataset, args.num_tasks)
    except Exception as e:
        logger.warning(f"Failed to load {args.dataset} dataset: {e}")
        logger.info("Falling back to synthetic tasks...")
        all_tasks = create_synthetic_tasks(args.num_tasks)

    # Split into train and test
    random.shuffle(all_tasks)
    split_idx = int(len(all_tasks) * 0.8)
    train_tasks = all_tasks[:split_idx]
    test_tasks = all_tasks[split_idx:]

    logger.info(f"Train tasks: {len(train_tasks)}, Test tasks: {len(test_tasks)}")

    # Load model and tokenizer
    logger.info(f"\nLoading model: {MODEL_NAME}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            model.config.pad_token_id = tokenizer.eos_token_id
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

    # Initialize ExePlay framework
    logger.info("\nInitializing ExePlay Framework...")
    framework = ExePlayFramework(
        model_name=MODEL_NAME,
        device=DEVICE,
        eqs_weights=EQS_WEIGHTS,
        dpo_beta=DPO_CONFIG['beta'],
        lambda_margin=DPO_CONFIG['lambda_margin']
    )

    # Run baselines
    logger.info("\n" + "="*60)
    logger.info("Running Baseline Methods")
    logger.info("="*60)
    baseline_results = run_all_baselines(
        model, tokenizer, test_tasks,
        num_samples=args.samples_per_task,
        device=DEVICE
    )

    # Run ExePlay experiment
    logger.info("\n" + "="*60)
    logger.info("Running ExePlay Experiment")
    logger.info("="*60)
    exeplay_results = run_exeplay_experiment(
        framework,
        train_tasks,
        num_iterations=args.num_iterations,
        samples_per_task=args.samples_per_task,
        logger=logger
    )

    # Evaluate on test set
    test_results = evaluate_on_test_set(
        framework,
        test_tasks,
        num_samples=args.samples_per_task,
        logger=logger
    )

    # Compile all results
    all_results = {
        "experiment_config": {
            "model": MODEL_NAME,
            "dataset": args.dataset,
            "num_tasks": args.num_tasks,
            "num_iterations": args.num_iterations,
            "samples_per_task": args.samples_per_task,
            "seed": args.seed,
            "eqs_weights": EQS_WEIGHTS,
            "dpo_config": DPO_CONFIG
        },
        "baseline_results": {
            name: {
                "method_name": result.method_name,
                "pass_rate": result.pass_rate,
                "avg_eqs": result.avg_eqs,
                "total_solutions": result.total_solutions,
                "passed_solutions": result.passed_solutions
            }
            for name, result in baseline_results.items()
        },
        "exeplay_results": exeplay_results,
        "test_results": test_results,
        "timestamp": datetime.now().isoformat()
    }

    # Save results
    results_file = os.path.join(RESULTS_DIR, "results.json")
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"\nResults saved to {results_file}")

    # Generate visualizations
    logger.info("\nGenerating visualizations...")
    try:
        create_all_visualizations(all_results, RESULTS_DIR)
        logger.info("Visualizations created successfully!")
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()

    # Print summary
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("="*60)

    logger.info("\nBaseline Results:")
    for name, result in baseline_results.items():
        logger.info(f"  {name}: Pass Rate = {result.pass_rate:.4f}, Avg EQS = {result.avg_eqs:.4f}")

    logger.info(f"\nExePlay Results:")
    logger.info(f"  Final Pass Rate: {exeplay_results['final_pass_rate']:.4f}")
    logger.info(f"  Final Avg EQS: {exeplay_results['final_avg_eqs']:.4f}")
    logger.info(f"  Total Preference Pairs: {exeplay_results['total_pairs']}")

    logger.info(f"\nTest Set Evaluation:")
    logger.info(f"  Pass Rate: {test_results['pass_rate']:.4f}")
    logger.info(f"  Avg EQS: {test_results['avg_eqs']:.4f}")

    logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Experiment completed successfully!")

    return all_results


if __name__ == "__main__":
    main()
