#!/usr/bin/env python3
"""
Main orchestrator for H-E1 AUROC Discriminative Degradation Analysis.

Runs inference on base vs instruct model pairs, computes AUROC metrics,
and generates validation report.
"""

import os
import sys
import json
import yaml
import logging
import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

# Add code directory to path
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    SEED, MODEL_PAIRS, CACHE_DIR, RESULTS_DIR, FIGURES_DIR,
    OUTPUTS_DIR, ensure_directories, GATE_TYPE
)
from data import load_mmlu_test
from inference import run_model_inference, unload_model
from metrics import (
    compute_auroc_with_ci, compute_conditional_margins,
    compute_i2_statistic, evaluate_gate_criteria
)
from visualize import save_all_figures

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
    """Set random seeds for reproducibility."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_or_run_inference(
    family: str,
    variant: str,
    model_id: str,
    dataset,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load cached results or run inference.

    Args:
        family: Model family name (qwen, llama, mistral)
        variant: Model variant (base, instruct)
        model_id: HuggingFace model ID
        dataset: MMLU dataset

    Returns:
        (margins, correctness) arrays
    """
    cache_path = str(CACHE_DIR / family)
    return run_model_inference(model_id, dataset, cache_path)


def run_family(family: str, dataset) -> dict:
    """
    Run evaluation for one model family.

    Args:
        family: Model family name
        dataset: MMLU dataset

    Returns:
        Dict with base and instruct results
    """
    base_id, instruct_id = MODEL_PAIRS[family]
    family_results = {}

    # Run base model
    logger.info(f"Running {family} base model: {base_id}")
    base_margins, base_correct = load_or_run_inference(family, "base", base_id, dataset)
    base_auroc = compute_auroc_with_ci(base_margins, base_correct)
    base_cond = compute_conditional_margins(base_margins, base_correct)

    family_results["base"] = {
        **base_auroc,
        **base_cond,
        "model_id": base_id,
        "n_samples": len(base_margins),
        "accuracy": float(np.mean(base_correct)),
    }

    # Run instruct model
    logger.info(f"Running {family} instruct model: {instruct_id}")
    inst_margins, inst_correct = load_or_run_inference(family, "instruct", instruct_id, dataset)
    inst_auroc = compute_auroc_with_ci(inst_margins, inst_correct)
    inst_cond = compute_conditional_margins(inst_margins, inst_correct)

    family_results["instruct"] = {
        **inst_auroc,
        **inst_cond,
        "model_id": instruct_id,
        "n_samples": len(inst_margins),
        "accuracy": float(np.mean(inst_correct)),
    }

    # Compute delta
    delta = base_auroc["auroc"] - inst_auroc["auroc"]
    family_results["delta"] = {
        "auroc_diff": delta,
        "direction": "degraded" if delta > 0 else "improved",
    }

    # Store raw data for visualization
    family_results["_margins_base"] = base_margins
    family_results["_margins_instruct"] = inst_margins
    family_results["_correct_base"] = base_correct
    family_results["_correct_instruct"] = inst_correct

    logger.info(f"{family}: Base AUROC={base_auroc['auroc']:.4f}, Instruct AUROC={inst_auroc['auroc']:.4f}, Delta={delta:.4f}")

    return family_results


def save_results(all_results: dict, results_dir: Path) -> str:
    """
    Save results to YAML and CSV files.

    Args:
        all_results: Complete results dict
        results_dir: Directory for output files

    Returns:
        Path to results YAML file
    """
    results_dir.mkdir(parents=True, exist_ok=True)

    # Prepare serializable results (remove numpy arrays)
    serializable = {}
    for family, data in all_results.items():
        if family.startswith("_"):
            continue
        serializable[family] = {
            k: v for k, v in data.items()
            if not k.startswith("_") and not isinstance(v, np.ndarray)
        }

    # Save YAML
    yaml_path = results_dir / "auroc_results.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(serializable, f, default_flow_style=False)

    # Save CSV summary
    csv_path = OUTPUTS_DIR / "results.csv"
    with open(csv_path, "w") as f:
        f.write("family,variant,auroc,ci_lower,ci_upper,accuracy,n_samples\n")
        for family in ["qwen", "llama", "mistral"]:
            if family not in all_results:
                continue
            for variant in ["base", "instruct"]:
                data = all_results[family][variant]
                f.write(f"{family},{variant},{data['auroc']:.4f},{data['ci_lower']:.4f},"
                       f"{data['ci_upper']:.4f},{data['accuracy']:.4f},{data['n_samples']}\n")

    logger.info(f"Results saved to: {yaml_path}")
    logger.info(f"CSV saved to: {csv_path}")

    return str(yaml_path)


