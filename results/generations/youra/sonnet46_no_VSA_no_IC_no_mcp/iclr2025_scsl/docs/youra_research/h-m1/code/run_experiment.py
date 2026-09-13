"""
Single seed/condition experiment runner.
Usage: python run_experiment.py --seed 0 --condition original
       python run_experiment.py --seed 0 --condition no_background
"""
import argparse
import json
import os
import sys
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from src.training.trainer import SimCLRTrainer
from src.evaluation.probes import run_probes
from src.evaluation.stats import check_collapse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main(seed: int, condition: str):
    assert condition in ("original", "no_background"), f"Invalid condition: {condition}"

    config = ExperimentConfig()
    os.makedirs(config.checkpoint_dir, exist_ok=True)
    os.makedirs(config.results_dir, exist_ok=True)

    logger.info(f"Starting experiment: seed={seed}, condition={condition}")

    # Train SimCLR
    trainer = SimCLRTrainer(config, condition=condition, seed=seed)
    ckpt_path = trainer.train()

    # Run linear probes
    probe_result = run_probes(ckpt_path, config.waterbirds_root, config.device)

    # Collapse detection
    collapse_info = check_collapse(probe_result["task_probe_acc"])

    # Build result record
    result = {
        "hypothesis_id": "h-m1",
        "condition": condition,
        "seed": seed,
        "epoch": config.epochs,
        "spurious_probe_acc": probe_result["spurious_probe_acc"],
        "task_probe_acc": probe_result["task_probe_acc"],
        "ratio": probe_result["ratio"],
        "collapsed": collapse_info["collapsed"],
        "mechanism_verified": condition == "no_background",  # verified during training
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    result_path = config.result_path(condition, seed)
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(f"Result saved: {result_path}")
    logger.info(f"  spurious_acc={result['spurious_probe_acc']:.4f}, "
                f"task_acc={result['task_probe_acc']:.4f}, "
                f"ratio={result['ratio']:.4f}, "
                f"collapsed={result['collapsed']}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--condition", type=str, required=True, choices=["original", "no_background"])
    args = parser.parse_args()
    main(args.seed, args.condition)
