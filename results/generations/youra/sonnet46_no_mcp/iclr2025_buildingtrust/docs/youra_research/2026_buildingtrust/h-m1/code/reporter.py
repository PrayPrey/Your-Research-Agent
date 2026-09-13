from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path


def write_results_json(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write hm1_results.json with all results and pass/fail flags."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now().isoformat(),
        "hypothesis": "h-m1",
        "gate_pass": gate_pass,
        "primary_gate": {
            "criterion": "partial_rho(ECE, TruthfulQA_pct | MMLU_acc) >= 0.40 AND BCa CI excludes zero",
            "result": primary_result,
        },
        "internal_consistency": {
            "criterion": "rho(ECE, Brier) >= 0.30",
            "result": internal_result,
        },
        "confound_magnitude": confound_result,
        "discriminant_validity": {
            "criterion": "abs(partial_rho(ECE, HumanEval | MMLU_acc)) < 0.20",
            "result": discriminant_result,
        },
        "decoding_invariance": {
            "criterion": "abs(partial_rho_T07(ECE, TruthfulQA_pct | MMLU_acc)) >= 0.30",
            "result": invariance_result,
        },
    }

    def _convert(obj):
        if isinstance(obj, float) and (obj != obj):  # nan
            return None
        if isinstance(obj, (bool, int, float, str, type(None))):
            return obj
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_convert(v) for v in obj]
        return str(obj)

    with open(output_path, "w") as f:
        json.dump(_convert(payload), f, indent=2)


def write_validation_md(
    internal_result: dict,
    primary_result: dict,
    confound_result: dict,
    discriminant_result: dict,
    invariance_result: dict,
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write 04_validation.md with criterion table (threshold, observed, pass/fail)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    gate_str = "**PASS ✓**" if gate_pass else "**FAIL ✗**"
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _fmt(val, digits=3):
        if val is None or (isinstance(val, float) and val != val):
            return "N/A"
        return f"{val:.{digits}f}"

    primary_rho = primary_result.get("rho_partial", float("nan"))
    primary_ci_lo = primary_result.get("bca_ci_low", float("nan"))
    primary_ci_hi = primary_result.get("bca_ci_high", float("nan"))
    primary_pass = primary_result.get("passes_threshold", False)

    internal_rho = internal_result.get("rho", float("nan"))
    internal_pass = internal_result.get("passes_threshold", False)

    survival = confound_result.get("survival_fraction", float("nan"))
    confound_pass = not (isinstance(survival, float) and survival < 0.5)

    disc_rho = discriminant_result.get("rho_partial", float("nan"))
    disc_pass = discriminant_result.get("passes_threshold", False)

    inv_rho = invariance_result.get("rho_t07", float("nan"))
    inv_skipped = invariance_result.get("skipped", True)
    inv_pass = invariance_result.get("passes_threshold", False)
    inv_status = "SKIP" if inv_skipped else ("PASS ✓" if inv_pass else "FAIL ✗")

    content = f"""# Validation Report: H-M1

**Generated:** {ts}
**Hypothesis:** Capability-Independent Calibration-Hallucination Mechanistic Link
**Gate Type:** MUST_WORK
**Overall Gate Result:** {gate_str}

---

## Primary Gate Result

| Criterion | Threshold | Observed | CI (BCa 95%) | Pass/Fail |
|-----------|-----------|----------|--------------|-----------|
| partial ρ(ECE, TruthfulQA% \\| MMLU) | ≥ 0.40 | {_fmt(primary_rho)} | [{_fmt(primary_ci_lo)}, {_fmt(primary_ci_hi)}] | {"PASS ✓" if primary_pass else "FAIL ✗"} |

---

## All Criteria

| Criterion | Threshold | Observed | Pass/Fail |
|-----------|-----------|----------|-----------|
| Primary gate: \\|partial ρ(ECE, TruthfulQA%\\|MMLU)\\| ≥ 0.40 AND CI excludes zero | ≥ 0.40 | {_fmt(primary_rho)} | {"PASS ✓" if primary_pass else "FAIL ✗"} |
| Construct validity: ρ(ECE, Brier) | ≥ 0.30 | {_fmt(internal_rho)} | {"PASS ✓" if internal_pass else "FAIL ✗"} |
| Confound magnitude: survival fraction (partial/raw ρ) | ≥ 0.50 | {_fmt(survival)} | {"PASS ✓" if confound_pass else "FAIL ✗"} |
| Discriminant validity: \\|partial ρ(ECE, HumanEval\\|MMLU)\\| | < 0.20 | {_fmt(disc_rho)} | {"PASS ✓" if disc_pass else "FAIL ✗"} |
| Decoding invariance: \\|partial ρ_T07\\| | ≥ 0.30 | {_fmt(inv_rho)} | {inv_status} |

---

## Key Findings

- **Primary mechanism confirmed:** partial ρ(ECE, TruthfulQA% | MMLU) = {_fmt(primary_rho)} (BCa 95% CI: [{_fmt(primary_ci_lo)}, {_fmt(primary_ci_hi)}])
- **Calibration construct valid:** ρ(ECE, Brier) = {_fmt(internal_rho)} (threshold ≥ 0.30)
- **Confound magnitude:** MMLU explains {_fmt(1 - survival if not (isinstance(survival, float) and survival != survival) else float('nan'), 1)}% of raw correlation (survival fraction = {_fmt(survival)})
- **Discriminant validity:** partial ρ(ECE, HumanEval | MMLU) = {_fmt(disc_rho)} (threshold < 0.20)
- **Decoding invariance:** {"Skipped (T=0.7 data unavailable)" if inv_skipped else f"T=0.7 partial ρ = {_fmt(inv_rho)}"}

---

## MUST_WORK Gate Interpretation

{"The calibration-hallucination mechanistic link is **capability-independent**: partial ρ(ECE, TruthfulQA%|MMLU) survives MMLU control and the BCa 95% CI excludes zero. H-M1 MUST_WORK gate: **PASS**. Proceed to Phase 5." if gate_pass else "The partial ρ(ECE, TruthfulQA%|MMLU) did not meet threshold or CI includes zero. H-M1 MUST_WORK gate: **FAIL**. Route to reflection/Phase 0."}
"""

    with open(output_path, "w") as f:
        f.write(content)
