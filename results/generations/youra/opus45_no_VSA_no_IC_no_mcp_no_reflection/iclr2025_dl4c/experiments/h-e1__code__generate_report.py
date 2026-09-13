#!/usr/bin/env python
"""Generate 04_validation.md report from experiment results."""
import os
import json
import numpy as np
from datetime import datetime
from scipy import stats


def load_results(path="outputs/results.json"):
    with open(path) as f:
        results = json.load(f)
    # Convert string keys to int for seeds
    for cond in results:
        results[cond] = {int(k): v for k, v in results[cond].items()}
    return results


def samples_to_threshold(metric_log, threshold=0.3):
    for n_samples, p1 in metric_log:
        if p1 >= threshold:
            return n_samples
    return None


def compute_statistics(results):
    conditions = ["binary", "categorical", "high_bandwidth"]
    seeds = list(results.get("binary", {}).keys())

    stats_summary = {}

    for cond in conditions:
        if cond not in results:
            continue

        final_p1s = [results[cond][s]["final_pass_at_1"] for s in seeds if s in results[cond]]
        thresholds = []

        for s in seeds:
            if s in results[cond]:
                t = samples_to_threshold(results[cond][s].get("metric_log", []))
                if t is not None:
                    thresholds.append(t)

        stats_summary[cond] = {
            "final_pass_at_1_mean": np.mean(final_p1s) if final_p1s else 0.0,
            "final_pass_at_1_std": np.std(final_p1s) if final_p1s else 0.0,
            "samples_to_threshold_mean": np.mean(thresholds) if thresholds else None,
            "samples_to_threshold_std": np.std(thresholds) if thresholds else None,
            "n_reached_threshold": len(thresholds),
            "n_seeds": len(final_p1s)
        }

    return stats_summary


def compute_gate(results, stats_summary):
    binary_p1 = stats_summary.get("binary", {}).get("final_pass_at_1_mean", 0)
    hb_p1 = stats_summary.get("high_bandwidth", {}).get("final_pass_at_1_mean", 0)

    binary_stt = stats_summary.get("binary", {}).get("samples_to_threshold_mean")
    hb_stt = stats_summary.get("high_bandwidth", {}).get("samples_to_threshold_mean")

    # Statistical test
    seeds = list(results.get("binary", {}).keys())
    binary_vals = [results["binary"][s]["final_pass_at_1"] for s in seeds if s in results.get("binary", {})]
    hb_vals = [results["high_bandwidth"][s]["final_pass_at_1"] for s in seeds if s in results.get("high_bandwidth", {})]

    if len(binary_vals) >= 2 and len(hb_vals) >= 2:
        t_stat, p_value = stats.ttest_ind(hb_vals, binary_vals)
        cohens_d = (np.mean(hb_vals) - np.mean(binary_vals)) / np.sqrt((np.var(hb_vals) + np.var(binary_vals)) / 2)
    else:
        t_stat, p_value, cohens_d = None, None, None

    # Gate criteria
    gate_passed = False
    gate_reason = ""

    if hb_stt is not None and binary_stt is not None:
        gate_passed = hb_stt < binary_stt
        gate_reason = f"samples_to_threshold: high_bandwidth={hb_stt:.0f} < binary={binary_stt:.0f}"
    elif hb_p1 > binary_p1:
        gate_passed = True
        gate_reason = f"pass@1: high_bandwidth={hb_p1:.4f} > binary={binary_p1:.4f}"
    else:
        gate_reason = f"pass@1: high_bandwidth={hb_p1:.4f} <= binary={binary_p1:.4f}"

    return {
        "passed": gate_passed,
        "reason": gate_reason,
        "statistical_test": {
            "t_statistic": t_stat,
            "p_value": p_value,
            "cohens_d": cohens_d,
            "significant": p_value < 0.05 if p_value else False
        }
    }


