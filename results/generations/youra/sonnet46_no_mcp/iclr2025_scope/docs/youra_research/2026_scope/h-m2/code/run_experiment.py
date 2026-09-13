"""H-M2 Budget-Ratio Dose-Response Experiment Orchestrator."""
import argparse
import logging
import os
import sys

import numpy as np
import torch


def setup_logging(log_file: str = "experiment.log") -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="H-M2 Budget-Ratio Sweep Experiment")
    parser.add_argument("--device", default="cuda", help="Device (cuda/cpu)")
    parser.add_argument("--results-dir", default="outputs/h-m2", dest="results_dir")
    parser.add_argument("--figures-dir", default="figures", dest="figures_dir")
    parser.add_argument("--smoke-test-only", action="store_true", dest="smoke_test_only")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--log-file", default="experiment.log", dest="log_file")
    args = parser.parse_args()

    setup_logging(args.log_file)
    logger = logging.getLogger("run_experiment")

    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available() and args.device == "cuda":
        torch.cuda.manual_seed_all(args.seed)

    logger.info("=" * 60)
    logger.info("H-M2: Budget-Ratio Dose-Response Analysis")
    logger.info("=" * 60)
    logger.info(f"Device: {args.device}, Seed: {args.seed}")

    # Step 1: Load config
    from config import get_default_config, validate_config
    cfg = get_default_config()
    cfg.results_dir = args.results_dir
    cfg.figures_dir = args.figures_dir

    try:
        validate_config(cfg)
        logger.info(f"Config validated: {len(cfg.adapters)} adapters, {len(cfg.budget_ratios)} budget ratios")
    except (AssertionError, ValueError) as e:
        logger.warning(f"Config validation warning (continuing): {e}")

    # Step 2: Smoke test
    logger.info("Running smoke test...")
    from smoke_test import run_smoke_test
    smoke_ok = run_smoke_test(device=args.device)
    if not smoke_ok:
        logger.error("SMOKE TEST FAILED — aborting experiment")
        sys.exit(1)
    logger.info("Smoke test PASSED")

    if args.smoke_test_only:
        logger.info("--smoke-test-only flag set. Exiting.")
        print("EXPERIMENT COMPLETE")
        return

    # Step 3: Run all 12 evaluation runs
    from evaluate import BudgetSweepEvaluator, save_run_results
    evaluator = BudgetSweepEvaluator(cfg)
    logger.info(f"Starting {len(cfg.adapters)} adapters × {len(cfg.budget_ratios)} budget ratios sweep...")
    results = evaluator.run_all(device=args.device)
    logger.info(f"Completed {len(results)} runs")

    # Step 4: Save CSV
    csv_path = save_run_results(results, args.results_dir)
    logger.info(f"Results saved: {csv_path}")

    # Step 5: Spearman analysis
    from analyze import SpearmanAnalyzer
    analyzer = SpearmanAnalyzer()
    analysis = analyzer.run_full_analysis(results)

    # Step 6: Save JSON summary
    json_path = os.path.join(args.results_dir, "spearman_summary.json")
    analyzer.save_summary(analysis, json_path)
    logger.info(f"Spearman summary saved: {json_path}")

    # Step 7: Save figures
    from visualize import save_all_figures
    save_all_figures(analysis, results, args.figures_dir)

    # Step 8: Log gate result
    gate_passed = analysis["gate_passed"]
    logger.info("=" * 60)
    logger.info(f"GATE RESULT (SHOULD_WORK): {'PASS' if gate_passed else 'FAIL'}")
    for model_name, sr in analysis["spearman_results"].items():
        label = model_name.split("/")[-1] if "/" in model_name else model_name
        logger.info(f"  {label}: rho={sr.rho:.4f}, gate={'PASS' if sr.gate_passed else 'FAIL'}")
    if not gate_passed:
        logger.info("NOTE: SHOULD_WORK gate failed — documenting as scope limitation, H-M3 continues")
    logger.info("=" * 60)

    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
