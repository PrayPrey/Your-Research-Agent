"""
gate_and_report.py — H-M2 Pre-Softmax Logit Margin Inflation
Gate evaluation (SHOULD_WORK) and validation report generation.
"""
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Required sections for validation report
REQUIRED_SECTIONS = [
    "gate_result",
    "delta_margin_table",
    "bootstrap_ci_ppo",
    "gradient_ordering_stats",
    "execution_path",
    "key_findings",
    "figure_paths",
]


def evaluate_should_work_gate(
    delta_results: dict,
) -> tuple:
    """SHOULD_WORK gate: >= 2/3 PPO sizes with delta_mean > 0 AND ci_lower > 0.

    Args:
        delta_results: {"{alignment}_{size}": (delta_mean, ci_lower, ci_upper)}

    Returns:
        (gate_result: "PASS"|"FAIL", failed_checks: list[str], exploration_notes: dict)
        exploration_notes is {} on PASS; contains {action, hypothesis, next_step} on FAIL.
    """
    failed_checks = []
    sizes = ["1.4b", "2.8b", "6.9b"]
    min_passing = 2  # >= 2/3 PPO sizes

    ppo_pass_count = 0
    for size in sizes:
        key = f"ppo_{size}"
        if key not in delta_results:
            failed_checks.append(f"Missing result for {key}")
            continue

        delta_mean, ci_lower, ci_upper = delta_results[key]

        if delta_mean > 0 and ci_lower > 0:
            ppo_pass_count += 1
            logger.info("  PPO %s: PASS (Δ=%.4f, CI_lower=%.4f)", size, delta_mean, ci_lower)
        else:
            failed_checks.append(
                f"ppo_{size}: delta_mean={delta_mean:.4f} or ci_lower={ci_lower:.4f} not > 0"
            )
            logger.info(
                "  PPO %s: FAIL (Δ=%.4f, CI_lower=%.4f)", size, delta_mean, ci_lower
            )

    gate_result = "PASS" if ppo_pass_count >= min_passing else "FAIL"
    logger.info(
        "SHOULD_WORK gate: %d/%d PPO sizes pass → %s",
        ppo_pass_count, len(sizes), gate_result
    )

    exploration_notes = {}
    if gate_result == "FAIL":
        exploration_notes = {
            "action": "EXPLORE",
            "hypothesis": (
                "Logit margin inflation may not be the primary mechanism "
                "for alignment-induced overconfidence."
            ),
            "next_step": (
                "Proceed to H-M3 to investigate alternative mechanisms "
                "(boundary restructuring vs. pure scale inflation)."
            ),
            "ppo_sizes_passing": ppo_pass_count,
            "ppo_sizes_required": min_passing,
        }

    return gate_result, failed_checks, exploration_notes


