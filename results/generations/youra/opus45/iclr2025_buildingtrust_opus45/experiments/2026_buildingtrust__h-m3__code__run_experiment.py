#!/usr/bin/env python3
"""Main experiment orchestrator for H-M3 Brier decomposition.

Executes the full analysis pipeline:
1. Load cached margin/correctness data from H-E1
2. Compute Brier decomposition for base and instruct models
3. Bootstrap confidence intervals and paired difference tests
4. Generate figures and validation report
5. Evaluate gate condition

Usage:
    python run_experiment.py [--families qwen mistral]
"""
import argparse
import logging
import random
import sys
from datetime import datetime

import numpy as np

from config import (
    SEED,
    FAMILIES,
    FIGURES_DIR,
    ensure_directories,
)
from data_loader import load_all_families
from analysis import analyze_family, evaluate_gate
from visualize import save_all_figures
from report import save_experiment_results_yaml, generate_validation_report


def set_seed(seed: int = SEED) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def setup_logging() -> logging.Logger:
    """Configure logging."""
    logger = logging.getLogger("h-m3")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def main(families: list[str] = None) -> int:
    """Run the full H-M3 experiment pipeline.

    Args:
        families: List of model families to analyze (default: FAMILIES from config)

    Returns:
        Exit code: 0 for PASS, 1 for FAIL
    """
    families = families or FAMILIES
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("H-M3: Geometric vs Scalar Distortion via Brier Decomposition")
    logger.info("=" * 60)

    # Initialize
    logger.info("Initializing...")
    ensure_directories()
    set_seed()

    # Load data
    logger.info(f"Loading data for families: {families}")
    try:
        family_data = load_all_families(families)
    except FileNotFoundError as e:
        logger.error(f"Data loading failed: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Data validation failed: {e}")
        return 1

    for family, data in family_data.items():
        logger.info(f"  {family}: {len(data['base_margins'])} samples loaded")

    # Analyze each family
    logger.info("Running per-family analysis...")
    family_results = {}

    for family in families:
        logger.info(f"  Analyzing {family}...")
        try:
            results = analyze_family(family, family_data[family])
            family_results[family] = results

            # Log key results
            ref_base = results["base"]["decomposition"]["refinement"]
            ref_inst = results["instruct"]["decomposition"]["refinement"]
            delta = results["refinement_difference"]["delta_mean"]
            p_val = results["refinement_difference"]["p_value"]

            logger.info(
                f"    Refinement: base={ref_base:.4f}, instruct={ref_inst:.4f}, "
                f"delta={delta:+.4f}, p={p_val:.4f}"
            )
            logger.info(f"    Gate pass: {results['gate_pass']}")

        except Exception as e:
            logger.error(f"  Analysis failed for {family}: {e}")
            return 1

    # Evaluate gate
    gate_result = evaluate_gate(family_results)
    logger.info(f"Gate result: {gate_result}")

    # Generate figures
    logger.info("Generating figures...")
    try:
        figure_paths = save_all_figures(family_results, family_data, FIGURES_DIR)
        for path in figure_paths:
            logger.info(f"  Saved: {path}")
    except Exception as e:
        logger.error(f"Figure generation failed: {e}")
        # Continue - figures are not critical for gate evaluation

    # Save results
    logger.info("Saving results...")
    try:
        save_experiment_results_yaml(family_results, gate_result)
        logger.info("  Saved: experiment_results.yaml")

        generate_validation_report(family_results, gate_result)
        logger.info("  Saved: 04_validation.md")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return 1

    # Final summary
    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate Type: SHOULD_WORK")
    logger.info(f"Gate Result: {gate_result}")
    logger.info("=" * 60)

    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="H-M3: Geometric vs Scalar Distortion via Brier Decomposition"
    )
    parser.add_argument(
        "--families",
        nargs="+",
        default=FAMILIES,
        help=f"Model families to analyze (default: {FAMILIES})",
    )

    args = parser.parse_args()
    sys.exit(main(args.families))
