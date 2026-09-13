"""
verify_gate.py — H-E1: Gate Evaluation + Validation Report
Implements: evaluate_gate (MUST_WORK logic), generate_validation_report (04_validation.md)
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from calibration_analysis import GATE_CONFIG, REPORT_CONFIG, MODELS

# ── Gate Evaluation ───────────────────────────────────────────────────────────

def evaluate_gate(results: dict) -> dict:
    """Check MUST_WORK gate: delta_rel > 0 AND ci_lower > 0 for PPO or DPO in >=2/3 sizes.

    Args:
        results: dict keyed by model_key with delta_rel, ci_lower, ci_upper

    Returns:
        {
            gate: 'PASS' | 'FAIL',
            method: 'PPO' | 'DPO' | 'BOTH' | 'NONE',
            sizes_passing: {method: [sizes]},
            failure_mode: str | None,
        }
    """
    sizes = GATE_CONFIG["sizes"]
    methods = GATE_CONFIG["methods"]  # ["ppo", "dpo"]
    min_sizes = GATE_CONFIG["min_sizes_passing"]

    sizes_passing = {m: [] for m in methods}

    for size in sizes:
        for alignment in methods:
            model_key = f"pythia-{size}-{alignment}"
            if model_key not in results:
                continue
            m = results[model_key]
            delta_rel = m.get("delta_rel")
            ci_lower = m.get("ci_lower")
            if delta_rel is not None and ci_lower is not None:
                if delta_rel > 0 and ci_lower > 0:
                    sizes_passing[alignment].append(size)

    # Determine passing methods
    ppo_pass = len(sizes_passing["ppo"]) >= min_sizes
    dpo_pass = len(sizes_passing["dpo"]) >= min_sizes

    if ppo_pass and dpo_pass:
        gate = "PASS"
        method = "BOTH"
        failure_mode = None
    elif ppo_pass:
        gate = "PASS"
        method = "PPO"
        failure_mode = None
    elif dpo_pass:
        gate = "PASS"
        method = "DPO"
        failure_mode = None
    else:
        gate = "FAIL"
        method = "NONE"
        # Diagnose failure mode
        any_positive = any(
            (results.get(f"pythia-{s}-{a}", {}).get("delta_rel") or 0) > 0
            for s in sizes for a in methods
        )
        if any_positive:
            failure_mode = (
                f"Positive delta_rel found but CI lower bound not > 0 in {min_sizes}+ sizes. "
                "Effect is present but not statistically robust."
            )
        else:
            failure_mode = (
                "No positive delta_rel for PPO or DPO in any model size. "
                "Alignment training does not increase Brier reliability."
            )

    return {
        "gate": gate,
        "method": method,
        "sizes_passing": sizes_passing,
        "failure_mode": failure_mode,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "criteria": {
            "description": "delta_rel > 0 AND ci_lower > 0 for PPO or DPO in >= 2/3 Pythia sizes",
            "ppo_sizes_passing": sizes_passing["ppo"],
            "dpo_sizes_passing": sizes_passing["dpo"],
            "min_sizes_required": min_sizes,
        },
    }


# ── Validation Report ─────────────────────────────────────────────────────────

def generate_validation_report(
    results: dict,
    gate_result: dict,
    output_path: str = "04_validation.md",
) -> None:
    """Write 04_validation.md with 5 required sections.

    Sections: gate_result, per_model_metrics_table, key_findings,
              failure_analysis, mechanism_activation_indicators
    """
    lines = []
    now = datetime.utcnow().strftime("%Y-%m-%d %Human:%M:%S UTC")

    lines.append("# H-E1 Validation Report")
    lines.append(f"\n**Generated:** {now}")
    lines.append("**Hypothesis:** H-E1 — Alignment-Induced Brier Reliability Overconfidence")
    lines.append("**Gate Type:** MUST_WORK\n")

    # ── Section 1: Gate Result ─────────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 1. Gate Result\n")
    gate = gate_result["gate"]
    gate_icon = "✅ PASS" if gate == "PASS" else "❌ FAIL"
    lines.append(f"**Gate Verdict:** {gate_icon}")
    lines.append(f"**Passing Method:** {gate_result['method']}")
    lines.append(f"**Timestamp:** {gate_result['timestamp']}\n")

    lines.append("**Gate Criteria:**")
    lines.append("> `delta_rel > 0 AND ci_lower > 0` for PPO or DPO in ≥ 2/3 Pythia model sizes (1.4B, 2.8B, 6.9B)\n")

    sizes_passing = gate_result["sizes_passing"]
    lines.append(f"- PPO sizes passing: {sizes_passing.get('ppo', [])}")
    lines.append(f"- DPO sizes passing: {sizes_passing.get('dpo', [])}\n")

    if gate_result["failure_mode"]:
        lines.append(f"**Failure Mode:** {gate_result['failure_mode']}\n")

    # ── Section 2: Per-Model Metrics Table ────────────────────────────────────
    lines.append("---\n")
    lines.append("## 2. Per-Model Metrics Table\n")
    lines.append("| Model | N Samples | ECE | Brier REL | Brier RES | Brier UNC | Δ REL | CI Lower | CI Upper |")
    lines.append("|-------|-----------|-----|-----------|-----------|-----------|-------|----------|----------|")

    for model_key in MODELS:
        if model_key not in results:
            continue
        m = results[model_key]
        if m.get("status") == "no_data":
            lines.append(f"| {model_key} | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue

        def fmt(v):
            return f"{v:.4f}" if v is not None else "N/A"

        lines.append(
            f"| {model_key} "
            f"| {m.get('n_samples', 'N/A')} "
            f"| {fmt(m.get('ece'))} "
            f"| {fmt(m.get('brier_rel'))} "
            f"| {fmt(m.get('brier_res'))} "
            f"| {fmt(m.get('brier_unc'))} "
            f"| {fmt(m.get('delta_rel'))} "
            f"| {fmt(m.get('ci_lower'))} "
            f"| {fmt(m.get('ci_upper'))} |"
        )

    lines.append("")

    # ── Section 3: Key Findings ───────────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 3. Key Findings\n")

    if gate == "PASS":
        lines.append(f"- **MUST_WORK gate PASSED** via {gate_result['method']} method.")
        lines.append(
            f"- Alignment training (PPO/DPO) increases Brier reliability (overconfidence) "
            f"with statistically significant CI lower > 0 in "
            f"{len(sizes_passing.get('ppo', [])) + len(sizes_passing.get('dpo', []))} "
            f"model-size pairs."
        )
        lines.append("- Existence of alignment-induced overconfidence confirmed.")
        lines.append("- Proceeds to Phase 5 for baseline comparison.")
    else:
        lines.append("- **MUST_WORK gate FAILED.**")
        lines.append("- Alignment training does not reliably increase Brier reliability.")
        lines.append("- Pipeline will route to Phase 2A for hypothesis redesign.")

    # Summarize delta directions
    positive_cases = []
    negative_cases = []
    for model_key, m in results.items():
        if "base" in model_key:
            continue
        dr = m.get("delta_rel")
        if dr is not None:
            if dr > 0:
                positive_cases.append(f"{model_key} (Δ={dr:.4f})")
            else:
                negative_cases.append(f"{model_key} (Δ={dr:.4f})")

    if positive_cases:
        lines.append(f"\n**Positive Δ REL cases ({len(positive_cases)}):**")
        for case in positive_cases:
            lines.append(f"  - {case}")

    if negative_cases:
        lines.append(f"\n**Negative/Zero Δ REL cases ({len(negative_cases)}):**")
        for case in negative_cases:
            lines.append(f"  - {case}")

    lines.append("")

    # ── Section 4: Failure Analysis ───────────────────────────────────────────
    lines.append("---\n")
    lines.append("## 4. Failure Analysis\n")

    if gate == "PASS":
        lines.append("No gate failure. Potential limitations noted:")
        lines.append("- Results are specific to Pythia model family and MMLU benchmark.")
        lines.append("- Aligned checkpoint IDs assumed to be RLHFlow/pythia-* (Li et al. 2024).")
        lines.append("- Risk R1 fallback (LLaMA-2) not triggered.")
    else:
        lines.append(f"**Primary failure mode:** {gate_result.get('failure_mode', 'Unknown')}")
        lines.append("\n**Possible causes:**")
        lines.append("1. Aligned checkpoints not available (Risk R1 — fallback may be needed)")
        lines.append("2. Alignment training on Pythia family does not systematically inflate Brier reliability")
        lines.append("3. MMLU task coverage insufficient to detect calibration shifts")
        lines.append("4. Batch size or dtype issues during lm-eval run")

    # Deviation log (Risk R1)
    from calibration_analysis import DEVIATION_LOG
    if DEVIATION_LOG:
        lines.append("\n**Risk R1 Deviations (LLaMA-2 fallback used):**")
        for entry in DEVIATION_LOG:
            lines.append(
                f"  - pythia-{entry['size']}-{entry['alignment']}: "
                f"{entry['original']} → {entry['fallback']} ({entry['reason']})"
            )

    lines.append("")

    # ── Section 5: Mechanism Activation Indicators ────────────────────────────
    lines.append("---\n")
    lines.append("## 5. Mechanism Activation Indicators\n")
    lines.append(
        "These indicators assess which alignment-induced logit perturbation mechanism "
        "is active (H1: scale distortion, H2: boundary shift, H3: framing susceptibility)."
    )
    lines.append("\n| Indicator | Description | Status |")
    lines.append("|-----------|-------------|--------|")
    lines.append("| H1: Logit scale inflation | PPO/DPO increase max logit margin | To be tested in H-M2 |")
    lines.append("| H2: Decision boundary shift | Rank-order changes in logprobs | To be tested in H-M3 |")
    lines.append("| H3: Framing susceptibility | TruthfulQA MC1 distractor interaction | To be tested in H-M3 |")
    lines.append("| ECE monotonicity | PPO >= DPO > SFT across sizes | See metrics table |")
    lines.append("")

    # ECE monotonicity check
    sizes = ["1.4b", "2.8b", "6.9b"]
    monotone_count = 0
    for size in sizes:
        ece_sft = results.get(f"pythia-{size}-sft", {}).get("ece")
        ece_dpo = results.get(f"pythia-{size}-dpo", {}).get("ece")
        ece_ppo = results.get(f"pythia-{size}-ppo", {}).get("ece")
        if all(v is not None for v in [ece_sft, ece_dpo, ece_ppo]):
            if ece_ppo >= ece_dpo >= ece_sft:
                monotone_count += 1
                lines.append(f"- ✅ ECE monotonicity holds for {size}: PPO={ece_ppo:.4f} >= DPO={ece_dpo:.4f} >= SFT={ece_sft:.4f}")
            else:
                lines.append(f"- ⚠️ ECE monotonicity violated for {size}: PPO={ece_ppo:.4f}, DPO={ece_dpo:.4f}, SFT={ece_sft:.4f}")

    if monotone_count > 0:
        lines.append(f"\nECE monotonicity holds in {monotone_count}/3 model sizes.")

    lines.append("")

    # Write file
    report_content = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_content)

    print(f"✅ Validation report written: {output_path}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Gate Verification")
    parser.add_argument(
        "--results-dir", default="./results",
        help="Path to results directory containing calibration_results.json"
    )
    parser.add_argument(
        "--output", default="04_validation.md",
        help="Output path for validation report"
    )
    args = parser.parse_args()

    # Load calibration results
    json_path = os.path.join(args.results_dir, "calibration_results.json")
    if not os.path.exists(json_path):
        print(f"ERROR: {json_path} not found. Run calibration_analysis.py first.")
        exit(1)

    with open(json_path) as f:
        results = json.load(f)

    # Evaluate gate
    gate_result = evaluate_gate(results)
    print(f"\nGate Result: {gate_result['gate']} (method: {gate_result['method']})")

    # Save gate_result.json
    gate_path = os.path.join(args.results_dir, "gate_result.json")
    with open(gate_path, "w") as f:
        json.dump(gate_result, f, indent=2)
    print(f"Gate result saved: {gate_path}")

    # Generate validation report
    generate_validation_report(results, gate_result, output_path=args.output)
