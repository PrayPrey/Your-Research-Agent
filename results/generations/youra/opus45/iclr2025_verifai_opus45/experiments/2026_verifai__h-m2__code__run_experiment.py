#!/usr/bin/env python3
"""Entry point for H-M2 experiment: G3 Superiority Over Minimal Feedback.

This script runs the post-hoc statistical analysis comparing G3 vs G0 repair success.
It loads results from H-M1 and performs McNemar's test for paired binary outcomes.

Expected Result: FAIL - G0 significantly outperforms G3 (opposite of hypothesis)

Usage:
    python run_experiment.py

Output:
    - results/comparison_results.json - Full analysis results
    - results/metrics.yaml - Key metrics summary
    - figures/*.png - Visualization figures
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from analyze import main


def setup_logging(log_file: str = "experiment.log") -> logging.Logger:
    """Set up logging to file and console."""
    logger = logging.getLogger("h-m2")
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def run_experiment() -> dict:
    """Run the H-M2 experiment and return results."""
    # Setup
    logger = setup_logging()
    logger.info("Starting H-M2 experiment: G3 Superiority Over Minimal Feedback")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    # Initialize config
    config = Config()
    logger.info(f"H-M1 results path: {config.h_m1_results_path}")
    logger.info(f"Expected pairs: {config.expected_n_pairs}")
    logger.info(f"Difference threshold: {config.difference_threshold * 100}pp")

    # Verify H-M1 data exists
    if not os.path.exists(config.h_m1_results_path):
        logger.error(f"H-M1 results not found: {config.h_m1_results_path}")
        raise FileNotFoundError(f"H-M1 results not found: {config.h_m1_results_path}")

    # Run analysis
    try:
        results = main(config)
        logger.info(f"Analysis complete. Gate result: {results['gate']['verdict']}")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

    # Log key metrics
    logger.info(f"G0 success rate: {results['rates']['g0_rate']*100:.1f}%")
    logger.info(f"G3 success rate: {results['rates']['g3_rate']*100:.1f}%")
    logger.info(f"Difference (G3-G0): {results['rates']['difference_pp']:+.1f}pp")
    logger.info(f"McNemar p-value: {results['mcnemar']['pvalue']:.2e}")
    logger.info(f"Gate passed: {results['gate']['gate_passed']}")

    return results


if __name__ == "__main__":
    try:
        results = run_experiment()
        sys.exit(0 if results["gate"]["verdict"] in ["PASS", "FAIL"] else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
