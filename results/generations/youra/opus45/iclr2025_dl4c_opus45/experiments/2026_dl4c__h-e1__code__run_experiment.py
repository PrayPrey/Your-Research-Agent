#!/usr/bin/env python3
"""End-to-end orchestration for H-E1: Alignment-Induced Error Type Divergence experiment."""

import json
import os
import sys
import logging
from datetime import datetime

import numpy as np

from config import CONFIG, ExperimentConfig
from data_loader import load_combined_dataset
from generate import load_rl_model, load_dpo_model, generate_samples, save_samples, load_samples
from execute import execute_all_samples, save_execution_results, load_execution_results
from analyze import run_analysis, build_contingency_table
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


def main(config: ExperimentConfig) -> None:
    """End-to-end pipeline.

    1. load_combined_dataset() -> problems
    2. load_rl_model() + generate_samples() -> save_samples("outputs/samples_rl.jsonl")
    3. load_dpo_model() + generate_samples() -> save_samples("outputs/samples_dpo.jsonl")
    4. execute_all_samples(rl_samples, problems) -> rl_results
    5. execute_all_samples(dpo_samples, problems) -> dpo_results
    6. run_analysis(rl_results, dpo_results, config) -> metrics
    7. generate_all_figures(metrics, contingency, rl_results, dpo_results, config)
    8. Print gate_pass summary: PASS/FAIL with chi2, p_value, cramers_v
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("H-E1: Alignment-Induced Error Type Divergence Experiment")
    logger.info("=" * 60)

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # ======================================================================
    # Step 1: Load Dataset
    # ======================================================================
    logger.info("\n[Step 1] Loading datasets...")
    problems = load_combined_dataset()
    problems_dict = {p["task_id"]: p for p in problems}
    logger.info(f"Loaded {len(problems)} problems")

    # ======================================================================
    # Step 2: Generate RL samples (or load cached)
    # ======================================================================
    rl_samples_path = os.path.join(config.output_dir, "samples_rl.jsonl")
    if os.path.exists(rl_samples_path):
        logger.info(f"\n[Step 2] Loading cached RL samples from {rl_samples_path}")
        rl_samples = load_samples(rl_samples_path)
    else:
        logger.info("\n[Step 2] Generating RL samples...")
        rl_model, rl_tokenizer = load_rl_model(config)
        rl_samples = generate_samples(rl_model, rl_tokenizer, problems, "rl", config)
        save_samples(rl_samples, rl_samples_path)
        # Free memory
        del rl_model, rl_tokenizer
        import torch
        torch.cuda.empty_cache()
    logger.info(f"RL samples: {len(rl_samples)}")

    # ======================================================================
    # Step 3: Generate DPO samples (or load cached)
    # ======================================================================
    dpo_samples_path = os.path.join(config.output_dir, "samples_dpo.jsonl")
    if os.path.exists(dpo_samples_path):
        logger.info(f"\n[Step 3] Loading cached DPO samples from {dpo_samples_path}")
        dpo_samples = load_samples(dpo_samples_path)
    else:
        logger.info("\n[Step 3] Generating DPO samples...")
        dpo_model, dpo_tokenizer = load_dpo_model(config)
        dpo_samples = generate_samples(dpo_model, dpo_tokenizer, problems, "dpo", config)
        save_samples(dpo_samples, dpo_samples_path)
        # Free memory
        del dpo_model, dpo_tokenizer
        import torch
        torch.cuda.empty_cache()
    logger.info(f"DPO samples: {len(dpo_samples)}")

    # ======================================================================
    # Step 4: Execute RL samples (or load cached)
    # ======================================================================
    rl_results_path = os.path.join(config.output_dir, "rl_execution_results.json")
    if os.path.exists(rl_results_path):
        logger.info(f"\n[Step 4] Loading cached RL execution results from {rl_results_path}")
        rl_results = load_execution_results(rl_results_path)
    else:
        logger.info("\n[Step 4] Executing RL samples...")
        rl_results = execute_all_samples(rl_samples, problems_dict, config.timeout)
        save_execution_results(rl_results, rl_results_path)
    rl_pass = sum(1 for r in rl_results if r["status"] == "pass")
    logger.info(f"RL execution: {rl_pass}/{len(rl_results)} pass ({100*rl_pass/len(rl_results):.1f}%)")

    # ======================================================================
    # Step 5: Execute DPO samples (or load cached)
    # ======================================================================
    dpo_results_path = os.path.join(config.output_dir, "dpo_execution_results.json")
    if os.path.exists(dpo_results_path):
        logger.info(f"\n[Step 5] Loading cached DPO execution results from {dpo_results_path}")
        dpo_results = load_execution_results(dpo_results_path)
    else:
        logger.info("\n[Step 5] Executing DPO samples...")
        dpo_results = execute_all_samples(dpo_samples, problems_dict, config.timeout)
        save_execution_results(dpo_results, dpo_results_path)
    dpo_pass = sum(1 for r in dpo_results if r["status"] == "pass")
    logger.info(f"DPO execution: {dpo_pass}/{len(dpo_results)} pass ({100*dpo_pass/len(dpo_results):.1f}%)")

    # ======================================================================
    # Step 6: Run analysis
    # ======================================================================
    logger.info("\n[Step 6] Running statistical analysis...")
    metrics = run_analysis(rl_results, dpo_results, config)

    # ======================================================================
    # Step 7: Generate figures
    # ======================================================================
    logger.info("\n[Step 7] Generating figures...")
    contingency = np.array(metrics["contingency_table"])
    generate_all_figures(metrics, contingency, rl_results, dpo_results, config)

    # ======================================================================
    # Step 8: Print summary
    # ======================================================================
    duration = datetime.now() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT RESULTS")
    logger.info("=" * 60)
    logger.info(f"Chi-square: {metrics['chi2']:.4f}")
    logger.info(f"P-value: {metrics['p_value']:.6f} (threshold: < {config.chi2_p_threshold})")
    logger.info(f"Cramér's V: {metrics['cramers_v']:.4f} (threshold: > {config.cramers_v_threshold})")
    logger.info(f"Direction matches prediction: {metrics['direction_matches']}")
    logger.info(f"  RL syntax+runtime prop: {metrics['rl_syntax_runtime_prop']:.4f}")
    logger.info(f"  DPO syntax+runtime prop: {metrics['dpo_syntax_runtime_prop']:.4f}")
    logger.info("-" * 60)

    if metrics["gate_pass"]:
        logger.info("🎉 GATE RESULT: PASS")
        logger.info("Effect exists: chi-square significant and effect size meaningful")
    else:
        logger.info("❌ GATE RESULT: FAIL")
        if metrics["p_value"] >= config.chi2_p_threshold:
            logger.info(f"  - p-value {metrics['p_value']:.4f} >= {config.chi2_p_threshold}")
        if metrics["cramers_v"] <= config.cramers_v_threshold:
            logger.info(f"  - Cramér's V {metrics['cramers_v']:.4f} <= {config.cramers_v_threshold}")

    logger.info(f"\nExperiment completed in {duration}")
    logger.info(f"Results saved to: {config.output_dir}/")
    logger.info(f"Figures saved to: {config.figures_dir}/")

    # Save final results JSON with experiment metadata
    final_results = {
        "hypothesis_id": "h-e1",
        "experiment_name": "Alignment-Induced Error Type Divergence",
        "gate_type": "MUST_WORK",
        "gate_pass": metrics["gate_pass"],
        "metrics": metrics,
        "config": {
            "rl_model_id": config.rl_model_id,
            "dpo_model_id": config.dpo_model_id,
            "n_samples": config.n_samples,
            "temperature": config.temperature,
            "seed": config.seed
        },
        "duration_seconds": duration.total_seconds(),
        "timestamp": datetime.now().isoformat()
    }

    results_path = os.path.join(config.output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(final_results, f, indent=2)
    logger.info(f"Final results saved to {results_path}")

    return metrics["gate_pass"]


if __name__ == "__main__":
    success = main(CONFIG)
    sys.exit(0 if success else 1)
