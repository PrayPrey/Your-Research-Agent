#!/usr/bin/env python3
"""
H-E1: Query-Aware KV Eviction — Existence (PoC) Validation
Entry point for Phase 4 experiment execution.
"""
import sys
import os
import logging
import torch

# Ensure h-e1/code is importable regardless of working directory
_this_dir = os.path.dirname(os.path.abspath(__file__))
_code_dir = os.path.join(_this_dir, "code")
if _code_dir not in sys.path:
    sys.path.insert(0, _code_dir)

from experiment.config import ExperimentConfig, validate_config
from experiment.runner import run_all
from results.aggregator import build_results_json
from visualization.figures import save_all_figures


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger("h-e1")

    torch.manual_seed(42)

    cfg = ExperimentConfig()
    # Output paths relative to this script's directory
    cfg.output_dir = _this_dir
    cfg.results_file = "results.json"
    cfg.figures_dir = os.path.join(_this_dir, "figures")

    logger.info("=== H-E1: Starting experiment ===")
    logger.info(f"Config: {cfg}")

    validate_config(cfg)

    raw_results, spot_check_scores = run_all(cfg)

    results_path = os.path.join(cfg.output_dir, cfg.results_file)
    results = build_results_json(raw_results, cfg, output_path=results_path)

    save_all_figures(results, spot_check_scores, cfg.figures_dir)

    gc = results["gate_check"]
    logger.info("=== GATE CHECK ===")
    logger.info(f"M1 macro-F1: {results['per_method']['M1']['macro_f1']:.2f}")
    logger.info(f"M2 macro-F1: {results['per_method']['M2']['macro_f1']:.2f}")
    logger.info(f"M1 - M2 delta: {gc['m1_minus_m2']:.2f} (threshold ≥ {cfg.gate_threshold})")
    logger.info(f"Bootstrap 95% CI: [{gc['bootstrap_ci_lower']:.2f}, {gc['bootstrap_ci_upper']:.2f}]")
    logger.info(f"Gate PASS: {gc['gate_pass']}")

    if gc["gate_pass"]:
        logger.info("✅ H-E1 GATE PASSED — query-aware eviction (M1) beats cumulative-attn (M2) by ≥2.0 F1")
        sys.exit(0)
    else:
        logger.warning("❌ H-E1 GATE FAILED — delta below threshold or CI includes 0")
        sys.exit(1)


if __name__ == "__main__":
    main()
