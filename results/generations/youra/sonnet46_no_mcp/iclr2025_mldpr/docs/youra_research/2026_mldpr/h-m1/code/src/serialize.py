"""H-M1 results serialization: JSON + CSV output, gate_result.json PASS/FAIL."""
import json
import os
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def _make_serializable(obj):
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, pd.Series):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items() if not callable(v) and k not in ("cph_model", "kmf_high", "kmf_low")}
    if isinstance(obj, list):
        return [_make_serializable(i) for i in obj]
    return obj


def build_results_dict(
    primary: dict,
    unadjusted: dict,
    matching_meta: dict,
    ablations: dict,
    sensitivity: dict,
) -> dict:
    """Assemble canonical results dict (FR-9 schema)."""
    return {
        "log_rank_p": primary.get("log_rank_p"),
        "cox_hr": primary.get("cox_hr"),
        "cox_ci_lower": primary.get("cox_ci_lower"),
        "cox_ci_upper": primary.get("cox_ci_upper"),
        "cox_p": primary.get("cox_p"),
        "median_ttfr_high": primary.get("median_ttfr_high"),
        "median_ttfr_low": primary.get("median_ttfr_low"),
        "n_matched_pairs": matching_meta.get("n_matched_pairs"),
        "smd_max": matching_meta.get("smd_max"),
        "n_cohort_filtered": primary.get("n_cohort_filtered"),
        "baseline_log_rank_p": unadjusted.get("baseline_log_rank_p"),
        "baseline_cox_hr": unadjusted.get("baseline_cox_hr"),
        "ablations": ablations,
        "sensitivity": sensitivity,
    }


def save_results(results: dict, results_dir: str) -> dict:
    """Save results to JSON and CSV files."""
    os.makedirs(results_dir, exist_ok=True)
    json_path = os.path.join(results_dir, "results.json")
    csv_path = os.path.join(results_dir, "results.csv")
    serializable = _make_serializable(results)
    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2)
    flat = {k: v for k, v in serializable.items() if not isinstance(v, (dict, list))}
    pd.DataFrame([flat]).to_csv(csv_path, index=False)
    logger.info(f"Results saved: {json_path}, {csv_path}")
    return {"json_path": json_path, "csv_path": csv_path}


def save_gate_result(
    results: dict,
    results_dir: str,
    log_rank_alpha: float,
    cox_hr_gate: float,
) -> str:
    """Save gate_result.json with PASS/FAIL determination."""
    os.makedirs(results_dir, exist_ok=True)
    log_rank_p = results.get("log_rank_p", 1.0)
    cox_hr = results.get("cox_hr", 0.0)
    median_high = results.get("median_ttfr_high", float("inf"))
    median_low = results.get("median_ttfr_low", 0.0)
    primary_pass = (
        log_rank_p is not None and log_rank_p < log_rank_alpha and
        median_high is not None and median_low is not None and median_high < median_low
    )
    secondary_pass = cox_hr is not None and cox_hr > cox_hr_gate
    gate_result = "PASS" if primary_pass else "FAIL"
    gate = {
        "result": gate_result,
        "primary_gate": {
            "log_rank_p": log_rank_p,
            "threshold": log_rank_alpha,
            "passed": bool(primary_pass),
        },
        "secondary_gate": {
            "cox_hr": cox_hr,
            "threshold": cox_hr_gate,
            "passed": bool(secondary_pass),
        },
        "median_ttfr_high": median_high,
        "median_ttfr_low": median_low,
        "n_matched_pairs": results.get("n_matched_pairs"),
        "smd_max": results.get("smd_max"),
    }
    path = os.path.join(results_dir, "gate_result.json")
    with open(path, "w") as f:
        json.dump(_make_serializable(gate), f, indent=2)
    logger.info(f"Gate result: {gate_result} (log_rank_p={log_rank_p:.4f}, cox_hr={cox_hr:.3f})")
    return path
