"""
run_experiment.py — Main Orchestration for H-M1 NLI Distribution Analysis
"""
import dataclasses
import json
import logging
import sys
from pathlib import Path
from typing import List

from config import ExperimentConfig, load_config
from data import TaskScores, load_all_tasks
from analyze import TaskAnalysisResult, GateResult, analyze_nli_distribution, evaluate_gate, verify_mechanism_activated
from visualize import generate_all_figures


def setup_logging() -> None:
    """Configure root logger: INFO level, timestamped format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def save_results(
    results: List[TaskAnalysisResult],
    gate: GateResult,
    config: ExperimentConfig,
) -> None:
    """Save h_m1_results.json (full) and h_m1_summary.json (gate fields)."""
    results_dir = Path(config.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Full results
    full_results = {
        "tasks": [dataclasses.asdict(r) for r in results],
        "gate": dataclasses.asdict(gate),
    }
    results_path = results_dir / config.results_filename
    with open(results_path, "w") as f:
        json.dump(full_results, f, indent=2)
    logging.getLogger(__name__).info(f"Saved full results to: {results_path}")

    # Summary
    summary = {
        "gate_pass": gate.gate_pass,
        "kl_all_pass": gate.kl_all_pass,
        "wilcoxon_pass_count": gate.wilcoxon_pass_count,
        "mechanism_activated": gate.mechanism_activated,
        "per_task": {
            r.task_name: {
                "kl_divergence_from_uniform": r.kl_divergence_from_uniform,
                "kl_passes": r.kl_passes,
                "wilcoxon_pvalue": r.wilcoxon_pvalue,
                "wilcoxon_passes": r.wilcoxon_passes,
                "p_near_uniform": r.p_near_uniform,
                "cohens_d": r.cohens_d,
            }
            for r in results
        }
    }
    summary_path = results_dir / config.summary_filename
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logging.getLogger(__name__).info(f"Saved summary to: {summary_path}")


def main() -> None:
    """Full pipeline. Exits with sys.exit(1) if h-e1 results missing.

    Execution order:
    1. setup_logging()
    2. config = load_config("config.yaml")
    3. Verify h_e1_results_path exists → sys.exit(1) if not
    4. task_data_list = load_all_tasks(config)
    5. results = [analyze_nli_distribution(...) for td in task_data_list]
    6. gate = evaluate_gate(results, config)
    7. _, indicators = verify_mechanism_activated(results, config)
    8. save_results(results, gate, config)
    9. generate_all_figures(task_data_list, results, config, config.figures_dir)
    10. log "GATE: PASS/FAIL (KL_all={}, Wilcoxon_count={}/3)"
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    # Step 2: Load config
    config = load_config("config.yaml")
    logger.info(f"Config loaded: h_e1_results_path={config.h_e1_results_path}")

    # Step 3: Verify h-e1 results exist
    h_e1_path = Path(config.h_e1_results_path)
    if not h_e1_path.exists():
        logger.error(
            f"H-E1 results not found at: {h_e1_path}\n"
            "Please run H-E1 experiment first."
        )
        sys.exit(1)

    # Step 4: Load all tasks
    logger.info("Loading task data...")
    task_data_list = load_all_tasks(config)
    logger.info(f"Loaded {len(task_data_list)} tasks")

    # Step 5: Analyze NLI distribution per task
    logger.info("Analyzing NLI distributions...")
    results: List[TaskAnalysisResult] = []
    for td in task_data_list:
        result = analyze_nli_distribution(
            td.scores_nxt3, td.labels_n, td.task_name, config
        )
        results.append(result)

    # Step 6: Evaluate gate
    logger.info("Evaluating MUST_WORK gate...")
    gate = evaluate_gate(results, config)

    # Step 7: Verify mechanism
    all_pass, indicators = verify_mechanism_activated(results, config)
    logger.info(f"Mechanism activated: {all_pass}")
    for task_name, task_indicators in indicators.items():
        logger.info(f"  [{task_name}] {task_indicators}")

    # Step 8: Save results
    logger.info("Saving results...")
    save_results(results, gate, config)

    # Step 9: Generate figures
    logger.info("Generating figures...")
    generate_all_figures(task_data_list, results, config, config.figures_dir)

    # Step 10: Log gate result
    gate_str = "PASS" if gate.gate_pass else "FAIL"
    logger.info(
        f"GATE: {gate_str} (KL_all={gate.kl_all_pass}, Wilcoxon_count={gate.wilcoxon_pass_count}/3)"
    )

    if gate.gate_pass:
        logger.info("H-M1 MUST_WORK gate: PASSED — NLI distribution signal confirmed")
    else:
        logger.warning("H-M1 MUST_WORK gate: FAILED — Check KL divergence and Wilcoxon results")


if __name__ == "__main__":
    main()
