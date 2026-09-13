#!/usr/bin/env python3
"""H-M2 entrypoint: confidence-accuracy decoupling analysis."""
import json
import logging
import sys
from pathlib import Path

# All modules are in the same directory
sys.path.insert(0, str(Path(__file__).parent))

from config import H_M2_RESULTS_DIR, H_M2_FIGURES_DIR
from jsonl_loader import preflight_check
from cell_analyzer import run_all_cells
from gate_evaluator import evaluate_gate
from secondary_analyzer import (
    anli_gradient,
    confidence_delta_analysis,
    ablation_threshold_sensitivity,
    ablation_task_subset,
    ablation_model_size,
)
from results_writer import (
    write_main_results,
    write_gate_report,
    write_secondary_results,
    write_summary,
)
from visualizer import (
    plot_gate_metrics,
    plot_accuracy_scatter,
    plot_confidence_distributions,
    plot_delta_acc_heatmap,
    plot_anli_gradient,
    plot_base_vs_chat,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    print("=" * 60)
    print("H-M2: Confidence-Accuracy Decoupling Analysis")
    print("=" * 60)

    # 1. Pre-flight check
    preflight_check()

    # 2. Run all cells
    print("\nComputing per-cell statistics...")
    cell_results = run_all_cells()

    # 3. Evaluate gate
    print("\nEvaluating H-M2 gate...")
    gate_result = evaluate_gate(cell_results)

    # 4. Secondary analyses
    print("\nRunning secondary analyses...")
    anli_stats   = anli_gradient(cell_results)
    conf_delta   = confidence_delta_analysis(cell_results)
    ablation_thr = ablation_threshold_sensitivity(cell_results)
    ablation_sub = ablation_task_subset(cell_results)
    ablation_mdl = ablation_model_size(cell_results)

    secondary = {
        "anli_gradient":               anli_stats,
        "confidence_delta":            conf_delta,
        "ablation_threshold_sensitivity": ablation_thr,
        "ablation_task_subset":        ablation_sub,
        "ablation_model_size":         ablation_mdl,
        "mean_delta_acc":              gate_result.mean_delta_acc,
        "mean_conf_wrong_adv":         gate_result.mean_conf_wrong_adv,
        "mean_conf_correct_adv":       gate_result.mean_conf_correct_adv,
    }

    # 5. Write results
    print("\nWriting results...")
    H_M2_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_main_results(cell_results, H_M2_RESULTS_DIR)
    write_gate_report(gate_result, H_M2_RESULTS_DIR)
    write_secondary_results(secondary, H_M2_RESULTS_DIR)

    summary_path = Path(__file__).parent.parent / "results" / "h_m2_summary.md"
    write_summary(gate_result, secondary, cell_results, summary_path)

    # 6. Generate figures
    print("\nGenerating figures...")
    H_M2_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_gate_metrics(cell_results, gate_result, H_M2_FIGURES_DIR)
    plot_accuracy_scatter(cell_results, H_M2_FIGURES_DIR)
    plot_confidence_distributions(cell_results, H_M2_FIGURES_DIR)
    plot_delta_acc_heatmap(cell_results, H_M2_FIGURES_DIR)
    plot_anli_gradient(anli_stats, H_M2_FIGURES_DIR)
    plot_base_vs_chat(cell_results, H_M2_FIGURES_DIR)

    # 7. Save structured experiment_results.json
    expr_path = Path(__file__).parent.parent / "experiment_results.json"
    expr_results = {
        "hypothesis_id": "H-M2",
        "gate_result": gate_result.overall_result,
        "gate_pass_rate": gate_result.gate_pass_rate,
        "gate_pass_count": gate_result.gate_pass_count,
        "total_cells": gate_result.total_cells,
        "mean_delta_acc": gate_result.mean_delta_acc,
        "mean_conf_wrong_adv": gate_result.mean_conf_wrong_adv,
        "passed_cells": [f"{m}_{t}" for m, t in gate_result.passed_cells],
        "failed_cells": gate_result.failed_cells,
        "secondary": secondary,
    }
    with open(expr_path, "w") as f:
        def _jsonable(obj):
            if isinstance(obj, dict):
                return {str(k): _jsonable(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [_jsonable(i) for i in obj]
            if isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            return str(obj)
        json.dump(_jsonable(expr_results), f, indent=2)
    print(f"Wrote: {expr_path}")

    # Final gate verdict
    print("\n" + "=" * 60)
    print(f"H-M2 GATE RESULT: {gate_result.overall_result}")
    print(f"gate_pass_rate: {gate_result.gate_pass_rate:.4f}")
    print(f"mean ΔAcc: {gate_result.mean_delta_acc:.4f}")
    print(f"mean conf_wrong_adv: {gate_result.mean_conf_wrong_adv:.4f}")
    print("=" * 60)
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
