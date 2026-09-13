#!/usr/bin/env python3
"""
Quick test of H-M3 implementation with reduced scope (3 tasks, 3 iterations)
to verify the methodology works before full experiment
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Patch the config for testing
from run_experiment import ExperimentConfig, TokenEfficiencyPipeline
import logging

# Override config for testing
class TestConfig(ExperimentConfig):
    max_iterations: int = 3  # Reduced from 10
    output_dir = __file__.replace('run_test.py', 'outputs_test')
    figures_dir = __file__.replace('run_test.py', 'figures_test')

# Monkey-patch the task loader to use only 3 tasks
original_load = None

def patched_load_qualified_task_ids(self, h_e1_validation_path):
    """Load only first 3 tasks for testing"""
    task_ids = original_load(self, h_e1_validation_path)
    logging.info(f"TEST MODE: Using only first 3 tasks (of {len(task_ids)} total)")
    return task_ids[:3]

def main():
    from run_experiment import HumanEvalLoader
    global original_load
    original_load = HumanEvalLoader.load_qualified_task_ids
    HumanEvalLoader.load_qualified_task_ids = patched_load_qualified_task_ids

    print("="*60)
    print("H-M3 TEST MODE")
    print("Scope: 3 tasks, 3 iterations (instead of 20 tasks, 10 iterations)")
    print("Purpose: Verify methodology works before full experiment")
    print("="*60)

    config = TestConfig()
    pipeline = TokenEfficiencyPipeline(config)

    try:
        results = pipeline.run()
        print(f"\n{'='*60}")
        print(f"TEST COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Gate status: {'PASSED' if results['gate_satisfied'] else 'FAILED'}")
        print(f"Efficiency ratio: {results['metrics']['efficiency_ratio']:.3f}")
        print(f"\nCASCADE successful tasks: {results['metrics']['cascade']['successful_tasks']}/3")
        print(f"AGGREGATION successful tasks: {results['metrics']['aggregation']['successful_tasks']}/3")
        print(f"{'='*60}\n")
        print("✅ Code verification passed - methodology works!")
        print("Ready for full experiment with 20 tasks, 10 iterations")
        return 0
    except Exception as e:
        logging.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ TEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