def save_experiment_results_json(all_results: dict, gate_results: dict) -> str:
    """
    Save structured experiment results for Phase 5/6 consumption.

    Args:
        all_results: Complete results dict
        gate_results: Gate evaluation results

    Returns:
        Path to experiment_results.json
    """
    hypothesis_dir = CODE_DIR.parent
    json_path = hypothesis_dir / "experiment_results.json"

    # Build structured output
    experiment_results = {
        "hypothesis_id": "h-e1",
        "hypothesis_type": "EXISTENCE",
        "experiment_date": datetime.now().isoformat(),
        "gate": {
            "type": GATE_TYPE,
            "result": "PASS" if gate_results.get("all_pass", False) else "FAIL",
            "per_family": {k: bool(v) for k, v in gate_results.items() if k != "all_pass"},
        },
        "metrics": {},
        "summary": {},
    }

    # Add per-family metrics
    for family in ["qwen", "llama", "mistral"]:
        if family not in all_results:
            continue
        base = all_results[family]["base"]
        inst = all_results[family]["instruct"]
        experiment_results["metrics"][family] = {
            "base_auroc": base["auroc"],
            "base_auroc_ci": [base["ci_lower"], base["ci_upper"]],
            "instruct_auroc": inst["auroc"],
            "instruct_auroc_ci": [inst["ci_lower"], inst["ci_upper"]],
            "delta": base["auroc"] - inst["auroc"],
            "base_accuracy": base["accuracy"],
            "instruct_accuracy": inst["accuracy"],
        }

    # Compute summary statistics
    deltas = [experiment_results["metrics"][f]["delta"] for f in ["qwen", "llama", "mistral"] if f in experiment_results["metrics"]]
    experiment_results["summary"] = {
        "mean_delta": float(np.mean(deltas)) if deltas else 0.0,
        "all_families_degraded": bool(all(d > 0 for d in deltas)),
        "families_tested": len(deltas),
    }

    with open(json_path, "w") as f:
        json.dump(experiment_results, f, indent=2)

    logger.info(f"Experiment results saved to: {json_path}")
    return str(json_path)


