"""
run_experiment.py — H-M1: Attention Entropy Mechanistic Analysis.

Usage:
    CUDA_VISIBLE_DEVICES=1 python run_experiment.py [--smoke-test] [--model llama2|mistral]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ.setdefault("WANDB_DISABLED", "true")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch

from config import get_experiment_config, validate_config, ExperimentConfig
from evaluate import run_evaluation
from visualize import generate_all_figures

_H_M1_CODE = Path(__file__).resolve().parent   # h-m1/code/
_H_M1_DIR = _H_M1_CODE.parent                  # h-m1/
FIGURES_DIR = str(_H_M1_DIR / "figures")
OUTPUTS_DIR = str(_H_M1_CODE / "outputs")
RESULTS_PATH = str(_H_M1_DIR / "experiment_results.json")
LOG_PATH = str(_H_M1_CODE / "experiment.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH),
    ],
)
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="H-M1 Attention Entropy Experiment")
    p.add_argument("--smoke-test", action="store_true",
                   help="Run with minimal samples for quick validation")
    p.add_argument("--model", choices=["llama2", "mistral", "both"], default="both",
                   help="Which model pair to evaluate")
    p.add_argument("--gpu", type=int, default=None,
                   help="GPU index to use (overrides CUDA_VISIBLE_DEVICES)")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("=" * 60)
    logger.info("H-M1 EXPERIMENT: Attention Entropy Mechanistic Analysis")
    logger.info("=" * 60)
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info(f"Device: {device}")
    if device == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Load and optionally filter config
    exp_cfg = get_experiment_config()

    if args.smoke_test:
        logger.info("SMOKE TEST MODE: using min_samples_per_category=5")
        exp_cfg.min_samples_per_category = 5

    if args.model == "llama2":
        exp_cfg.models = exp_cfg.models[:2]
    elif args.model == "mistral":
        exp_cfg.models = exp_cfg.models[2:]

    try:
        validate_config(exp_cfg)
    except AssertionError as e:
        logger.error(f"Config validation failed: {e}")
        sys.exit(1)

    # Run evaluation
    logger.info("Starting evaluation pipeline...")
    results = run_evaluation(exp_cfg, device)

    # Save results
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

    # Build serializable results (remove aggregator objects)
    save_results = {
        "hypothesis_id": "h-m1",
        "gate_result": "PASS" if results["gate_passed"] else "FAIL",
        "gate_type": "MUST_WORK",
        "fraction_significant": results["fraction_significant"],
        "models": [
            {
                "model_label": m["model_label"],
                "gate_passed": m["gate"]["passed"],
                "fraction_significant": m["gate"]["fraction_significant"],
                "significant_layers": m["gate"]["significant_layers"],
                "summary": m["summary"],
            }
            for m in results["models"]
        ],
        "timestamp": datetime.now().isoformat(),
        "smoke_test": args.smoke_test,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(save_results, f, indent=2)
    logger.info(f"Results saved: {RESULTS_PATH}")

    # Generate figures
    logger.info("Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    try:
        saved_figs = generate_all_figures(results["models"], FIGURES_DIR)
        logger.info(f"Generated {len(saved_figs)} figures in {FIGURES_DIR}")
    except Exception as e:
        logger.warning(f"Figure generation failed: {e}")

    # Summary
    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate Result: {'PASS' if results['gate_passed'] else 'FAIL'}")
    logger.info(f"Fraction significant layers: {results['fraction_significant']:.3f}")
    for m in results["models"]:
        logger.info(
            f"  {m['model_label']}: {'PASS' if m['gate']['passed'] else 'FAIL'} "
            f"({m['gate']['fraction_significant']*100:.1f}% significant)"
        )
    logger.info(f"Results: {RESULTS_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
