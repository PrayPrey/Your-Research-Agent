#!/usr/bin/env python3
"""
Main experiment runner for H-M2: Min-k% memorization signal.
Compares Pythia Pile vs dedup-Pile checkpoints on 4 benchmarks.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent))


def setup_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    parser = argparse.ArgumentParser(description="H-M2: Min-k% memorization signal")
    parser.add_argument("--dry-run", action="store_true",
                        help="Quick smoke test with 50 items per benchmark, 1B models only")
    parser.add_argument("--dry-run-items", type=int, default=50)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--skip-stages", nargs="*", default=[])
    parser.add_argument("--stages", nargs="*", default=None)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--results-path",
                        default="docs/youra_research/h-m2/experiment_results.json")
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger("run_experiment")

    logger.info("=" * 60)
    logger.info("H-M2: Min-k% Memorization Signal — Pile vs Dedup-Pile")
    logger.info("=" * 60)
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'FULL'}")
    logger.info(f"Device: {args.device}")

    from pipeline import run_pipeline, save_experiment_results

    results = run_pipeline(
        stages=args.stages,
        skip_stages=args.skip_stages,
        resume=not args.no_resume,
        device=args.device,
        dry_run=args.dry_run,
        dry_run_items=args.dry_run_items,
    )

    gate = results.get("gate", {})
    mechanism = results.get("mechanism", {})
    stats = results.get("stats", [])

    logger.info("")
    logger.info("=" * 60)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Gate result:         {gate.get('result', 'N/A')}")
    logger.info(f"Gate satisfied:      {gate.get('satisfied', False)}")
    logger.info(f"n_significant:       {gate.get('n_significant', 0)}/8 benchmark×model_size combos")
    logger.info(f"n_pile_higher:       {gate.get('n_pile_higher', 0)}/8")
    logger.info(f"Mechanism activated: {mechanism.get('activated', False)}")
    logger.info("")

    for s in stats:
        sig = "✓ SIGNIFICANT" if s.significant else "  not sig"
        logger.info(
            f"  {s.benchmark:16s} {s.model_size:4s} | "
            f"pile={s.mean_pile:.4f} dedup={s.mean_deduped:.4f} "
            f"diff={s.differential:+.4f} p_corr={s.p_corrected:.4f} {sig}"
        )

    # Save results
    results_path = Path(args.results_path)
    save_experiment_results(results, results_path)

    logger.info(f"\nResults saved to: {results_path}")
    logger.info("EXPERIMENT COMPLETE")

    # Exit with appropriate code
    sys.exit(0 if gate.get("satisfied", False) else 1)


if __name__ == "__main__":
    main()
