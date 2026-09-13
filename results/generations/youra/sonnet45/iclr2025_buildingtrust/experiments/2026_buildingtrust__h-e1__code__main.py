"""Main orchestrator for H-E1: Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)."""

import os
import sys
import json
import yaml
import logging
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODEL_PAIRS, DATASETS, CACHE_DIR, FIGURES_DIR, RESULTS_DIR,
    OUTPUTS_DIR, SEED, GATE_THRESHOLDS,
)
from data_loader import load_all_datasets
from model_runner import run_pair_extraction
from analysis_pipeline import run_full_analysis
from visualization import save_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def save_results(results: dict, results_dir: str) -> str:
    """Serialize results dict to results.yaml and experiment_results.json."""
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Remove non-serializable objects (lr_model, margin_z, flip, kl_div ndarray)
    serializable = {}
    for pair_id, r in results.get("pairs", {}).items():
        s = {k: v for k, v in r.items() if k not in ("lr_model", "margin_z", "flip", "kl_div")}
        serializable[pair_id] = s

    output = {
        "hypothesis_id": "h-e1",
        "timestamp": results["timestamp"],
        "gate_result": results["gate_result"],
        "pairs": serializable,
        "gate_thresholds": GATE_THRESHOLDS,
        "summary": results.get("summary", {}),
    }

    yaml_path = os.path.join(results_dir, "results.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"Results saved to: {yaml_path}")

    # Also save to outputs/results.csv style summary
    json_path = os.path.join(OUTPUTS_DIR, "results.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info(f"Results saved to: {json_path}")

    # Save experiment_results.json at hypothesis level
    hyp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exp_json_path = os.path.join(hyp_dir, "experiment_results.json")
    with open(exp_json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info(f"Experiment results saved to: {exp_json_path}")

    # Save CSV for results.csv
    import csv
    csv_path = os.path.join(OUTPUTS_DIR, "results.csv")
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["pair_id", "method", "base_model", "aligned_model",
                      "n_items", "flip_rate", "beta1", "pvalue_beta1",
                      "auroc_mmlu", "partial_eta2", "pipeline_activated"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for pair_id, r in serializable.items():
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)
    logger.info(f"CSV saved to: {csv_path}")

    return yaml_path


def print_gate_summary(results: dict, thresholds: dict) -> None:
    """Print β₁, p-value, AUROC per pair and PASS/FAIL for each gate criterion."""
    print("\n" + "=" * 70)
    print("GATE SUMMARY: H-E1 — Confidence Margin Predicts Argmax Flip")
    print("=" * 70)
    print(f"{'Pair':<10} {'Method':<6} {'β₁':>8} {'p-value':>10} {'AUROC':>8} {'η²':>8} {'Status'}")
    print("-" * 70)

    gate_passes = []

    for pair_id, r in results.get("pairs", {}).items():
        beta1    = r.get("beta1", float("nan"))
        pval     = r.get("pvalue_beta1", float("nan"))
        auroc    = r.get("auroc_mmlu", float("nan"))
        eta2     = r.get("partial_eta2", float("nan"))
        method   = r.get("method", "?")

        b1_ok    = beta1 < thresholds["beta1_max"]
        pv_ok    = pval  < thresholds["pvalue_max"]
        auroc_ok = auroc >= thresholds["auroc_min"]
        eta_ok   = eta2  >= thresholds["partial_eta2_min"]

        pair_pass = b1_ok and pv_ok and auroc_ok
        gate_passes.append(pair_pass)
        status = "PASS" if pair_pass else "FAIL"

        print(f"{pair_id:<10} {method:<6} {beta1:>8.4f} {pval:>10.5f} {auroc:>8.4f} {eta2:>8.4f} [{status}]")

    print("-" * 70)
    overall = any(gate_passes) if gate_passes else False
    overall_str = "GATE PASS ✓" if overall else "GATE FAIL ✗"
    print(f"\nOverall: {overall_str}")
    print(f"Gate Thresholds: β₁ < {thresholds['beta1_max']}, "
          f"p < {thresholds['pvalue_max']}, "
          f"AUROC ≥ {thresholds['auroc_min']}")

    # Cross-benchmark summary
    print("\nCross-Benchmark AUROC:")
    for pair_id, r in results.get("pairs", {}).items():
        cb = r.get("cross_benchmark", {})
        if cb:
            cb_str = ", ".join(f"{k}={v:.4f}" for k, v in cb.items())
            print(f"  {pair_id}: {cb_str}")

    print("=" * 70)


def main() -> None:
    """Full pipeline: load data, extract logprobs, analyze, visualize, save."""
    import numpy as np
    import random
    import torch

    # Set seeds
    np.random.seed(SEED)
    random.seed(SEED)
    torch.manual_seed(SEED)

    timestamp = datetime.now().isoformat()
    logger.info("=" * 60)
    logger.info("H-E1: Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)")
    logger.info(f"Started: {timestamp}")
    logger.info("=" * 60)

    # Create output directories
    for d in [CACHE_DIR, FIGURES_DIR, RESULTS_DIR, OUTPUTS_DIR]:
        os.makedirs(d, exist_ok=True)

    # Step 1: Load all datasets
    logger.info("\nStep 1: Loading datasets...")
    datasets = load_all_datasets(DATASETS)
    for name, items in datasets.items():
        logger.info(f"  {name}: {len(items)} items")

    # Step 2: Extract logprobs and run analysis per model pair
    all_results = []
    results_by_pair = {}

    for pair_cfg in MODEL_PAIRS:
        pair_id = pair_cfg["pair_id"]
        logger.info(f"\nStep 2: Processing pair {pair_id} ({pair_cfg['base']} + {pair_cfg['aligned']})")

        try:
            # 2a. Extract logprobs (base + aligned) for all 3 benchmarks
            datasets_logprobs = run_pair_extraction(
                pair_cfg, datasets, CACHE_DIR, DATASETS
            )

            # 2b. Run full analysis (margin, flip, KL, logistic regression, AUROC)
            pair_results = run_full_analysis(pair_cfg, datasets_logprobs)
            all_results.append(pair_results)
            results_by_pair[pair_id] = pair_results

            logger.info(f"  β₁={pair_results['beta1']:.4f}, "
                        f"p={pair_results['pvalue_beta1']:.5f}, "
                        f"AUROC={pair_results['auroc_mmlu']:.4f}, "
                        f"η²={pair_results['partial_eta2']:.4f}")
            logger.info(f"  Pipeline activated: {pair_results['pipeline_activated']}")
            logger.info(f"  Cross-benchmark: {pair_results.get('cross_benchmark', {})}")

        except Exception as e:
            logger.error(f"  Error processing pair {pair_id}: {e}")
            import traceback
            traceback.print_exc()
            # Record partial result
            results_by_pair[pair_id] = {
                "pair_id": pair_id, "method": pair_cfg["method"],
                "base_model": pair_cfg["base"], "aligned_model": pair_cfg["aligned"],
                "error": str(e), "beta1": float("nan"), "pvalue_beta1": float("nan"),
                "auroc_mmlu": float("nan"), "partial_eta2": float("nan"),
                "pipeline_activated": False, "cross_benchmark": {},
            }

    if not all_results:
        logger.error("No pairs completed successfully.")
        sys.exit(1)

    # Determine overall gate result
    gate_passes = []
    for r in all_results:
        b1_ok    = r.get("beta1", float("nan")) < GATE_THRESHOLDS["beta1_max"]
        pv_ok    = r.get("pvalue_beta1", 1.0) < GATE_THRESHOLDS["pvalue_max"]
        auroc_ok = r.get("auroc_mmlu", 0.0) >= GATE_THRESHOLDS["auroc_min"]
        gate_passes.append(b1_ok and pv_ok and auroc_ok)

    gate_result = "PASS" if any(gate_passes) else "FAIL"

    # Summary dict
    n_pass = sum(gate_passes)
    results = {
        "timestamp": timestamp,
        "gate_result": gate_result,
        "pairs": results_by_pair,
        "summary": {
            "total_pairs":      len(MODEL_PAIRS),
            "completed_pairs":  len(all_results),
            "gate_pass_pairs":  n_pass,
            "overall_gate":     gate_result,
        },
    }

    # Step 3: Generate and save figures
    logger.info("\nStep 3: Generating figures...")
    try:
        save_all_figures(all_results, FIGURES_DIR)
    except Exception as e:
        logger.warning(f"  Figure generation error (non-fatal): {e}")

    # Step 4: Save results
    logger.info("\nStep 4: Saving results...")
    save_results(results, RESULTS_DIR)

    # Step 5: Print gate summary
    print_gate_summary(results, GATE_THRESHOLDS)

    logger.info(f"\nDone. Gate result: {gate_result}")
    return gate_result


if __name__ == "__main__":
    main()
