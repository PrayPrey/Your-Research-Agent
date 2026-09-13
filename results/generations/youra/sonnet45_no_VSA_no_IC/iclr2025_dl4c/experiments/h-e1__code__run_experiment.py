#!/usr/bin/env python3
"""Main orchestrator for h-e1 binary feedback sufficiency experiment."""

import sys
import os
import yaml
import logging
import random
import numpy as np
import torch
import argparse
from datetime import datetime

from dataset import HumanEvalLoader
from model import ModelManager
from sandbox import ExecutionSandbox
from train import SFTTrainer, GRPOTrainer
from eval import Evaluator
from validate import ValidationReporter

def setup_logging(log_file: str, console: bool = True):
    """Configure logging."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handlers = [logging.FileHandler(log_file)]
    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        handlers=handlers
    )

def set_seed(seed: int):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    parser = argparse.ArgumentParser(description="Run h-e1 binary feedback sufficiency experiment")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--skip-sft", action="store_true", help="Skip SFT training (use existing checkpoint)")
    parser.add_argument("--skip-binary", action="store_true", help="Skip binary RLVR training")
    parser.add_argument("--skip-error-type", action="store_true", help="Skip error-type RLVR training")
    parser.add_argument("--eval-only", action="store_true", help="Run evaluation only")
    args = parser.parse_args()

    config = load_config(args.config)

    setup_logging(config["logging"]["log_file"], config["logging"]["console_output"])
    logger = logging.getLogger(__name__)

    logger.info("="*80)
    logger.info(f"Starting h-e1 experiment: {config['experiment']['description']}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

    set_seed(config["reproducibility"]["seed"])
    logger.info(f"Random seed set to {config['reproducibility']['seed']}")

    logger.info("[Stage 1/7] Loading HumanEval dataset...")
    loader = HumanEvalLoader(config["dataset"]["cache_dir"])
    loader.load_dataset()
    sft_pairs = loader.get_sft_pairs()
    test_suites = loader.prepare_test_suites()
    logger.info(f"Dataset loaded: {len(sft_pairs)} training pairs, {len(test_suites)} test problems")

    sandbox = ExecutionSandbox(config)
    logger.info("Execution sandbox initialized")

    model_manager = ModelManager(config)

    results = {
        "sft_pass1": None,
        "binary_pass1": None,
        "error_type_pass1": None
    }

    if not args.eval_only:
        logger.info("[Stage 2/7] Setting up SFT baseline model...")
        if not args.skip_sft:
            sft_model, tokenizer = model_manager.setup_sft_model()

            logger.info("[Stage 3/7] Training SFT baseline...")
            sft_trainer = SFTTrainer(config, sft_model, tokenizer)
            sft_checkpoint = sft_trainer.train(sft_pairs)
            logger.info(f"SFT checkpoint: {sft_checkpoint}")
        else:
            logger.info("Skipping SFT training (using existing checkpoint)")
            sft_checkpoint = config["evaluation"]["checkpoint_paths"]["sft"]
            _, tokenizer = model_manager.setup_sft_model()

        logger.info("[Stage 4/7] Training GRPO Binary...")
        if not args.skip_binary:
            policy_model, ref_model, tokenizer = model_manager.setup_rlvr_models(sft_checkpoint)
            grpo_trainer = GRPOTrainer(config, policy_model, ref_model, tokenizer, sandbox)
            binary_checkpoint = grpo_trainer.train(test_suites, "binary", config["training"]["grpo_binary"])
            logger.info(f"Binary RLVR checkpoint: {binary_checkpoint}")
        else:
            logger.info("Skipping Binary RLVR training")

        logger.info("[Stage 5/7] Training GRPO Error-Type...")
        if not args.skip_error_type:
            policy_model, ref_model, tokenizer = model_manager.setup_rlvr_models(sft_checkpoint)
            grpo_trainer = GRPOTrainer(config, policy_model, ref_model, tokenizer, sandbox)
            error_type_checkpoint = grpo_trainer.train(test_suites, "error_type", config["training"]["grpo_error_type"])
            logger.info(f"Error-Type RLVR checkpoint: {error_type_checkpoint}")
        else:
            logger.info("Skipping Error-Type RLVR training")

    logger.info("[Stage 6/7] Evaluating all checkpoints on HumanEval...")

    for name, checkpoint_path in [
        ("SFT", config["evaluation"]["checkpoint_paths"]["sft"]),
        ("Binary", config["evaluation"]["checkpoint_paths"]["binary"]),
        ("Error-Type", config["evaluation"]["checkpoint_paths"]["error_type"])
    ]:
        if not os.path.exists(checkpoint_path):
            logger.warning(f"{name} checkpoint not found: {checkpoint_path}")
            continue

        logger.info(f"Loading {name} checkpoint...")
        model, tokenizer = model_manager.load_pretrained()
        model = model_manager.configure_lora(model)

        checkpoint = torch.load(checkpoint_path, map_location=model_manager.device)
        model.load_state_dict(checkpoint["model_state_dict"])

        evaluator = Evaluator(config, model, tokenizer, sandbox)
        eval_results = evaluator.evaluate_checkpoint(test_suites)

        results_path = os.path.join(config["evaluation"]["output_dir"], f"{name.lower()}_results.json")
        evaluator.save_results(eval_results, results_path)

        results[f"{name.lower()}_pass1"] = eval_results["pass@1"]
        logger.info(f"{name} pass@1: {eval_results['pass@1']:.4f}")

    logger.info("[Stage 7/7] Validating gate thresholds...")
    reporter = ValidationReporter(config)

    gate_result = reporter.check_gate(
        results["sft_pass1"],
        results["binary_pass1"],
        results["error_type_pass1"]
    )

    gate_figure_path = "../figures/gate_metrics.png"
    reporter.generate_gate_metrics_figure(gate_result, gate_figure_path)

    pass_rates_figure_path = "../figures/pass_rates.png"
    reporter.generate_pass_rates_figure(gate_result, pass_rates_figure_path)

    logger.info("="*80)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate Status: {'PASS ✓' if gate_result['gate_passed'] else 'FAIL ✗'}")
    logger.info(f"  SFT Baseline: {results['sft_pass1']*100:.2f}%")
    logger.info(f"  Binary RLVR: {results['binary_pass1']*100:.2f}%")
    logger.info(f"  Error-Type RLVR: {results['error_type_pass1']*100:.2f}%")
    logger.info(f"  Absolute Improvement: {gate_result['absolute_improvement']:.2f} pp (threshold: {config['gate']['thresholds']['absolute_improvement']} pp)")
    if gate_result['retention_ratio'] is not None:
        logger.info(f"  Retention Ratio: {gate_result['retention_ratio']:.2f} (threshold: {config['gate']['thresholds']['retention_ratio']})")
    else:
        logger.info(f"  Retention Ratio: N/A (Error-Type gain ≤ 0)")
    logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

    validation_report_path = "../04_validation.md"
    generate_validation_report(config, results, gate_result, validation_report_path)

    return 0 if gate_result["gate_passed"] else 1

def generate_validation_report(config, results, gate_result, output_path):
    """Generate 04_validation.md report."""
    logger = logging.getLogger(__name__)
    logger.info(f"Generating validation report: {output_path}")

    report = f"""# Validation Report: h-e1

