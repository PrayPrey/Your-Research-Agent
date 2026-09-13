"""Main entrypoint for H-M2 experiment."""
import json
import os
import sys

import numpy as np

from config import FIGURES_DIR, HE1_CODE_DIR, HE1_JSON, HE1_RESULTS_DIR, RESULTS_JSON
from analysis import run_analysis
from visualization import generate_all_figures


def serialize_results(obj):
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Cannot serialize {type(obj)}")


def check_gate(primary_pass: bool, secondary_pass: bool) -> str:
    if primary_pass and secondary_pass:
        return "PASS"
    elif primary_pass or secondary_pass:
        return "PARTIAL_PASS"
    else:
        return "FAIL/EXPLORE"


def run_experiment():
    try:
        print("=" * 60)
        print("H-M2: RLHF Representation Rigidity — Adversarial Robustness")
        print("=" * 60)

        results = run_analysis(HE1_CODE_DIR, HE1_RESULTS_DIR, HE1_JSON)

        primary = results["primary"]
        sign_result = results["sign_result"]
        deltas = results["deltas"]
        rho_partial = results["rho_partial"]
        annotated_df = results["annotated_df"]
        ablations = results["ablations"]
        pythia = results["pythia"]

        overall_gate = check_gate(primary["primary_gate_pass"], sign_result["secondary_gate_pass"])
        print(f"\nOverall Gate: {overall_gate}")

        print("\nGenerating figures...")
        figure_paths = generate_all_figures(
            rho_sr=primary["rho_partial_safety_robustness"],
            delta_values=sign_result["delta_robustness"],
            deltas=deltas,
            rho_partial=rho_partial,
            annotated_df=annotated_df,
            figures_dir=FIGURES_DIR,
        )
        print(f"Figures saved: {figure_paths}")

        output = {
            "hypothesis_id": "h-m2",
            "rho_partial_safety_robustness": primary["rho_partial_safety_robustness"],
            "p_value_safety_robustness": primary["p_value_safety_robustness"],
            "primary_gate_pass": primary["primary_gate_pass"],
            "delta_robustness": sign_result["delta_robustness"],
            "n_nonpositive_delta": sign_result["n_nonpositive_delta"],
            "secondary_gate_pass": sign_result["secondary_gate_pass"],
            "overall_gate": overall_gate,
            "pythia_rho_robustness_scale": pythia["pythia_rho_robustness_scale"] if pythia else None,
            "figure_paths": figure_paths,
            "rho_direct_from_matrix": primary["rho_direct_from_matrix"],
            "rho_recomputed": primary["rho_recomputed"],
            "pingouin_rho": primary["pingouin_rho"],
            "ablations": ablations,
        }

        os.makedirs(os.path.dirname(RESULTS_JSON), exist_ok=True)
        with open(RESULTS_JSON, "w") as f:
            json.dump(output, f, indent=2, default=serialize_results)
        print(f"\nResults saved: {RESULTS_JSON}")

        print("\n" + "=" * 60)
        print(f"H-M2 COMPLETE — Gate: {overall_gate}")
        print(f"  ρ_partial(safety,robustness) = {primary['rho_partial_safety_robustness']:.4f}")
        print(f"  p-value = {primary['p_value_safety_robustness']:.4e}")
        print(f"  n_nonpositive Δ_robustness = {sign_result['n_nonpositive_delta']}/3")
        print("=" * 60)

        return output

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

        error_output = {
            "hypothesis_id": "h-m2",
            "error": str(e),
            "overall_gate": "ERROR",
        }
        try:
            os.makedirs(os.path.dirname(RESULTS_JSON), exist_ok=True)
            with open(RESULTS_JSON, "w") as f:
                json.dump(error_output, f, indent=2)
        except Exception:
            pass
        return error_output


if __name__ == "__main__":
    run_experiment()
