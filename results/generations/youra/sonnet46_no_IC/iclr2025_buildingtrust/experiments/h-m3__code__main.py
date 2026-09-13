"""Main entry point for H-M3 experiment."""
import json
import os
import numpy as np

from config import HE1_JSON, FIGURES_DIR, RESULTS_JSON
from analysis import run_analysis
from visualization import generate_all_figures


def serialize_results(results: dict) -> dict:
    out = {}
    for k, v in results.items():
        if isinstance(v, np.ndarray):
            out[k] = v.tolist()
        elif isinstance(v, np.floating):
            out[k] = float(v)
        elif isinstance(v, np.integer):
            out[k] = int(v)
        elif isinstance(v, np.bool_):
            out[k] = bool(v)
        elif isinstance(v, dict):
            out[k] = {kk: (int(vv) if isinstance(vv, (np.integer,)) else
                           float(vv) if isinstance(vv, (np.floating,)) else
                           bool(vv) if isinstance(vv, np.bool_) else vv)
                      for kk, vv in v.items()}
        else:
            out[k] = v
    return out


def check_gate(results: dict) -> str:
    try:
        primary = bool(results.get("primary_gate_pass", False))
        secondary = bool(results.get("secondary_gate_pass", False))
        if primary and secondary:
            return "PASS"
        elif primary or secondary:
            return "PARTIAL_PASS"
        else:
            return "FAIL"
    except Exception:
        return "FAIL"


def run_experiment() -> None:
    os.makedirs(FIGURES_DIR, exist_ok=True)

    results = run_analysis(HE1_JSON)
    figure_paths = generate_all_figures(results, FIGURES_DIR)
    results['figure_paths'] = figure_paths

    serializable = serialize_results(results)
    serializable['overall_gate'] = check_gate(results)
    serializable['hypothesis_id'] = 'h-m3'

    with open(RESULTS_JSON, 'w') as f:
        json.dump(serializable, f, indent=2)

    print(f"Phase 4 complete. Gate: {serializable['overall_gate']}")
    print(f"Results saved to: {RESULTS_JSON}")


if __name__ == "__main__":
    run_experiment()
