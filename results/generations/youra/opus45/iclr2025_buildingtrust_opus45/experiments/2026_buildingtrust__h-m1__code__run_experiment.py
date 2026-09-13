#!/usr/bin/env python3
"""
Main orchestrator for H-M1 Conditional Margin Inflation Analysis.

Statistical reanalysis of H-E1 cached data to test whether instruction tuning
inflates margins for incorrect predictions.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

import numpy as np

# Add code directory to path
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    SEED, FAMILIES, FIGURES_DIR, HYPOTHESIS_DIR,
    H_E1_CACHE_DIR, ensure_directories, GATE_TYPE
)
from data_loader import load_family_arrays, validate_arrays, load_h_e1_results_json
from analysis import analyze_family
from visualize import save_all_figures
from report import evaluate_gate, save_experiment_results_yaml, generate_validation_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CODE_DIR / 'experiment.log')
    ]
)
logger = logging.getLogger(__name__)


def set_seed(seed: int = SEED) -> None:
    """Set random seed for reproducibility."""
    np.random.seed(seed)
    logger.info(f"Random seed set to {seed}")


def main(families: list[str] = None) -> int:
    """
    Main orchestrator: load -> validate -> analyze -> visualize -> report.

    Args:
        families: List of model families to analyze (defaults to config.FAMILIES)

    Returns:
        Exit code (0 for PASS, 1 for FAIL)
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("H-M1: Conditional Margin Inflation Analysis")
    logger.info("=" * 60)

    # Set seed
    set_seed(SEED)

    # Create output directories
    ensure_directories()

    # Use default families if not specified
    if families is None:
        families = FAMILIES
    logger.info(f"Analyzing families: {families}")

    # Verify H-E1 cache exists
    if not H_E1_CACHE_DIR.exists():
        logger.error(f"H-E1 cache not found: {H_E1_CACHE_DIR}")
        return 1

    # Load and analyze each family
    family_results = {}
    arrays_by_family = {}

    for family in families:
        logger.info(f"\n{'='*40}")
        logger.info(f"Processing family: {family}")
        logger.info(f"{'='*40}")

        try:
            # Load cached arrays
            logger.info("Loading cached arrays from H-E1...")
            arrays = load_family_arrays(family, H_E1_CACHE_DIR)
            logger.info(f"  Base margins: {arrays['base_margins'].shape}")
            logger.info(f"  Inst margins: {arrays['inst_margins'].shape}")

            # Validate arrays
            logger.info("Validating arrays...")
            validate_arrays(arrays)
            logger.info("  Validation passed")

            # Store arrays for visualization
            arrays_by_family[family] = arrays

            # Run analysis
            logger.info("Running statistical analysis...")
            result = analyze_family(family, arrays)
            family_results[family] = result

            # Log key results
            logger.info(f"\n  Results for {family}:")
            logger.info(f"    Base E[m|incorrect]: {result['base_stats']['mean_incorrect']:.4f}")
            logger.info(f"    Inst E[m|incorrect]: {result['inst_stats']['mean_incorrect']:.4f}")
            logger.info(f"    Inflation ratio: {result['effect_size']['inflation_ratio']:.2f}x")
            logger.info(f"    p-value: {result['permutation_test']['p_value']:.6f}")
            logger.info(f"    Gate pass: {result['gate_pass']}")

        except FileNotFoundError as e:
            logger.error(f"Failed to load data for {family}: {e}")
            continue
        except ValueError as e:
            logger.error(f"Validation failed for {family}: {e}")
            continue

    # Check we have results
    if not family_results:
        logger.error("No families were successfully analyzed!")
        return 1

    # Evaluate overall gate
    gate_result = evaluate_gate(family_results)
    logger.info(f"\n{'='*60}")
    logger.info(f"GATE EVALUATION: {gate_result}")
    logger.info(f"{'='*60}")

    # Generate figures
    logger.info("\nGenerating figures...")
    try:
        figure_paths = save_all_figures(family_results, arrays_by_family, FIGURES_DIR)
        for path in figure_paths:
            logger.info(f"  Saved: {path}")
    except Exception as e:
        logger.error(f"Figure generation failed: {e}")
        # Continue anyway - figures are not critical

    # Save results
    logger.info("\nSaving results...")
    results_path = HYPOTHESIS_DIR / "experiment_results.yaml"
    save_experiment_results_yaml(family_results, gate_result, results_path)
    logger.info(f"  Saved: {results_path}")

    # Generate validation report
    report_path = HYPOTHESIS_DIR / "04_validation.md"
    generate_validation_report(family_results, gate_result, report_path)
    logger.info(f"  Saved: {report_path}")

    # Final summary
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"\n{'='*60}")
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"  Families analyzed: {len(family_results)}")
    logger.info(f"  Families passed: {sum(1 for r in family_results.values() if r['gate_pass'])}")
    logger.info(f"  Gate result: {gate_result}")
    logger.info(f"  Elapsed time: {elapsed:.1f}s")

    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="H-M1: Conditional Margin Inflation Analysis"
    )
    parser.add_argument(
        "--families",
        nargs="+",
        choices=["qwen", "mistral", "llama"],
        default=None,
        help="Model families to analyze (default: qwen, mistral)"
    )
    args = parser.parse_args()

    exit_code = main(families=args.families)
    sys.exit(exit_code)
