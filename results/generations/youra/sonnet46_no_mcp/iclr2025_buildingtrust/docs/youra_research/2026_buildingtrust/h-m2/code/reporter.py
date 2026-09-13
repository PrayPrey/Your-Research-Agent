from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def _to_serializable(obj):
    """Recursively convert numpy types to Python native for JSON serialization."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def write_results_json(
    partial_result: dict,
    composite_auc: dict,
    baseline_auc: dict,
    delta_result: dict,
    gate_pass: bool,
    path: Path,
) -> None:
    """Save all gate metric dicts to hm2_results.json."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    results = {
        "hypothesis_id": "h-m2",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "gate_pass": gate_pass,
        "partial_rho": _to_serializable(partial_result),
        "composite_auc": _to_serializable({k: v for k, v in composite_auc.items()
                                           if k not in ("y_proba", "y_true")}),
        "baseline_auc": _to_serializable({k: v for k, v in baseline_auc.items()
                                          if k not in ("y_proba", "y_true")}),
        "delta_bootstrap": _to_serializable(delta_result),
    }
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def _gate_label(delta_result: dict) -> str:
    auc_c = delta_result["auc_composite"]
    delta = delta_result["delta_auc"]
    ci_lo = delta_result["delta_auc_ci"][0]
    if auc_c >= config.AUC_THRESHOLD and delta >= config.DELTA_AUC_THRESHOLD and ci_lo > 0:
        return "PASS"
    elif auc_c >= 0.60 or delta >= 0.05:
        return "PARTIAL"
    else:
        return "EXPLORE"


def write_validation_md(
    partial_result: dict,
    composite_auc: dict,
    baseline_auc: dict,
    delta_result: dict,
    gate_pass: bool,
    path: Path,
) -> None:
    """Generate 04_validation.md with pass/fail status for each gate criterion."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    gate_label = _gate_label(delta_result)
    ts = datetime.utcnow().isoformat() + "Z"

    rho_adv = partial_result["rho_partial_advglue"]
    ci_lo_adv = partial_result["bca_ci_low"]
    ci_hi_adv = partial_result["bca_ci_high"]
    passes_rho = partial_result["passes_threshold"]

    rho_anli = partial_result["rho_partial_anli"]
    ci_lo_anli = partial_result["anli_bca_ci_low"]
    ci_hi_anli = partial_result["anli_bca_ci_high"]

    auc_c = delta_result["auc_composite"]
    auc_b = delta_result["auc_baseline"]
    delta = delta_result["delta_auc"]
    d_ci_lo, d_ci_hi = delta_result["delta_auc_ci"]
    passes_auc = delta_result["passes_auc_threshold"]
    passes_delta = delta_result["passes_delta_threshold"]

    def _check(ok: bool) -> str:
        return "✅ PASS" if ok else "❌ FAIL"

    content = f"""# H-M2 Validation Report

**Hypothesis:** Epistemic composite (ECE + TruthfulQA% + Brier) predicts top-quartile AdvGLUE failure
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_label}
**Generated:** {ts}

---

## Gate Criteria

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| partial ρ(ECE, AdvGLUE\\|MMLU) | {rho_adv:.4f} | ≥ 0.40 (abs) | {_check(passes_rho)} |
| BCa 95% CI excludes zero | [{ci_lo_adv:.4f}, {ci_hi_adv:.4f}] | CI excl. zero | {_check(partial_result["ci_excludes_zero"])} |
| LOO-AUC composite | {auc_c:.4f} | ≥ 0.70 | {_check(passes_auc)} |
| ΔR² (composite - baseline) | {delta:.4f} | ≥ 0.10 | {_check(passes_delta)} |
| ΔR² CI excludes zero | [{d_ci_lo:.4f}, {d_ci_hi:.4f}] | CI lo > 0 | {_check(delta_result["ci_excludes_zero"])} |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| partial ρ(ECE, AdvGLUE\\|MMLU) | {rho_adv:.4f} (BCa 95% CI [{ci_lo_adv:.4f}, {ci_hi_adv:.4f}]) |
| partial ρ(ECE, ANLI\\|MMLU) | {rho_anli:.4f} (BCa 95% CI [{ci_lo_anli:.4f}, {ci_hi_anli:.4f}]) |
| LOO-AUC composite | {auc_c:.4f} |
| LOO-AUC MMLU-only | {auc_b:.4f} |
| ΔAUC | {delta:.4f} (95% CI [{d_ci_lo:.4f}, {d_ci_hi:.4f}]) |

---

## Figures

| Figure | Description |
|--------|-------------|
| fig1_gate_metrics_comparison.png | LOO-AUC comparison bar chart |
| fig2_roc_curves_comparison.png | ROC curve overlay |
| fig3_partial_correlation_comparison.png | Partial rho comparison |
| fig4_advglue_drop_distribution.png | AdvGLUE drop distribution |
| fig5_feature_importance.png | LOO logistic regression coefficients |
| fig6_epistemic_vs_adversarial_scatter.png | PC1 composite vs AdvGLUE scatter |

---

## Interpretation

{"The composite epistemic predictor (ECE + TruthfulQA% + Brier) **passes** the SHOULD_WORK gate: AUC ≥ 0.70 and ΔAUC ≥ 0.10 with CI excluding zero. H-M3 proceeds." if gate_label == "PASS" else
 f"The composite epistemic predictor achieves gate result **{gate_label}**. H-M3 proceeds regardless of H-M2 outcome (SHOULD_WORK gate)."}

**Prerequisite confirmation (H-E1 + H-M1):** Results build on confirmed partial ρ(ECE, TruthfulQA%|MMLU) = -0.758 and survival fraction 0.943 from H-M1.

---

## Conclusion

Gate: **{gate_label}** → Proceed to H-M3 in all cases (SHOULD_WORK).
"""
    with open(path, "w") as f:
        f.write(content)
