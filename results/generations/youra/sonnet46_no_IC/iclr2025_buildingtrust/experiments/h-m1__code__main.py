"""Main orchestration for H-M1: RLHF Co-Optimization of Safety and Ethics."""
import json
import logging
import os
import sys

import numpy as np

from config import (
    DIMENSIONS, FIGURES_DIR, HE1_CODE_DIR, HE1_JSON, HE1_RESULTS_DIR,
    LOG_PATH, OUTPUT_DIR, RESULTS_JSON,
)
from analysis import run_analysis
from visualization import (
    plot_gate_metrics,
    plot_within_family_deltas,
    plot_safety_ethics_scatter,
    plot_delta_2d,
    plot_rho_heatmap_highlighted,
)


def serialize_results(results: dict, out_path: str) -> None:
    """Write results dict to JSON, converting numpy types."""
    def _convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, bool):
            return bool(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    serializable = {
        "hypothesis_id": "h-m1",
        "gate_pass": results["gate_pass"],
        "primary_gate": results["primary"],
        "secondary_gate": results["sign_test"],
        "deltas": [
            {k: v for k, v in d.items() if k != "all_deltas"}
            for d in results["deltas"]
        ],
        "rho_partial": results["rho_partial"].tolist(),
        "dimensions": DIMENSIONS,
    }
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2, default=_convert)


def check_gate(results: dict) -> bool:
    return results["primary"]["primary_gate_pass"] and results["sign_test"]["secondary_gate_pass"]


def run_experiment(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
    output_dir: str = OUTPUT_DIR,
) -> dict:
    """Orchestrate H-M1: load → analyze → visualize → serialize → log."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "code", "outputs"), exist_ok=True)

    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger("h-m1")
    log.info("H-M1 experiment starting")

    # Analysis
    results = run_analysis(he1_code_dir, he1_results_dir, he1_json)
    log.info(f"rho_partial(safety,ethics)={results['primary']['rho_safety_ethics']:.4f}")
    log.info(f"n_both_positive={results['sign_test']['n_both_positive']}/3")
    log.info(f"gate_pass={results['gate_pass']}")

    # Figures
    pairs = results["pairs"]
    deltas = results["deltas"]
    sign_test = results["sign_test"]
    rho_partial = results["rho_partial"]
    annotated_df = results["annotated_df"]
    primary = results["primary"]

    plot_gate_metrics(
        primary["rho_safety_ethics"],
        sign_test["n_both_positive"],
        3,
        os.path.join(FIGURES_DIR, "fig1_gate_metrics.png"),
    )
    plot_within_family_deltas(
        deltas, sign_test,
        os.path.join(FIGURES_DIR, "fig2_within_family_deltas.png"),
    )
    plot_safety_ethics_scatter(
        annotated_df, pairs,
        os.path.join(FIGURES_DIR, "fig3_safety_ethics_scatter.png"),
    )
    plot_delta_2d(
        deltas,
        os.path.join(FIGURES_DIR, "fig4_delta_2d.png"),
    )
    plot_rho_heatmap_highlighted(
        rho_partial, DIMENSIONS,
        os.path.join(FIGURES_DIR, "fig5_rho_heatmap.png"),
    )
    log.info("All 5 figures generated")

    # Serialize
    serialize_results(results, RESULTS_JSON)
    log.info(f"Results saved: {RESULTS_JSON}")

    # Gate report
    gate_str = "PASS" if results["gate_pass"] else "FAIL"
    print(f"\n=== H-M1 Gate Result: {gate_str} ===")
    print(f"  Primary gate (rho>0.5): {'PASS' if primary['primary_gate_pass'] else 'FAIL'} (rho={primary['rho_safety_ethics']:.4f})")
    print(f"  Secondary gate (>=2/3 both-positive): {'PASS' if sign_test['secondary_gate_pass'] else 'FAIL'} ({sign_test['n_both_positive']}/3, p={sign_test['binom_pvalue']:.4f})")
    for d in deltas:
        print(f"  LLaMA-2-{d['scale']}: Δ_safety={d['delta_safety']:+.4f}, Δ_ethics={d['delta_ethics']:+.4f}, both_positive={d['both_positive']}")

    log.info(f"H-M1 experiment completed. Gate: {gate_str}")
    return results


if __name__ == "__main__":
    run_experiment()
