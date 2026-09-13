#!/usr/bin/env python3
"""
Run Experiment Orchestrator for H-E1

Top-level script that runs the complete experiment:
1. Train LoRA adapters (or skip if already trained)
2. Compute Grassmann distances
3. Run statistical analysis
4. Generate figures
5. Print gate pass/fail summary
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Add code directory to path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

from config import (
    HYPOTHESIS_FOLDER,
    ADAPTER_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    ANALYSIS_CONFIG,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(skip_training: bool = False, hypothesis_folder: str = None) -> dict:
    """
    Run the complete H-E1 experiment.

    Args:
        skip_training: If True, skip training and use existing adapters
        hypothesis_folder: Override hypothesis folder path

    Returns:
        Dict with experiment results and gate status
    """
    if hypothesis_folder is None:
        hypothesis_folder = HYPOTHESIS_FOLDER

    logger.info("=" * 70)
    logger.info("H-E1: LoRA Adapter Geometric Signatures Existence Proof")
    logger.info("=" * 70)
    logger.info(f"Hypothesis folder: {hypothesis_folder}")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("")

    results = {
        "hypothesis_id": "h-e1",
        "start_time": datetime.now().isoformat(),
        "steps": {},
        "gate_result": None,
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 1: Training Pipeline
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("STEP 1: LoRA Adapter Training")
    logger.info("-" * 50)

    if skip_training:
        logger.info("Skipping training (--skip-training flag set)")
        # Check if adapters exist
        adapter_dir = os.path.join(hypothesis_folder, "adapters")
        if os.path.exists(adapter_dir):
            adapter_count = len([d for d in os.listdir(adapter_dir) if "_seed" in d])
            logger.info(f"Found {adapter_count} existing adapters")
            results["steps"]["training"] = {"status": "skipped", "adapter_count": adapter_count}
        else:
            logger.error("No adapters found! Run without --skip-training first.")
            results["steps"]["training"] = {"status": "error", "message": "No adapters found"}
            return results
    else:
        from train import run_training_pipeline
        try:
            metadata = run_training_pipeline(hypothesis_folder)
            results["steps"]["training"] = {
                "status": "completed",
                "adapter_count": len(metadata),
            }
            logger.info(f"Training complete: {len(metadata)} adapters")
        except Exception as e:
            logger.error(f"Training failed: {e}")
            results["steps"]["training"] = {"status": "error", "message": str(e)}
            raise

    logger.info("")

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 2: Analysis (Grassmann Distance + Statistics)
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("STEP 2: Grassmann Distance Analysis")
    logger.info("-" * 50)

    from analyze import run_analysis
    import numpy as np

    try:
        stats = run_analysis(hypothesis_folder)
        results["steps"]["analysis"] = {
            "status": "completed",
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        results["steps"]["analysis"] = {"status": "error", "message": str(e)}
        raise

    logger.info("")

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 3: Visualization
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("STEP 3: Figure Generation")
    logger.info("-" * 50)

    from visualize import generate_all_figures

    try:
        results_dir = os.path.join(hypothesis_folder, "results")
        distance_matrix = np.load(os.path.join(results_dir, "pairwise_distances.npy"))
        with open(os.path.join(results_dir, "adapter_metadata.json")) as f:
            adapter_meta = json.load(f)

        generate_all_figures(hypothesis_folder, stats, distance_matrix, adapter_meta)
        results["steps"]["visualization"] = {"status": "completed"}
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        results["steps"]["visualization"] = {"status": "error", "message": str(e)}
        # Non-fatal - continue to gate check

    logger.info("")

    # ═══════════════════════════════════════════════════════════════════════════
    # Step 4: Gate Check (MUST_WORK)
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("STEP 4: MUST_WORK Gate Evaluation")
    logger.info("-" * 50)

    p_threshold = ANALYSIS_CONFIG["p_threshold"]
    d_threshold = ANALYSIS_CONFIG["cohens_d_threshold"]

    gate_checks = {
        "p_value_check": stats["p_value"] < p_threshold,
        "cohens_d_check": stats["cohens_d"] > d_threshold,
        "effect_direction_check": stats["within_mean"] < stats["between_mean"],
    }

    gate_passed = all(gate_checks.values())

    results["gate_result"] = {
        "passed": gate_passed,
        "checks": gate_checks,
        "criteria": {
            "p_threshold": p_threshold,
            "cohens_d_threshold": d_threshold,
        },
        "values": {
            "p_value": stats["p_value"],
            "cohens_d": stats["cohens_d"],
            "within_mean": stats["within_mean"],
            "between_mean": stats["between_mean"],
        }
    }

    # Print gate summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("GATE EVALUATION SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"  Gate Type: MUST_WORK")
    logger.info("")
    logger.info("  Criteria Checks:")
    logger.info(f"    [{'PASS' if gate_checks['effect_direction_check'] else 'FAIL'}] Effect Direction: within_mean ({stats['within_mean']:.4f}) < between_mean ({stats['between_mean']:.4f})")
    logger.info(f"    [{'PASS' if gate_checks['p_value_check'] else 'FAIL'}] P-Value: {stats['p_value']:.6f} < {p_threshold}")
    logger.info(f"    [{'PASS' if gate_checks['cohens_d_check'] else 'FAIL'}] Cohen's d: {stats['cohens_d']:.4f} > {d_threshold}")
    logger.info("")
    logger.info(f"  95% CI for (between - within): [{stats['ci_95'][0]:.4f}, {stats['ci_95'][1]:.4f}]")
    logger.info("")

    if gate_passed:
        logger.info("  ╔════════════════════════════════════════════════════════════════╗")
        logger.info("  ║                      GATE: PASSED                              ║")
        logger.info("  ╚════════════════════════════════════════════════════════════════╝")
    else:
        logger.info("  ╔════════════════════════════════════════════════════════════════╗")
        logger.info("  ║                      GATE: FAILED                              ║")
        logger.info("  ╚════════════════════════════════════════════════════════════════╝")

    logger.info("")
    logger.info("=" * 70)

    # Save results
    results["end_time"] = datetime.now().isoformat()

    results_file = os.path.join(hypothesis_folder, "experiment_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to: {results_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run H-E1 Experiment")
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training step (use existing adapters)"
    )
    parser.add_argument(
        "--hypothesis-folder",
        type=str,
        default=None,
        help="Override hypothesis folder path"
    )

    args = parser.parse_args()

    try:
        results = main(
            skip_training=args.skip_training,
            hypothesis_folder=args.hypothesis_folder
        )
        sys.exit(0 if results["gate_result"]["passed"] else 1)
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        sys.exit(2)
