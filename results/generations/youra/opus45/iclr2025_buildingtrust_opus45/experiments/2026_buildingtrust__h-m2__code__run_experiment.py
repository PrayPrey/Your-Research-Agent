#!/usr/bin/env python3
"""
Main orchestrator for H-M2 Percentile-Normalized Monotonicity Attenuation Analysis.

Statistical reanalysis of H-E1 cached data to test whether instruction tuning
attenuates the percentile-normalized confidence-correctness relationship (β_percentile).
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
    H_E1_CACHE_DIR, ensure_directories, GATE_TYPE, BOOTSTRAP_N
)
from data_loader import load_family_arrays, validate_arrays, load_all_families
from analysis import analyze_family, run_2x2_analysis
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
    Main experiment pipeline:
    1. Ensure output directories exist
    2. Load and validate data from H-E1 cache
    3. Run per-family analysis (zscore → β → bootstrap CI → diff test → gate)
    4. Run 2x2 analysis (family × model_type)
    5. Generate figures
    6. Evaluate gate and generate reports
    7. Return exit code (0=PASS, 1=FAIL)

    Args:
        families: List of model families to analyze (default: FAMILIES from config)

    Returns:
        Exit code: 0 if gate PASS, 1 if gate FAIL
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("H-M2: Percentile-Normalized Monotonicity Attenuation Analysis")
    logger.info("=" * 60)

    if families is None:
        families = FAMILIES

    # 1. Setup
    logger.info("Step 1: Setting up directories and seed...")
    ensure_directories()
    set_seed()

    logger.info(f"  H-E1 cache: {H_E1_CACHE_DIR}")
    logger.info(f"  Figures: {FIGURES_DIR}")
    logger.info(f"  Families: {families}")
    logger.info(f"  Bootstrap iterations: {BOOTSTRAP_N}")

    # 2. Load data
    logger.info("Step 2: Loading and validating data from H-E1 cache...")
    arrays_by_family = {}

    for family in families:
        logger.info(f"  Loading {family}...")
        try:
            arrays = load_family_arrays(family)
            validate_arrays(arrays)
            arrays_by_family[family] = arrays
            n = len(arrays["base_margins"])
            logger.info(f"    ✓ {family}: {n} samples loaded and validated")
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"    ✗ {family}: {e}")
            return 1

    # 3. Run per-family analysis
    logger.info("Step 3: Running per-family analysis...")
    family_results = {}

    for family in families:
        logger.info(f"  Analyzing {family}...")
        result = analyze_family(family, arrays_by_family[family])
        family_results[family] = result

        logger.info(f"    β_base: {result['base_beta']:.4f} [{result['base_ci'][1]:.4f}, {result['base_ci'][2]:.4f}]")
        logger.info(f"    β_inst: {result['inst_beta']:.4f} [{result['inst_ci'][1]:.4f}, {result['inst_ci'][2]:.4f}]")
        logger.info(f"    Δβ: {result['delta_beta']:.4f}, p={result['p_value']:.4f}")
        logger.info(f"    Gate: {'PASS' if result['gate_pass'] else 'FAIL'}")

    # 4. Run 2x2 analysis
    logger.info("Step 4: Running 2x2 analysis...")
    analysis_2x2 = run_2x2_analysis(arrays_by_family)
    for family, betas in analysis_2x2.items():
        logger.info(f"  {family}: base={betas['base']:.4f}, instruct={betas['instruct']:.4f}")

    # 5. Generate figures
    logger.info("Step 5: Generating figures...")
    figure_paths = save_all_figures(family_results, arrays_by_family)
    for path in figure_paths:
        logger.info(f"  ✓ Saved: {path}")

    # 6. Evaluate gate and generate reports
    logger.info("Step 6: Evaluating gate and generating reports...")
    gate_result = evaluate_gate(family_results)

    logger.info(f"  Gate type: {GATE_TYPE}")
    logger.info(f"  Gate result: {gate_result}")

    # Save YAML results
    save_experiment_results_yaml(family_results, gate_result)
    logger.info(f"  ✓ Saved: experiment_results.yaml")

    # Generate validation report
    generate_validation_report(family_results, gate_result)
    logger.info(f"  ✓ Saved: 04_validation.md")

    # 7. Summary
    elapsed = datetime.now() - start_time
    logger.info("=" * 60)
    logger.info(f"Experiment completed in {elapsed.total_seconds():.2f} seconds")
    logger.info(f"Gate Result: {gate_result}")
    logger.info("=" * 60)

    # Return exit code
    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="H-M2: Percentile-Normalized Monotonicity Attenuation Analysis"
    )
    parser.add_argument(
        "--families",
        nargs="+",
        default=None,
        help="Model families to analyze (default: qwen mistral)"
    )
    args = parser.parse_args()

    exit_code = main(families=args.families)
    sys.exit(exit_code)
