"""Gate criterion evaluation: ratio + CI non-overlap test."""
from config import GATE_RATIO_THRESHOLD


def evaluate_gate(regression_results: dict) -> dict:
    """
    Evaluate SHOULD_WORK gate:
      PASS: ratio >= 2.0 AND CIs non-overlapping
      PARTIAL: ratio >= 2.0 but CIs overlap, OR ratio < 2.0 but SSM beta significantly < 0
      FAIL: ratio < 2.0 AND no significant depth effect for SSM

    Returns gate evaluation dict.
    """
    ssm = regression_results["mohawk_ssm"]
    lawcat = regression_results["lawcat"]
    holm_p = regression_results["holm_corrected_p_values"]

    beta_ssm = ssm["beta"]
    beta_lawcat = lawcat["beta"]

    # Ratio of absolute depth coefficients
    ratio = abs(beta_ssm) / max(abs(beta_lawcat), 1e-9)

    # CI non-overlap: SSM CI and LAWCAT CI do NOT overlap
    # (both are for depth_percentile coefficient)
    ssm_ci_low, ssm_ci_high = ssm["ci_low"], ssm["ci_high"]
    lawcat_ci_low, lawcat_ci_high = lawcat["ci_low"], lawcat["ci_high"]
    ci_overlap = (ssm_ci_high >= lawcat_ci_low) and (lawcat_ci_high >= ssm_ci_low)

    # Gate verdict
    ssm_significant = holm_p["mohawk_ssm"] < 0.05 and beta_ssm < 0
    if ratio >= GATE_RATIO_THRESHOLD and not ci_overlap:
        verdict = "PASS"
    elif ratio >= GATE_RATIO_THRESHOLD or ssm_significant:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    result = {
        "gate_pass": verdict == "PASS",
        "verdict": verdict,
        "ratio": round(ratio, 4),
        "ratio_threshold": GATE_RATIO_THRESHOLD,
        "ci_overlap": ci_overlap,
        "ssm_ci": [ssm_ci_low, ssm_ci_high],
        "lawcat_ci": [lawcat_ci_low, lawcat_ci_high],
        "beta_ssm": round(beta_ssm, 4),
        "beta_lawcat": round(beta_lawcat, 4),
        "ssm_significant_negative": ssm_significant,
        "holm_p_ssm": round(holm_p["mohawk_ssm"], 4),
        "holm_p_lawcat": round(holm_p["lawcat"], 4),
    }

    print(f"[Gate] β_SSM={beta_ssm:.4f}, β_LAWCAT={beta_lawcat:.4f}")
    print(f"[Gate] Ratio={ratio:.4f} (threshold={GATE_RATIO_THRESHOLD})")
    print(f"[Gate] CI overlap: {ci_overlap}")
    print(f"[Gate] Verdict: {verdict}")

    return result
