"""H-M5 Analysis: Main entrypoint."""
import json
import logging
from pathlib import Path

from data_loader import load_panel_data, prepare_analysis_df
from models import fit_baseline, fit_panel_fe, run_robustness_suite
from granger import run_bidirectional_granger
import visualize

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


def gate_check(fe_result: dict, granger_result: dict) -> bool:
    """Primary: beta < 0 AND p < 0.05."""
    primary_pass = fe_result["beta"] < 0 and fe_result["p_value"] < 0.05
    sec_fwd = granger_result["n_significant_forward"] >= 1
    sec_rev = granger_result["n_significant_reverse"] == 0
    log.info(f"Primary gate: beta={fe_result['beta']:.4f}, p={fe_result['p_value']:.4f} -> {'PASS' if primary_pass else 'FAIL'}")
    log.info(f"Granger secondary: forward_sig={sec_fwd}, no_reverse={sec_rev}")
    return primary_pass


def main() -> dict:
    """Run complete H-M5 analysis."""
    log.info("Loading panel data...")
    raw = load_panel_data()
    log.info(f"Loaded {len(raw)} venue-years")

    df1 = prepare_analysis_df(raw, lag=1)
    df2 = prepare_analysis_df(raw, lag=2)
    log.info(f"Prepared analysis: lag1={len(df1)}, lag2={len(df2)} observations")

    log.info("Fitting baseline model...")
    baseline = fit_baseline(df1)
    log.info(f"Baseline: beta={baseline['beta']:.4f}, p={baseline['p_value']:.4f}")

    log.info("Fitting Panel FE model...")
    fe = fit_panel_fe(df1)
    log.info(f"Panel FE: beta={fe['beta']:.4f}, p={fe['p_value']:.4f}, R²={fe['r_squared']:.4f}")

    log.info("Running robustness suite...")
    robustness = run_robustness_suite(df1, df2)

    log.info("Running Granger causality tests...")
    granger = run_bidirectional_granger(df1)
    log.info(f"Granger: forward_sig={granger['n_significant_forward']}, reverse_sig={granger['n_significant_reverse']}")

    passed = gate_check(fe, granger)
    log.info(f"GATE RESULT: {'PASS' if passed else 'FAIL'}")

    log.info("Generating figures...")
    out_dir = Path(__file__).parent.parent / "figures"
    visualize.generate_all(fe, granger, df1, str(out_dir))

    results = {
        "baseline": baseline,
        "panel_fe": {k: v for k, v in fe.items() if k != "results_obj"},
        "robustness": {
            "lag2": {k: v for k, v in robustness["lag2"].items() if k != "results_obj"},
            "entity_only": {k: v for k, v in robustness["entity_only"].items() if k != "results_obj"},
            "delta_spec": robustness["delta_spec"],
        },
        "granger": granger,
        "gate_passed": passed,
        "n_observations": len(df1),
    }

    results_path = Path(__file__).parent.parent / "results" / "h_m5_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"Results saved to {results_path}")

    return results


if __name__ == "__main__":
    main()