def generate_report(results, stats_summary, gate, output_path):
    report = f"""# Phase 4 Validation Report: H-E1

**Hypothesis:** Higher bandwidth reward signals accelerate PPO convergence vs binary rewards
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Status:** {"PASSED" if gate["passed"] else "FAILED"}

---

## Executive Summary

This experiment tested whether multi-signal reward functions (categorical error types + continuous test pass ratios)
accelerate training convergence compared to binary pass/fail rewards for code generation tasks.

**Gate Result:** {"✅ PASSED" if gate["passed"] else "❌ FAILED"}
**Reason:** {gate["reason"]}

---

## Results Summary

| Condition | pass@1 (mean ± std) | Samples to Threshold | Seeds Reaching Threshold |
|-----------|---------------------|---------------------|--------------------------|
"""

    for cond in ["binary", "categorical", "high_bandwidth"]:
        s = stats_summary.get(cond, {})
        p1_str = f"{s.get('final_pass_at_1_mean', 0):.4f} ± {s.get('final_pass_at_1_std', 0):.4f}"
        stt = s.get('samples_to_threshold_mean')
        stt_str = f"{stt:.0f} ± {s.get('samples_to_threshold_std', 0):.0f}" if stt else "Not reached"
        n_reached = s.get('n_reached_threshold', 0)
        n_seeds = s.get('n_seeds', 0)
        report += f"| {cond} | {p1_str} | {stt_str} | {n_reached}/{n_seeds} |\n"

    report += f"""
---

## Statistical Analysis

- **Test:** Independent t-test (high_bandwidth vs binary)
- **t-statistic:** {f'{gate["statistical_test"]["t_statistic"]:.4f}' if gate["statistical_test"]["t_statistic"] else "N/A"}
- **p-value:** {f'{gate["statistical_test"]["p_value"]:.4f}' if gate["statistical_test"]["p_value"] else "N/A"}
- **Cohen's d:** {f'{gate["statistical_test"]["cohens_d"]:.4f}' if gate["statistical_test"]["cohens_d"] else "N/A"}
- **Significant (p < 0.05):** {gate["statistical_test"]["significant"]}

---

## Gate Evaluation

**Gate Type:** MUST_WORK (EXISTENCE hypothesis)
**Criteria:** High-bandwidth condition reaches pass@1 > 0.3 in fewer training samples than binary condition,
OR high_bandwidth achieves higher final pass@1 than binary.

**Result:** {"✅ GATE SATISFIED" if gate["passed"] else "❌ GATE NOT SATISFIED"}

{gate["reason"]}

---

## Experimental Setup

- **Model:** CodeLlama-7B-Instruct
- **Dataset:** MBPP (sanitized) train split
- **Evaluation:** MBPP validation subset (50 samples)
- **Reward Conditions:**
  - Binary: 1.0 if all tests pass, 0.0 otherwise
  - Categorical: Score based on error type (passed=1.0, assertion=0.5, runtime=0.25, syntax=0.0)
  - High-bandwidth: 0.5*categorical + 0.3*pass_ratio + 0.2*partial_credit
- **Training:** Policy gradient (REINFORCE) with advantage baseline
- **Seeds:** {len(list(results.get("binary", {}).keys()))}
- **Epochs:** 1 (PoC validation)

---

## Artifacts

- `outputs/results.json`: Raw experiment data
- `outputs/figures/`: Visualization plots (if generated)

---

## Conclusion

{"The hypothesis is **supported**: higher bandwidth reward signals do show improved performance over binary signals, validating the core mechanism for further investigation in Phase 5." if gate["passed"] else "The hypothesis requires **revision**: high-bandwidth rewards did not outperform binary rewards in this PoC experiment. Consider adjusting the reward weighting scheme or investigating other reward formulations."}

---

*Generated by Phase 4 validation pipeline*
"""

    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report saved to: {output_path}")
    return gate["passed"]


def main():
    results = load_results()
    stats_summary = compute_statistics(results)
    gate = compute_gate(results, stats_summary)

    output_path = "../04_validation.md"
    passed = generate_report(results, stats_summary, gate, output_path)

    # Also save structured evaluation
    evaluation = {
        "summary": stats_summary,
        "gate": gate,
        "timestamp": datetime.now().isoformat()
    }

    with open("outputs/evaluation.json", "w") as f:
        json.dump(evaluation, f, indent=2, default=str)

    print(f"\nGate Result: {'PASSED' if passed else 'FAILED'}")
    return passed


if __name__ == "__main__":
    main()
