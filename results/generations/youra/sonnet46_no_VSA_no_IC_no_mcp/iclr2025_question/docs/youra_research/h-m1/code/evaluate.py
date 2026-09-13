"""Gate verification and metrics for H-M1."""
import json
import os
import numpy as np


def verify_mechanism_activated(
    results: list,
    intra_var_threshold: float = 0.1,
    min_passing: int = 15,
    min_eligible: int = 20,
) -> tuple:
    """
    Primary gate: mean_intra_var > threshold on >=min_passing eligible questions.
    Returns (primary_pass, indicators).
    """
    eligible = [r for r in results if r["has_paraphrase"]]
    assert len(eligible) >= min_eligible, f"Only {len(eligible)} eligible; need {min_eligible}"
    passing = [
        r for r in eligible
        if r["mean_intra_var"] is not None and r["mean_intra_var"] > intra_var_threshold
    ]
    primary_pass = len(passing) >= min_passing
    valid_vars = [r["mean_intra_var"] for r in eligible if r["mean_intra_var"] is not None]
    indicators = {
        "n_eligible_questions": len(eligible),
        "n_passing_primary_threshold": len(passing),
        "primary_criterion_met": primary_pass,
        "mean_variance_overall": float(np.mean(valid_vars)) if valid_vars else 0.0,
        "fraction_passing": len(passing) / len(eligible) if eligible else 0.0,
        "intra_var_threshold": intra_var_threshold,
        "min_passing": min_passing,
    }
    print(
        f"[H-M1] eligible={len(eligible)}, passing={len(passing)}, "
        f"mean_var={indicators['mean_variance_overall']:.4f} nats², "
        f"fraction={indicators['fraction_passing']:.3f}, GATE={'PASS' if primary_pass else 'FAIL'}"
    )
    return primary_pass, indicators


def compute_secondary_metrics(
    results: list,
    variance_thresholds: list = (0.05, 0.1, 0.2, 0.5),
) -> dict:
    """Threshold sensitivity, high/low uncertainty strata, inter>intra fraction."""
    eligible = [r for r in results if r["has_paraphrase"] and r["mean_intra_var"] is not None]
    if not eligible:
        return {}

    threshold_sensitivity = {}
    for t in variance_thresholds:
        frac = sum(1 for r in eligible if r["mean_intra_var"] > t) / len(eligible)
        threshold_sensitivity[t] = float(frac)

    high_u = [r["mean_intra_var"] for r in eligible if r["high_uncertainty"] and r["mean_intra_var"] is not None]
    low_u = [r["mean_intra_var"] for r in eligible if not r["high_uncertainty"] and r["mean_intra_var"] is not None]

    inter_gt_intra = sum(
        1 for r in eligible
        if r["inter_var"] is not None and r["mean_intra_var"] is not None
        and r["inter_var"] > r["mean_intra_var"]
    ) / len(eligible)

    return {
        "threshold_sensitivity": threshold_sensitivity,
        "high_uncertainty_mean_var": float(np.mean(high_u)) if high_u else 0.0,
        "low_uncertainty_mean_var": float(np.mean(low_u)) if low_u else 0.0,
        "inter_gt_intra_fraction": float(inter_gt_intra),
        "n_eligible": len(eligible),
    }


def save_results(
    results: list,
    indicators: dict,
    secondary: dict,
    primary_pass: bool,
    out_dir: str,
) -> None:
    os.makedirs(out_dir, exist_ok=True)
    # Strip per_sample_te list from results for JSON (keep metrics only)
    results_slim = [{k: v for k, v in r.items() if k != "per_sample_te"} for r in results]
    with open(os.path.join(out_dir, "h_m1_results.json"), "w") as f:
        json.dump(results_slim, f, indent=2)
    summary = {
        "verdict": "PASS" if primary_pass else "FAIL",
        "gate_type": "MUST_WORK",
        "indicators": indicators,
        "secondary": secondary,
    }
    with open(os.path.join(out_dir, "h_m1_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[H-M1] Results saved to {out_dir}")
