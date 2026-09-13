#!/usr/bin/env python3
"""
Dry run test for H-E1 experiment
Tests with 5 tasks only
"""
import json
import logging
from pathlib import Path

# Import from main experiment
import sys
sys.path.insert(0, str(Path(__file__).parent))
from run_experiment import (
    ExperimentConfig, HumanEvalLoader, CodeLlamaGenerator,
    MypyVerifier, PytestVerifier, DualSensitivityClassifier,
    create_test_code, generate_figures
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dry_run():
    """Quick dry run with 5 tasks"""
    logger.info("Starting DRY RUN (5 tasks)")

    # Modified config for dry run
    config = ExperimentConfig(
        k_samples=5,  # Reduce to 5 samples per task
        max_length=128,  # Shorter completions
        output_dir=Path("./outputs_dry_run"),
        figures_dir=Path("./figures_dry_run")
    )

    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset
    loader = HumanEvalLoader(use_evalplus=True)
    problems = loader.load_problems()

    # Test with first 5 tasks only
    test_tasks = dict(list(problems.items())[:5])
    logger.info(f"Testing with {len(test_tasks)} tasks")

    # Initialize components (without loading full model)
    generator = None  # Skip model loading for dry run
    mypy_verifier = MypyVerifier(timeout=10)
    pytest_verifier = PytestVerifier(timeout=60)
    classifier = DualSensitivityClassifier(k_samples=5, variance_threshold=1.0)

    # Simulate results
    results = []
    for task_id, problem in test_tasks.items():
        logger.info(f"Processing {task_id}")

        # Create mock samples (just use prompt as sample for testing)
        samples = [problem['prompt'] + "\n    pass\n"] * 5

        # Test mypy verifier
        mypy_results = mypy_verifier.verify_batch(samples)
        logger.info(f"  Mypy: {sum(mypy_results)}/{len(mypy_results)} passed")

        # Test pytest verifier
        test_code = create_test_code(problem)
        pytest_results = pytest_verifier.verify_batch(samples, [test_code] * len(samples))
        logger.info(f"  Pytest: {sum(pytest_results)}/{len(pytest_results)} passed")

        # Classify
        result = classifier.classify_task(task_id, mypy_results, pytest_results)
        results.append(result)

    # Save dry run results
    dry_run_results = {
        'mode': 'DRY_RUN',
        'tasks_tested': len(test_tasks),
        'results': results
    }

    with open(config.output_dir / 'dry_run_results.json', 'w') as f:
        json.dump(dry_run_results, f, indent=2)

    logger.info(f"✅ DRY RUN COMPLETE - {len(results)} tasks processed")
    logger.info(f"   Results saved to {config.output_dir}")

    return dry_run_results

if __name__ == '__main__':
    results = dry_run()
    print(f"\n✅ Dry run completed successfully!")
    print(f"   Processed {len(results['results'])} tasks")
