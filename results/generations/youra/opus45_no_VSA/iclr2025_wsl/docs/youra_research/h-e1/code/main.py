#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from evaluate import aggregate_results, check_success_criteria, save_results
from extract import run_extraction
from visualize import plot_cv_pr_distribution, plot_success_rate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def main():
    log.info(f"Starting extraction: {CONFIG['n_models']} models, {CONFIG['n_seeds']} seeds")

    results = run_extraction(CONFIG)
    log.info(f"Extraction complete: {len(results)} models processed")

    summary = aggregate_results(results)
    log.info(f"Summary: completion={summary['completion_rate']:.2%}, mean_cv_pr={summary['mean_cv_pr']:.4f}")

    base = Path(__file__).parent.parent
    out_dir = base / CONFIG["output_dir"]
    fig_dir = base / CONFIG["figures_dir"]

    save_results(results, summary, str(out_dir))
    log.info(f"Results saved to {out_dir}")

    plot_success_rate(summary, str(fig_dir / "success_rate.png"))
    plot_cv_pr_distribution(results, str(fig_dir / "cv_pr_distribution.png"))
    log.info(f"Figures saved to {fig_dir}")

    success = check_success_criteria(summary)
    log.info(f"Success criteria: {'PASSED' if success else 'FAILED'}")

    print(f"\n{'='*50}")
    print("EXPERIMENT RESULTS")
    print(f"{'='*50}")
    print(f"Models processed: {summary['n_models_processed']}")
    print(f"Models valid: {summary['n_models_valid']}")
    print(f"Completion rate: {summary['completion_rate']:.2%}")
    print(f"Mean CV_PR: {summary['mean_cv_pr']:.4f}")
    print(f"Std CV_PR: {summary['std_cv_pr']:.4f}")
    print(f"Range: [{summary['min_cv_pr']:.4f}, {summary['max_cv_pr']:.4f}]")
    print(f"SUCCESS: {success}")
    print(f"{'='*50}\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
