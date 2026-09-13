#!/usr/bin/env python
"""H-E1 Experiment Runner: Orchestrate full contamination-correlation analysis."""
import sys
import json
import os
import logging
from datetime import datetime

from config import CONFIG, PATHS
from evaluate import run_all_evaluations
from contamination import contamination_by_task, use_literature_contamination
from analysis import run_full_analysis, save_analysis
from visualize import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def main():
    """Run complete H-E1 experiment pipeline."""
    start_time = datetime.now()
    log.info("=" * 60)
    log.info("H-E1 Experiment: Contamination-Correlation Analysis")
    log.info("=" * 60)

    log.info("\n[1/4] Running evaluations...")
    results = run_all_evaluations()
    log.info(f"Evaluated {len(results)} checkpoint-task pairs")

    log.info("\n[2/4] Computing contamination...")
    contam = contamination_by_task()
    for task, pct in contam.items():
        log.info(f"  {task}: {pct:.2f}%")

    log.info("\n[3/4] Running analysis...")
    analysis = run_full_analysis(results, contam)
    save_analysis(analysis)

    log.info("\n[4/4] Generating figures...")
    figures = generate_all_figures(results, contam, analysis)
    for fig in figures:
        log.info(f"  Generated: {fig}")

    log.info("\n" + "=" * 60)
    log.info("GATE CHECK")
    log.info("=" * 60)
    log.info(f"Spearman r = {analysis.r:.4f} (threshold: > {CONFIG.gate_r_threshold})")
    log.info(f"p-value    = {analysis.p_value:.4f} (threshold: < {CONFIG.gate_p_threshold})")

    gate_pass = analysis.r > CONFIG.gate_r_threshold and analysis.p_value < CONFIG.gate_p_threshold

    log.info("-" * 60)
    if gate_pass:
        log.info("GATE RESULT: PASS")
        log.info("Correlation exists - proceed to Phase 5 baseline comparison")
    else:
        log.info("GATE RESULT: FAIL")
        log.info("No significant correlation - ABANDON transfer function approach")
    log.info("-" * 60)

    duration = datetime.now() - start_time
    log.info(f"\nTotal runtime: {duration}")

    experiment_results = {
        "hypothesis_id": "H-E1",
        "gate_type": "MUST_WORK",
        "metrics": {
            "spearman_r": analysis.r,
            "p_value": analysis.p_value,
            "n_samples": analysis.n,
        },
        "thresholds": {
            "r_threshold": CONFIG.gate_r_threshold,
            "p_threshold": CONFIG.gate_p_threshold,
        },
        "gate_result": "PASS" if gate_pass else "FAIL",
        "per_benchmark": analysis.per_benchmark,
        "contamination_by_task": contam,
        "runtime_seconds": duration.total_seconds(),
        "timestamp": datetime.now().isoformat(),
        "poc_mode": False,
        "data_source": "literature" if use_literature_contamination() else "pile_ngrams",
        "evaluation_source": "lm-eval-harness (real model evaluation)",
        "contamination_source": "Yang et al. 2023, Deng et al. 2024" if use_literature_contamination() else "Pile 13-gram index",
        "models": f"Pythia {CONFIG.model_sizes}",
        "benchmarks": CONFIG.tasks,
    }

    results_path = os.path.join(os.path.dirname(PATHS.figures_dir), "experiment_results.json")
    with open(results_path, 'w') as f:
        json.dump(experiment_results, f, indent=2)
    log.info(f"Results saved to: {results_path}")

    return 0 if gate_pass else 1

if __name__ == "__main__":
    sys.exit(main())