def generate_validation_report(
    delta_results: dict,
    ordering_stats: dict,
    gate_result: str,
    failed_checks: list,
    exploration_notes: dict,
    execution_path: str,
    figure_paths: list,
    mechanism_indicators: dict,
    output_path: str,
) -> str:
    """Write h-m2/04_validation.md with all required sections.

    Returns:
        output_path
    """
    sizes = ["1.4b", "2.8b", "6.9b"]
    alignments = ["sft", "dpo", "ppo"]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = datetime.now().strftime("%Y-%m-%d")

    lines = []

    # ── Header ─────────────────────────────────────────────────────────────────
    lines.append("# H-M2 Validation Report: Pre-Softmax Logit Margin Inflation")
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Hypothesis ID | h-m2 |")
    lines.append(f"| Type | MECHANISM |")
    lines.append(f"| Date | {date_str} |")
    lines.append(f"| Gate Type | SHOULD_WORK |")
    lines.append(f"| Execution Path | {execution_path} |")
    lines.append(f"| Completed At | {now_str} |")
    lines.append("")

    # ── gate_result ────────────────────────────────────────────────────────────
    lines.append("## Gate Result")
    lines.append("")
    icon = "✅" if gate_result == "PASS" else "❌"
    lines.append(f"**{icon} SHOULD_WORK Gate: {gate_result}**")
    lines.append("")

    if failed_checks:
        lines.append("### Failed Checks")
        lines.append("")
        for check in failed_checks:
            lines.append(f"- {check}")
        lines.append("")

    # ── delta_margin_table ─────────────────────────────────────────────────────
    lines.append("## Delta Margin Table")
    lines.append("")
    lines.append("Mean Δmargin (aligned − base) for all 9 alignment × size pairs (in nats)")
    lines.append("")
    lines.append("| Alignment | 1.4b | 2.8b | 6.9b |")
    lines.append("|-----------|------|------|------|")

    for alignment in alignments:
        row = [alignment.upper()]
        for size in sizes:
            key = f"{alignment}_{size}"
            if key in delta_results:
                delta_mean, ci_lower, ci_upper = delta_results[key]
                row.append(f"{delta_mean:+.4f}")
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ── bootstrap_ci_ppo ──────────────────────────────────────────────────────
    lines.append("## Bootstrap CI (PPO Sizes)")
    lines.append("")
    lines.append("95% bootstrap confidence intervals for PPO Δmargin:")
    lines.append("")
    lines.append("| Size | Δmean | CI Lower | CI Upper | Gate Pass |")
    lines.append("|------|-------|----------|----------|-----------|")

    for size in sizes:
        key = f"ppo_{size}"
        if key in delta_results:
            dm, ci_lo, ci_hi = delta_results[key]
            passes = "✅" if (dm > 0 and ci_lo > 0) else "❌"
            lines.append(f"| {size} | {dm:+.4f} | {ci_lo:+.4f} | {ci_hi:+.4f} | {passes} |")
        else:
            lines.append(f"| {size} | N/A | N/A | N/A | N/A |")
    lines.append("")

    # ── gradient_ordering_stats ────────────────────────────────────────────────
    lines.append("## Gradient Ordering Statistics (Wilcoxon Signed-Rank)")
    lines.append("")
    lines.append("One-sided test (alternative='greater') across 3 Pythia sizes:")
    lines.append("")
    lines.append("| Test | Statistic | p-value |")
    lines.append("|------|-----------|---------|")

    ppo_ge_dpo_stat = ordering_stats.get("ppo_ge_dpo_stat", float("nan"))
    ppo_ge_dpo_p = ordering_stats.get("ppo_ge_dpo_p", float("nan"))
    dpo_gt_sft_stat = ordering_stats.get("dpo_gt_sft_stat", float("nan"))
    dpo_gt_sft_p = ordering_stats.get("dpo_gt_sft_p", float("nan"))

    def fmt(v):
        if v != v:  # NaN check
            return "N/A (ties)"
        return f"{v:.4f}"

    lines.append(f"| PPO ≥ DPO | {fmt(ppo_ge_dpo_stat)} | {fmt(ppo_ge_dpo_p)} |")
    lines.append(f"| DPO > SFT | {fmt(dpo_gt_sft_stat)} | {fmt(dpo_gt_sft_p)} |")
    lines.append("")
    lines.append("*Note: Wilcoxon with n=3 has limited power; results are indicative.*")
    lines.append("")

    # ── execution_path ─────────────────────────────────────────────────────────
    lines.append("## Execution Path")
    lines.append("")
    if execution_path == "Path A":
        lines.append("**Path A** (data reuse): Loaded pre-softmax log-probs from H-E1 cached")
        lines.append("lm-eval JSONL outputs. Zero new GPU-hours required.")
    else:
        lines.append("**Path B** (re-run): Executed lm-eval with `--log_samples --num_fewshot 4`")
        lines.append("for all 12 Pythia models.")
    lines.append("")

    # ── mechanism_indicators ──────────────────────────────────────────────────
    lines.append("## Mechanism Indicators")
    lines.append("")
    lines.append("| Indicator | Value |")
    lines.append("|-----------|-------|")
    for k, v in mechanism_indicators.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")

    # ── exploration_notes (only if FAIL) ──────────────────────────────────────
    if exploration_notes:
        lines.append("## Exploration Notes")
        lines.append("")
        for k, v in exploration_notes.items():
            lines.append(f"**{k}**: {v}")
            lines.append("")

    # ── figure_paths ──────────────────────────────────────────────────────────
    lines.append("## Figure Paths")
    lines.append("")
    for fp in figure_paths:
        lines.append(f"- `{fp}`")
    lines.append("")

    # ── key_findings ──────────────────────────────────────────────────────────
    lines.append("## Key Findings")
    lines.append("")

    # Generate findings from results
    findings = []

    # Finding 1: gate result
    if gate_result == "PASS":
        ppo_passing = sum(
            1 for s in sizes
            if f"ppo_{s}" in delta_results and
               delta_results[f"ppo_{s}"][0] > 0 and
               delta_results[f"ppo_{s}"][1] > 0
        )
        findings.append(
            f"SHOULD_WORK gate **PASS**: {ppo_passing}/3 PPO sizes show "
            f"positive Δmargin with bootstrap CI lower > 0."
        )
    else:
        ppo_passing = sum(
            1 for s in sizes
            if f"ppo_{s}" in delta_results and
               delta_results[f"ppo_{s}"][0] > 0 and
               delta_results[f"ppo_{s}"][1] > 0
        )
        findings.append(
            f"SHOULD_WORK gate **FAIL**: Only {ppo_passing}/3 PPO sizes show "
            f"positive Δmargin with CI lower > 0 (required: 2)."
        )

    # Finding 2: largest margin increase
    if delta_results:
        max_key = max(delta_results, key=lambda k: delta_results[k][0])
        max_dm = delta_results[max_key][0]
        findings.append(
            f"Largest Δmargin: {max_key} (Δ={max_dm:+.4f} nats), "
            f"confirming alignment increases decision confidence for some models."
        )

    # Finding 3: execution path
    findings.append(
        f"Experiment executed via **{execution_path}**: "
        f"{'reused H-E1 lm-eval JSONL outputs (0 new GPU-hours)' if execution_path == 'Path A' else 're-ran lm_eval for all 12 models'}."
    )

    # Finding 4: gradient ordering (if available)
    if not (ppo_ge_dpo_p != ppo_ge_dpo_p):  # not NaN
        sig_str = "significant" if ppo_ge_dpo_p < 0.05 else "not significant"
        findings.append(
            f"Gradient ordering test PPO≥DPO: p={ppo_ge_dpo_p:.3f} ({sig_str}) "
            f"via Wilcoxon signed-rank (n=3, limited power)."
        )

    for finding in findings:
        lines.append(f"- {finding}")
    lines.append("")

    # ── Write to file ──────────────────────────────────────────────────────────
    content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)

    logger.info("Validation report written to %s (%d lines)", output_path, len(lines))
    return output_path


