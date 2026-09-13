"""Results logging: JSON results aggregation and 04_validation.md generation."""
import json
import os
import math
from datetime import datetime
from typing import Dict


def save_results_json(results: Dict, path: str) -> None:
    """Save all experiment results to experiment_results.json."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def _make_serializable(obj):
        if isinstance(obj, dict):
            return {k: _make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_make_serializable(i) for i in obj]
        elif hasattr(obj, "tolist"):  # numpy arrays
            return obj.tolist()
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        elif hasattr(obj, "item"):  # numpy scalars
            return obj.item()
        return obj

    serializable = _make_serializable(results)
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"[RESULTS] Saved to {path}")


def log_sensitivity_indicators(
    layer_idx: int,
    accuracy_drop: float,
    sensitive_threshold: float,
) -> None:
    """Print: [SENSITIVITY] Layer {l}: accuracy_drop={drop:.4f}, sensitive={...}"""
    sensitive = accuracy_drop >= sensitive_threshold
    print(f"[SENSITIVITY] Layer {layer_idx}: accuracy_drop={accuracy_drop:.4f}, sensitive={sensitive}")


def print_gate_summary(gate_result: Dict) -> None:
    """Print gate evaluation summary to stdout."""
    status = "PASS" if gate_result.get("gate_pass") else "FAIL"
    print(f"\n{'='*60}")
    print(f"[GATE] MUST_WORK: {status}")
    print(f"{'='*60}")
    metrics = gate_result.get("all_metrics", {})
    for k, v in metrics.items():
        if isinstance(v, float) and not math.isnan(v):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print(f"  gate_pearson: {gate_result.get('gate_pearson')}")
    print(f"  gate_tau: {gate_result.get('gate_tau')}")
    print(f"  gate_spectral: {gate_result.get('gate_spectral')}")
    print(f"  r6_fallback: {gate_result.get('r6_fallback')}")
    print(f"{'='*60}")


def generate_validation_report(
    results: Dict,
    gate_result: Dict,
    cfg,
    output_path: str,
) -> None:
    """Generate 04_validation.md with gate evaluation, metrics, and PASS/FAIL status."""
    gate_pass = gate_result.get("gate_pass", False)
    status_emoji = "✅ PASS" if gate_pass else "❌ FAIL"
    metrics = gate_result.get("all_metrics", {})
    r6_fallback = gate_result.get("r6_fallback", False)

    def fmt(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return "N/A"
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v)

    pearson_sst2 = fmt(metrics.get("pearson_r_sst2"))
    pearson_mnli = fmt(metrics.get("pearson_r_mnli"))
    tau_sst2 = fmt(metrics.get("kendall_tau_sst2"))
    tau_mnli = fmt(metrics.get("kendall_tau_mnli"))
    unique_var = fmt(metrics.get("unique_var_sparsity"))
    p_val = fmt(metrics.get("p_value_sparsity_beta"))
    n_sens_sst2 = metrics.get("n_sensitive_sst2", "N/A")

    regression = results.get("regression_results", {})
    r2_full = fmt(regression.get("r2_full"))
    r2_grad = fmt(regression.get("r2_grad_only"))

    baseline_accs = results.get("baseline_accs", {})
    sst2_acc = fmt(baseline_accs.get("sst2", {}).get("mean", None))
    mnli_acc = fmt(baseline_accs.get("mnli", {}).get("mean", None))

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    report = f"""# H-M3 Validation Report

**Hypothesis:** H-M3 (MECHANISM) — Sparsity-Rank Sensitivity Correlation
**Gate Type:** MUST_WORK
**Result:** {status_emoji}
**Generated:** {timestamp}

---

## Gate Evaluation Summary

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| Pearson r (SST-2) | {pearson_sst2} | ≤ {cfg.pearson_r_threshold} | {"✅" if gate_result.get("gate_pearson") else "❌"} |
| Pearson r (MNLI) | {pearson_mnli} | ≤ {cfg.pearson_r_threshold} | {"✅" if gate_result.get("gate_pearson") else "❌"} |
| Kendall τ (SST-2) | {tau_sst2} | ≥ {cfg.kendall_tau_threshold} | {"✅" if gate_result.get("gate_tau") else "❌"} |
| Kendall τ (MNLI) | {tau_mnli} | ≥ {cfg.kendall_tau_threshold} | {"✅" if gate_result.get("gate_tau") else "❌"} |
| Unique Variance (Sparsity) | {unique_var} | ≥ {cfg.unique_var_threshold} | {"✅" if gate_result.get("gate_spectral") else "❌"} |
| p-value (Sparsity β) | {p_val} | < {cfg.p_value_threshold} | {"✅" if gate_result.get("gate_spectral") else "❌"} |

**R6 Fallback Applied:** {"Yes" if r6_fallback else "No"} (n_sensitive_sst2={n_sens_sst2}, threshold={cfg.r6_min_sensitive_layers})

---

## Stream Analysis

### Stream 1: Joint Rank Sensitivity Sweep

- Sensitive layers threshold: accuracy_drop ≥ {cfg.sensitive_drop_threshold} (0.5%)
- SST-2 sensitive layers: {n_sens_sst2}
- Baseline accuracy: SST-2={sst2_acc}, MNLI={mnli_acc}

### Stream 2: AdaLoRA Reference

- AdaLoRA target_r: {cfg.adalora_target_r} (60% of r=16 budget)
- Kendall τ (SST-2): {tau_sst2}
- Kendall τ (MNLI): {tau_mnli}

### Stream 3: Delta-W Spectral Analysis

- R² (full: sparsity + grad_norm): {r2_full}
- R² (reduced: grad_norm only): {r2_grad}
- Unique variance of sparsity: {unique_var}
- p-value for sparsity coefficient: {p_val}

---

## Key Findings

{"1. ✅ Sparsity negatively predicts sensitivity (Pearson r ≤ −0.4 on sensitive layers)" if gate_result.get("gate_pearson") else "1. ❌ Pearson r gate failed"}
{"2. ✅ AdaLoRA rank allocation correlates with sparsity ranking (Kendall τ ≥ 0.4)" if gate_result.get("gate_tau") else "2. ❌ Kendall tau gate failed"}
{"3. ✅ Sparsity explains ≥20% unique variance in spectral decay (p < 0.05)" if gate_result.get("gate_spectral") else "3. ❌ Spectral variance gate failed"}

---

## MUST_WORK Gate

**Gate Result: {status_emoji}**

{"The mechanism is validated: sparse layers require lower LoRA rank for effective adaptation. This supports H-M3's central claim." if gate_pass else "The mechanism could not be validated. Review gate failures above and consider hypothesis revision."}

---

*Generated by Anonymous Pipeline Phase 4 — H-M3 Validation*
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"[REPORT] Validation report saved to {output_path}")