def generate_validation_report(
    all_results: dict,
    gate_results: dict,
    output_path: Path,
) -> None:
    """
    Generate 04_validation.md report.

    Args:
        all_results: Complete results dict
        gate_results: Gate evaluation results
        output_path: Path for report file
    """
    report_lines = [
        "# Validation Report: H-E1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Gate Type:** {GATE_TYPE}",
        f"**Gate Result:** {'PASS' if gate_results.get('all_pass', False) else 'FAIL'}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Family | Base AUROC | Instruct AUROC | Delta | Gate Pass |",
        "|--------|-----------|----------------|-------|-----------|",
    ]

    for family in ["qwen", "llama", "mistral"]:
        if family not in all_results:
            report_lines.append(f"| {family.capitalize()} | N/A | N/A | N/A | N/A |")
            continue

        base = all_results[family]["base"]
        inst = all_results[family]["instruct"]
        delta = base["auroc"] - inst["auroc"]
        gate_pass = "PASS" if gate_results.get(family, False) else "FAIL"

        report_lines.append(
            f"| {family.capitalize()} | "
            f"{base['auroc']:.4f} [{base['ci_lower']:.4f}, {base['ci_upper']:.4f}] | "
            f"{inst['auroc']:.4f} [{inst['ci_lower']:.4f}, {inst['ci_upper']:.4f}] | "
            f"{delta:+.4f} | {gate_pass} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## Detailed Results",
        "",
    ])

    for family in ["qwen", "llama", "mistral"]:
        if family not in all_results:
            continue

        base = all_results[family]["base"]
        inst = all_results[family]["instruct"]

        report_lines.extend([
            f"### {family.capitalize()}",
            "",
            f"**Base Model:** `{base['model_id']}`",
            f"- AUROC: {base['auroc']:.4f} (95% CI: [{base['ci_lower']:.4f}, {base['ci_upper']:.4f}])",
            f"- Accuracy: {base['accuracy']:.4f}",
            f"- Mean Margin (Correct): {base['mean_correct']:.4f}",
            f"- Mean Margin (Incorrect): {base['mean_incorrect']:.4f}",
            f"- N samples: {base['n_samples']}",
            "",
            f"**Instruct Model:** `{inst['model_id']}`",
            f"- AUROC: {inst['auroc']:.4f} (95% CI: [{inst['ci_lower']:.4f}, {inst['ci_upper']:.4f}])",
            f"- Accuracy: {inst['accuracy']:.4f}",
            f"- Mean Margin (Correct): {inst['mean_correct']:.4f}",
            f"- Mean Margin (Incorrect): {inst['mean_incorrect']:.4f}",
            f"- N samples: {inst['n_samples']}",
            "",
        ])

    report_lines.extend([
        "---",
        "",
        "## Gate Evaluation",
        "",
        f"**Gate Type:** {GATE_TYPE}",
        "",
        "**Criteria:**",
        "1. AUROC_base > AUROC_instruct for all families",
        "2. 95% CI of delta excludes zero",
        "",
        "**Per-Family Results:**",
    ])

    for family in ["qwen", "llama", "mistral"]:
        status = "PASS" if gate_results.get(family, False) else "FAIL"
        report_lines.append(f"- {family.capitalize()}: {status}")

    overall = "PASS" if gate_results.get("all_pass", False) else "FAIL"
    report_lines.extend([
        "",
        f"**Overall Gate Result:** {overall}",
        "",
        "---",
        "",
        "## Figures",
        "",
        "- `figures/auroc_comparison.png` - Bar chart comparing base vs instruct AUROC",
        "- `figures/margin_distributions.png` - KDE plots of margin distributions",
        "- `figures/forest_plot.png` - Forest plot of AUROC deltas",
        "",
        "---",
        "",
        "*Generated by Phase 4 run_experiment.py*",
    ])

    with open(output_path, "w") as f:
        f.write("\n".join(report_lines))

    logger.info(f"Validation report saved to: {output_path}")


def main(families: list[str] = None) -> None:
    """
    Main orchestrator.

    Args:
        families: List of families to run (default: all)
    """
    logger.info("=" * 60)
    logger.info("H-E1 AUROC Discriminative Degradation Analysis")
    logger.info("=" * 60)

    # Setup
    set_seed()
    ensure_directories()

    if families is None:
        families = list(MODEL_PAIRS.keys())

    # Load dataset
    logger.info("Loading MMLU dataset...")
    dataset = load_mmlu_test()
    logger.info(f"Dataset loaded: {len(dataset)} samples")

    # Run each family
    all_results = {}
    margins_by_model = {}
    correctness_by_model = {}

    for family in families:
        if family not in MODEL_PAIRS:
            logger.warning(f"Unknown family: {family}, skipping")
            continue

        logger.info(f"\n{'='*40}")
        logger.info(f"Processing family: {family}")
        logger.info(f"{'='*40}")

        family_results = run_family(family, dataset)
        all_results[family] = family_results

        # Store margins for visualization
        base_id, inst_id = MODEL_PAIRS[family]
        margins_by_model[base_id] = family_results["_margins_base"]
        margins_by_model[inst_id] = family_results["_margins_instruct"]
        correctness_by_model[base_id] = family_results["_correct_base"]
        correctness_by_model[inst_id] = family_results["_correct_instruct"]

    # Evaluate gate
    logger.info("\nEvaluating gate criteria...")
    gate_results = evaluate_gate_criteria(all_results)

    logger.info(f"Gate Results:")
    for family, passed in gate_results.items():
        logger.info(f"  {family}: {'PASS' if passed else 'FAIL'}")

    # Save results
    save_results(all_results, RESULTS_DIR)
    save_experiment_results_json(all_results, gate_results)

    # Generate figures
    logger.info("\nGenerating figures...")
    save_all_figures(all_results, margins_by_model, correctness_by_model, str(FIGURES_DIR))

    # Generate validation report
    hypothesis_dir = CODE_DIR.parent
    generate_validation_report(all_results, gate_results, hypothesis_dir / "04_validation.md")

    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate Result: {'PASS' if gate_results.get('all_pass', False) else 'FAIL'}")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 AUROC Experiment")
    parser.add_argument("--families", nargs="+", default=None,
                       help="Model families to evaluate (default: all)")
    args = parser.parse_args()

    main(families=args.families)
