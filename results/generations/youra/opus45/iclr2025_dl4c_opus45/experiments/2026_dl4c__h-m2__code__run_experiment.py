#!/usr/bin/env python3
"""H-M2 Experiment Runner: Execution Depth Analysis for RL vs DPO failures.

This script orchestrates the H-M2 hypothesis validation:
1. Load H-E1 cached execution results
2. Load evalplus problems (for prompts and tests)
3. Validate data integrity
4. Measure execution depth for all failures using REAL tracing
5. Run t-test statistical analysis
6. Generate visualization figures

Gate pass condition (SHOULD_WORK):
- p-value < 0.05 (one-sided t-test)
- mean(execution_depth | RL) > mean(execution_depth | DPO)

Exit codes:
- 0: Gate passed
- 1: Gate failed
"""

import logging
import os
import sys

from config import CONFIG, HM2Config
from data_loader import load_h_e1_results, extract_failures, validate_data_integrity
from depth_tracer import measure_all_failures
from analyze import run_analysis
from visualize import generate_all_figures


def load_evalplus_problems():
    """Load HumanEval+ and MBPP+ problems for prompt/test data.

    Returns:
        Dict mapping task_id -> problem dict with 'prompt', 'test', 'entry_point'
    """
    from evalplus.data import get_human_eval_plus, get_mbpp_plus

    problems = {}

    # Load HumanEval+
    humaneval = get_human_eval_plus()
    for task_id, problem in humaneval.items():
        problems[task_id] = {
            "prompt": problem.get("prompt", ""),
            "test": problem.get("test", ""),
            "entry_point": problem.get("entry_point", ""),
        }

    # Load MBPP+
    mbpp = get_mbpp_plus()
    for task_id, problem in mbpp.items():
        problems[task_id] = {
            "prompt": problem.get("prompt", ""),
            "test": problem.get("test", ""),
            "entry_point": problem.get("entry_point", ""),
        }

    return problems


def setup_logging() -> None:
    """Configure logging for experiment."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def main(config: HM2Config = None) -> int:
    """Run H-M2 execution depth analysis pipeline.

    Args:
        config: H-M2 configuration. Uses global CONFIG if None.

    Returns:
        Exit code: 0 if gate passes, 1 otherwise
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    if config is None:
        config = CONFIG

    logger.info("=" * 60)
    logger.info("H-M2: Execution Depth Analysis")
    logger.info("=" * 60)

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # Step 1: Load H-E1 results
    logger.info("Step 1: Loading H-E1 execution results...")
    try:
        rl_results, dpo_results = load_h_e1_results(config)
    except FileNotFoundError as e:
        logger.error(f"Failed to load H-E1 results: {e}")
        return 1

    # Step 2: Extract failures
    logger.info("Step 2: Extracting failure cases...")
    rl_failures = extract_failures(rl_results)
    dpo_failures = extract_failures(dpo_results)

    # Step 3: Validate data integrity
    logger.info("Step 3: Validating data integrity...")
    validation = validate_data_integrity(rl_failures, dpo_failures, config)

    if validation["warnings"]:
        for w in validation["warnings"]:
            logger.warning(w)

    if not validation["valid"]:
        logger.error("Data integrity validation failed")
        return 1

    logger.info(f"Validated: {validation['rl_failures']} RL failures, {validation['dpo_failures']} DPO failures")

    # Step 4: Load evalplus problems for prompt/test data
    logger.info("Step 4: Loading evalplus problems (prompts + tests)...")
    try:
        problems = load_evalplus_problems()
        logger.info(f"Loaded {len(problems)} problems from evalplus")
    except Exception as e:
        logger.error(f"Failed to load evalplus problems: {e}")
        logger.info("Falling back to trace-based measurement without full context")
        problems = {}

    # Step 5: Measure execution depth using REAL tracing
    logger.info("Step 5: Measuring execution depth for all failures (REAL tracing)...")
    logger.info(f"Processing {len(rl_failures)} RL failures...")
    rl_depth_results = measure_all_failures(rl_failures, "rl", config, problems)

    logger.info(f"Processing {len(dpo_failures)} DPO failures...")
    dpo_depth_results = measure_all_failures(dpo_failures, "dpo", config, problems)

    # Step 6: Run statistical analysis
    logger.info("Step 6: Running statistical analysis...")
    metrics = run_analysis(rl_depth_results, dpo_depth_results, config)

    # Step 7: Generate figures
    logger.info("Step 7: Generating visualization figures...")
    generate_all_figures(rl_depth_results, dpo_depth_results, metrics, config.figures_dir)

    # Report final result
    logger.info("=" * 60)
    if metrics["gate_pass"]:
        logger.info("H-M2 GATE: PASS")
        logger.info(f"  - p-value: {metrics['p_value']:.6f} < {config.t_test_p_threshold}")
        logger.info(f"  - Direction: RL mean ({metrics['rl_statistics']['mean']:.4f}) > DPO mean ({metrics['dpo_statistics']['mean']:.4f})")
        logger.info(f"  - Cohen's d: {metrics['cohens_d']:.4f}")
        return 0
    else:
        logger.info("H-M2 GATE: FAIL")
        if metrics["p_value"] >= config.t_test_p_threshold:
            logger.info(f"  - p-value: {metrics['p_value']:.6f} >= {config.t_test_p_threshold} (not significant)")
        if not metrics["direction_correct"]:
            logger.info(f"  - Direction wrong: RL mean ({metrics['rl_statistics']['mean']:.4f}) <= DPO mean ({metrics['dpo_statistics']['mean']:.4f})")
        return 1


if __name__ == "__main__":
    sys.exit(main())
