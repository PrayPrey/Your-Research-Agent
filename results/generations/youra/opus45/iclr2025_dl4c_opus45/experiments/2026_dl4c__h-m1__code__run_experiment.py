#!/usr/bin/env python3
"""H-M1: Zero-Reward Basin Mechanism Analysis.

Tests: P(assertion | failure, RL) > P(assertion | failure, DPO)
using one-sided Fisher's exact test.

This is an ANALYSIS hypothesis that reuses H-E1 execution results.
No new model inference or training required.
"""

import logging
import os
import sys
from datetime import datetime

from config import CONFIG, HM1Config
from data_loader import load_h_e1_results, validate_data_integrity
from analyze import run_analysis
from visualize import generate_all_figures

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main(config: HM1Config = None) -> int:
    """H-M1 analysis pipeline.

    1. Load H-E1 execution results (RL and DPO)
    2. Validate data integrity
    3. Run Fisher's exact test analysis
    4. Generate figures
    5. Return gate result

    Args:
        config: H-M1 configuration (defaults to CONFIG)

    Returns:
        0 if gate passes, 1 if gate fails
    """
    if config is None:
        config = CONFIG

    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("H-M1: Zero-Reward Basin Mechanism Analysis")
    logger.info("=" * 60)
    logger.info("Hypothesis: P(assertion | failure, RL) > P(assertion | failure, DPO)")
    logger.info("Method: One-sided Fisher's exact test")
    logger.info("")

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # ======================================================================
    # Step 1: Load H-E1 Results
    # ======================================================================
    logger.info("[Step 1] Loading H-E1 execution results...")
    try:
        rl_results, dpo_results = load_h_e1_results(config)
        logger.info(f"  Loaded {len(rl_results)} RL results")
        logger.info(f"  Loaded {len(dpo_results)} DPO results")
    except FileNotFoundError as e:
        logger.error(f"H-E1 data not found: {e}")
        return 1

    # ======================================================================
    # Step 2: Validate Data Integrity
    # ======================================================================
    logger.info("\n[Step 2] Validating data integrity...")
    validation = validate_data_integrity(rl_results, dpo_results, config)

    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"  {warning}")

    logger.info(f"  RL failures: {validation['rl_failures']}")
    logger.info(f"  DPO failures: {validation['dpo_failures']}")
    logger.info(f"  Data valid: {validation['valid']}")

    if not validation["valid"]:
        logger.error("Data validation failed. Aborting.")
        return 1

    # ======================================================================
    # Step 3: Run Fisher's Exact Test Analysis
    # ======================================================================
    logger.info("\n[Step 3] Running Fisher's exact test analysis...")
    metrics = run_analysis(rl_results, dpo_results, config)

    # ======================================================================
    # Step 4: Generate Figures
    # ======================================================================
    logger.info("\n[Step 4] Generating figures...")
    generate_all_figures(
        metrics,
        metrics.get("rl_counts", {}),
        metrics.get("dpo_counts", {}),
        config
    )

    # ======================================================================
    # Step 5: Print Summary
    # ======================================================================
    duration = datetime.now() - start_time

    logger.info("\n" + "=" * 60)
    logger.info("H-M1 RESULTS: Zero-Reward Basin Mechanism")
    logger.info("=" * 60)
    logger.info(f"RL assertion proportion:  {metrics['rl_assertion_prop']*100:.2f}% ({metrics['rl_assertion_count']}/{metrics['rl_total_failures']})")
    logger.info(f"DPO assertion proportion: {metrics['dpo_assertion_prop']*100:.2f}% ({metrics['dpo_assertion_count']}/{metrics['dpo_total_failures']})")
    logger.info("-" * 60)
    logger.info(f"Odds ratio: {metrics['odds_ratio']:.4f}")
    logger.info(f"P-value (Fisher's exact, {metrics['alternative']}): {metrics['p_value']:.6f}")
    logger.info(f"Threshold: p < {metrics['fisher_p_threshold']}")
    logger.info(f"Direction matches: {metrics['direction_matches']}")
    logger.info("-" * 60)

    # Mechanism log
    logger.info(f"\nMechanism Log: {metrics['mechanism_log']}")

    if metrics["gate_pass"]:
        logger.info("\n🎉 GATE RESULT: PASS")
        logger.info("Mechanism verified: RL's zero-reward basin concentrates failures in assertion errors")
        logger.info("  - RL assertion proportion significantly > DPO assertion proportion")
        logger.info("  - Consistent with binary execution reward creating flat zero-reward basin")
    else:
        logger.info("\n❌ GATE RESULT: FAIL")
        if not metrics["direction_matches"]:
            logger.info("  - Direction mismatch: RL assertion proportion not > DPO")
        if metrics["p_value"] >= metrics["fisher_p_threshold"]:
            logger.info(f"  - p-value {metrics['p_value']:.4f} >= {metrics['fisher_p_threshold']}")

    logger.info(f"\nExperiment completed in {duration}")
    logger.info(f"Results saved to: {config.output_dir}/")
    logger.info(f"Figures saved to: {config.figures_dir}/")

    return 0 if metrics["gate_pass"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