**Hypothesis:** {config['experiment']['description']}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** {'PASS' if gate_result['gate_passed'] else 'FAIL'}

---

## Results Summary

| Model | Pass@1 | Absolute Improvement | Retention Ratio |
|-------|--------|---------------------|-----------------|
| SFT Baseline | {results['sft_pass1']*100:.2f}% | - | - |
| Binary RLVR | {results['binary_pass1']*100:.2f}% | {gate_result['absolute_improvement']:.2f} pp | {gate_result['retention_ratio']:.2f if gate_result['retention_ratio'] else 'N/A'} |
| Error-Type RLVR | {results['error_type_pass1']*100:.2f}% | {(results['error_type_pass1']-results['sft_pass1'])*100:.2f} pp | 1.00 |

## Gate Validation

**EXISTENCE Gate (MUST_WORK):**

1. **Threshold 1: Absolute Improvement ≥ {config['gate']['thresholds']['absolute_improvement']} pp**
   - Actual: {gate_result['absolute_improvement']:.2f} pp
   - Status: {'✓ PASS' if gate_result['threshold_1_met'] else '✗ FAIL'}

2. **Threshold 2: Retention Ratio ≥ {config['gate']['thresholds']['retention_ratio']}**
   - Actual: {gate_result['retention_ratio']:.2f if gate_result['retention_ratio'] else 'N/A'}
   - Status: {'✓ PASS' if gate_result['threshold_2_met'] else '✗ FAIL'}

**Overall Gate Status:** {'✓ PASS' if gate_result['gate_passed'] else '✗ FAIL'}

---

## Key Findings

1. Binary feedback {'achieves' if gate_result['gate_passed'] else 'does not achieve'} dual-threshold sufficiency.
2. Absolute improvement: {gate_result['absolute_improvement']:.2f} pp over SFT baseline.
3. Retention ratio: {gate_result['retention_ratio']:.2f if gate_result['retention_ratio'] else 'N/A'} (binary gain / error-type gain).

---

## Figures

- Gate metrics: `figures/gate_metrics.png`
- Pass rates comparison: `figures/pass_rates.png`

---

## Configuration

- Model: {config['model']['name']}
- Dataset: {config['dataset']['name']} ({config['dataset']['num_problems']} problems)
- SFT epochs: {config['training']['sft']['epochs']}
- GRPO steps: {config['training']['grpo_binary']['steps']}
- Seed: {config['reproducibility']['seed']}

---

**Next Steps:** {'Proceed to mechanistic hypotheses (h-m1, h-m2, h-m3)' if gate_result['gate_passed'] else 'Re-evaluate main hypothesis or modify approach'}
"""

    with open(output_path, 'w') as f:
        f.write(report)

    logger.info(f"Validation report saved to {output_path}")

if __name__ == "__main__":
    sys.exit(main())
