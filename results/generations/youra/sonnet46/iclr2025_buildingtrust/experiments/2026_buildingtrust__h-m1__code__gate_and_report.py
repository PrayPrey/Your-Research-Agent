"""
gate_and_report.py — H-M1 Gate Evaluation & Validation Report

MUST_WORK gate: ECE_base < 0.15 for ALL 3 Pythia base model sizes.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Mechanism Activation Verification
# ═══════════════════════════════════════════════════════════════════════════════

def verify_mechanism_activation(
    ece_base: dict,
) -> None:
    """
    Validate ECE_base dict for completeness and value correctness.

    Args:
        ece_base: {"1.4b": float, "2.8b": float, "6.9b": float}

    Raises:
        ValueError: if validation fails
    """
    # Check all 3 sizes present
    missing = [s for s in config.BASE_SIZES if s not in ece_base]
    if missing:
        raise ValueError(
            f"ECE_base missing sizes: {missing}. Got: {list(ece_base.keys())}"
        )

    # Check all are floats in [0, 1]
    for size, val in ece_base.items():
        if not isinstance(val, (int, float)):
            raise ValueError(f"ECE_base[{size}] is not numeric: {val!r}")
        if not (0.0 <= float(val) <= 1.0):
            raise ValueError(
                f"ECE_base[{size}] = {val} is outside [0, 1]. "
                f"Calibration metric must be a probability."
            )

    logger.info("✓ Mechanism activation check passed")


# ═══════════════════════════════════════════════════════════════════════════════
# MUST_WORK Gate
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_must_work_gate(
    ece_base: dict,
    threshold: float = None,
) -> tuple:
    """
    MUST_WORK gate: ECE_base < threshold for ALL 3 sizes.

    Args:
        ece_base: {"1.4b": float, "2.8b": float, "6.9b": float}
        threshold: ECE threshold (default: config.GATE_THRESHOLD = 0.15)

    Returns:
        (gate_result: str, failed_ids: list[str])
        gate_result: "PASS" or "FAIL"
        failed_ids: list of size IDs that failed (empty on PASS)
    """
    if threshold is None:
        threshold = config.GATE_THRESHOLD

    failed_ids = []
    for size in config.BASE_SIZES:
        val = ece_base[size]
        if val >= threshold:
            failed_ids.append(size)
            logger.warning(
                f"GATE FAIL: ECE_base[{size}] = {val:.4f} >= {threshold}"
            )
        else:
            logger.info(
                f"GATE PASS: ECE_base[{size}] = {val:.4f} < {threshold}"
            )

    if failed_ids:
        logger.warning(f"MUST_WORK gate FAIL — {len(failed_ids)} size(s) failed: {failed_ids}")
        return "FAIL", failed_ids
    else:
        logger.info("MUST_WORK gate PASS — all ECE_base < 0.15")
        return "PASS", []


# ═══════════════════════════════════════════════════════════════════════════════
# ECE Ordering (ECE_base < ECE_SFT per size)
# ═══════════════════════════════════════════════════════════════════════════════

def check_ece_ordering(
    ece_base: dict,
    ece_aligned: Optional[dict] = None,
) -> dict:
    """
    Check ECE ordering: ECE_base < ECE_aligned (SFT/DPO/PPO) per size.

    Args:
        ece_base: {"1.4b": float, ...}
        ece_aligned: {"1.4b": {"sft": float, "dpo": float, "ppo": float}, ...}
                     If None, returns None for each size.

    Returns:
        dict: {"1.4b": bool|None, "2.8b": bool|None, "6.9b": bool|None}
              True = ECE_base < at least one aligned ECE (ordering holds)
              None = aligned ECE not available
    """
    ordering = {}
    for size in config.BASE_SIZES:
        base_ece = ece_base[size]
        if ece_aligned and size in ece_aligned:
            aligned_vals = ece_aligned[size]
            # Check if base is less than at least one aligned ECE (SFT is minimum)
            min_aligned = min(aligned_vals.values()) if aligned_vals else None
            if min_aligned is not None:
                holds = base_ece < min_aligned
                ordering[size] = holds
                logger.info(
                    f"ECE ordering [{size}]: base={base_ece:.4f} < "
                    f"min_aligned={min_aligned:.4f} → {holds}"
                )
            else:
                ordering[size] = None
        else:
            ordering[size] = None
            logger.info(
                f"ECE ordering [{size}]: no aligned ECE available → None"
            )

    return ordering


# ═══════════════════════════════════════════════════════════════════════════════
# Validation Report Generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_validation_report(
    ece_base: dict,
    gate_result: str,
    failed_ids: list,
    execution_path: str,
    figure_paths: list,
    ece_ordering: dict,
    ece_aligned: Optional[dict] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Write h-m1/04_validation.md with all required sections.

    Returns:
        str: path to written report file
    """
    if output_path is None:
        output_path = config.H_M1_REPORT_PATH

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    gate_icon = "✅" if gate_result == "PASS" else "❌"

    # ── ECE table ─────────────────────────────────────────────────────────────
    threshold = config.GATE_THRESHOLD
    table_rows = []
    for size in config.BASE_SIZES:
        val = ece_base[size]
        check = "✅ PASS" if val < threshold else "❌ FAIL"
        model_label = f"Pythia-{size.upper()}"
        table_rows.append(f"| {model_label} | {val:.4f} | {check} |")
    table_str = "\n".join(table_rows)

    # ── Key findings ──────────────────────────────────────────────────────────
    all_pass = gate_result == "PASS"
    findings = []

    if all_pass:
        findings.append(
            f"MUST_WORK gate **PASSED**: all 3 Pythia base models show ECE < {threshold}."
        )
        findings.append(
            "Pretraining without alignment produces well-calibrated logit distributions."
        )
        findings.append(
            f"Lowest ECE: Pythia-{min(ece_base, key=ece_base.get).upper()} "
            f"({min(ece_base.values()):.4f}); "
            f"Highest ECE: Pythia-{max(ece_base, key=ece_base.get).upper()} "
            f"({max(ece_base.values()):.4f})."
        )
        findings.append(
            "Base model calibration confirmed as causal baseline for H-M2/M3/M4 "
            "mechanism analysis (alignment-induced ECE shifts)."
        )
    else:
        findings.append(
            f"MUST_WORK gate **FAILED**: ECE_base >= {threshold} for sizes: {failed_ids}."
        )
        findings.append(
            "Base models show unexpected overconfidence before alignment training."
        )
        findings.append(
            "Hypothesis H-M1 causal premise may not hold for these model sizes. "
            "Recommend reviewing pretraining procedure or evaluation setup."
        )
        for size in failed_ids:
            findings.append(
                f"Pythia-{size.upper()} ECE_base = {ece_base[size]:.4f} (threshold: {threshold})."
            )

    # ── ECE ordering section ──────────────────────────────────────────────────
    ordering_lines = []
    for size in config.BASE_SIZES:
        val = ece_ordering.get(size)
        if val is None:
            ordering_lines.append(f"- Pythia-{size.upper()}: ECE_base = {ece_base[size]:.4f} (aligned ECE not available in this run)")
        elif val:
            ordering_lines.append(f"- Pythia-{size.upper()}: ECE_base ({ece_base[size]:.4f}) < aligned ECE ✅")
        else:
            ordering_lines.append(f"- Pythia-{size.upper()}: ECE_base ({ece_base[size]:.4f}) >= aligned ECE ⚠️")
    ordering_str = "\n".join(ordering_lines)

    # ── Figure paths section ──────────────────────────────────────────────────
    if figure_paths:
        fig_lines = "\n".join(f"- `{p}`" for p in figure_paths)
    else:
        fig_lines = "- No figures generated."

    # ── Assemble report ───────────────────────────────────────────────────────
    report = f"""# H-M1 Validation Report

**Generated:** {ts}
**Hypothesis:** H-M1 — Base Calibration Verification (ECE_base < 0.15)
**Gate Type:** MUST_WORK

---

## 1. Gate Result

**Gate Verdict:** {gate_icon} {gate_result}
**Threshold:** ECE_base < {threshold} for ALL 3 Pythia base sizes (1.4B, 2.8B, 6.9B)
**Execution Path:** {execution_path}

| Model | ECE_base | Gate Check |
|-------|----------|------------|
{table_str}

---

## 2. Key Findings

"""
    for i, finding in enumerate(findings, 1):
        report += f"{i}. {finding}\n"

    report += f"""
---

## 3. ECE Ordering (Base vs Aligned)

{ordering_str}

*(Full aligned ECE values available in H-E1 04_validation.md)*

---

## 4. Figure Paths

{fig_lines}

---

## 5. Execution Details

- **Execution Path:** {execution_path}
- **Gate Threshold:** {threshold}
- **Base Sizes Evaluated:** {config.BASE_SIZES}
- **N Calibration Bins:** {config.N_BINS}
- **Timestamp:** {ts}

---

## 6. Failure Analysis

"""
    if all_pass:
        report += "No gate failure. H-M1 confirms causal baseline: pretraining yields ECE < 0.15.\n"
    else:
        report += f"Gate failed for sizes: {failed_ids}. ECE_base values exceed threshold {threshold}.\n"
        report += "Possible causes: evaluation setup mismatch, model variant differences, or MMLU sampling.\n"

    report += f"""
---

## 7. Next Steps

"""
    if all_pass:
        report += "- H-M1 gate PASSED. H-M2 (logit margin inflation mechanism) is now READY.\n"
        report += "- Proceed with hypothesis loop: Phase 2C → 3 → 4 for H-M2.\n"
    else:
        report += "- H-M1 gate FAILED. Return to Phase 2A for hypothesis redesign.\n"
        report += "- Investigate base model calibration anomaly before proceeding.\n"

    # Write file
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    logger.info(f"✓ Validation report written: {output_path}")

    return str(output_path)