def write_gate_to_verification_state(
    gate_result: str,
    delta_results: dict,
    gate_report_path: str,
    verification_state_path: str,
) -> None:
    """Update h-m2 section in verification_state.yaml atomically (.tmp rename).

    Sets sub_hypotheses.h-m2 fields:
        gate.satisfied, gate.result, validation.status, validation.result,
        validation.key_metrics, validation.completed_at, completed, completed_at

    key_metrics:
        delta_ppo_1.4b, delta_ppo_2.8b, delta_ppo_6.9b,
        ci_lower_ppo_1.4b, ci_lower_ppo_2.8b, ci_lower_ppo_6.9b,
        execution_path
    """
    now_str = datetime.now(timezone.utc).isoformat()
    sizes = ["1.4b", "2.8b", "6.9b"]

    with open(verification_state_path, "r") as f:
        state = yaml.safe_load(f)

    h_m2 = state.get("sub_hypotheses", {}).get("h-m2", {})

    # Update gate
    gate_section = h_m2.get("gate", {})
    gate_section["satisfied"] = (gate_result == "PASS")
    gate_section["result"] = gate_result
    h_m2["gate"] = gate_section

    # Update validation
    val = h_m2.get("validation", {})
    val["status"] = "COMPLETED"
    val["result"] = gate_result
    val["report_file"] = gate_report_path
    val["completed_at"] = now_str

    # key_metrics
    key_metrics = {}
    for size in sizes:
        key = f"ppo_{size}"
        if key in delta_results:
            dm, ci_lo, ci_hi = delta_results[key]
            key_metrics[f"delta_ppo_{size}"] = round(float(dm), 6)
            key_metrics[f"ci_lower_ppo_{size}"] = round(float(ci_lo), 6)

    # All alignment means for reference
    for alignment in ["sft", "dpo", "ppo"]:
        for size in sizes:
            k = f"{alignment}_{size}"
            if k in delta_results:
                dm = delta_results[k][0]
                key_metrics[f"delta_{alignment}_{size}"] = round(float(dm), 6)

    val["key_metrics"] = key_metrics
    h_m2["validation"] = val

    # Update top-level status
    if gate_result == "PASS":
        h_m2["status"] = "COMPLETED"
        h_m2["completed"] = True
        h_m2["completed_at"] = now_str
    else:
        h_m2["status"] = "COMPLETED"
        h_m2["completed"] = True
        h_m2["completed_at"] = now_str

    state["sub_hypotheses"]["h-m2"] = h_m2

    # Update statistics
    stats_section = state.get("statistics", {})
    if gate_result == "PASS":
        stats_section["validated_sub_hypotheses"] = (
            stats_section.get("validated_sub_hypotheses", 0) + 1
        )
        stats_section["gates_passed"] = stats_section.get("gates_passed", 0) + 1
    stats_section["in_progress_sub_hypotheses"] = max(
        0, stats_section.get("in_progress_sub_hypotheses", 1) - 1
    )
    state["statistics"] = stats_section

    # Update history
    history = state.get("history", [])
    history.append({
        "event": f"Phase 4 coding completed — SHOULD_WORK {gate_result}",
        "timestamp": now_str,
        "phase": "Phase 4",
        "hypothesis_id": "h-m2",
        "details": (
            f"Phase 4 COMPLETED. Gate {gate_result}. "
            f"Key metrics: {key_metrics}. "
            f"04_validation.md written."
        ),
    })
    state["history"] = history

    # Atomic write via tmp file
    tmp_path = verification_state_path + ".tmp"
    with open(tmp_path, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True)
    os.replace(tmp_path, verification_state_path)
    logger.info("verification_state.yaml updated: h-m2 gate=%s", gate_result)
