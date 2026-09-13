"""report_generator.py — A-5: Serialize results to JSON and generate gate verdict."""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


GATE_THRESHOLD_R = 0.5
GATE_THRESHOLD_P = 0.05
EXPLORE_THRESHOLD_R = 0.3


def determine_gate_result(pearson_r: float, pearson_p: float) -> dict:
    """Determine SHOULD_WORK gate result for H-M3."""
    if pearson_r >= GATE_THRESHOLD_R and pearson_p < GATE_THRESHOLD_P:
        return {
            "result": "PASS",
            "satisfied": True,
            "reasoning": f"Pearson r={pearson_r:.3f} >= 0.5 and p={pearson_p:.4f} < 0.05",
        }
    elif pearson_r >= EXPLORE_THRESHOLD_R and pearson_p < GATE_THRESHOLD_P:
        return {
            "result": "PARTIAL",
            "satisfied": False,
            "reasoning": (f"Pearson r={pearson_r:.3f} in [0.3,0.5) with p={pearson_p:.4f} < 0.05; "
                          "partial support — EXPLORE mode triggered"),
        }
    else:
        return {
            "result": "FAIL",
            "satisfied": False,
            "reasoning": (f"Pearson r={pearson_r:.3f} < 0.3 or p={pearson_p:.4f} >= 0.05; "
                          "no significant contamination-accuracy correlation"),
        }


def save_experiment_results(
    results: dict,
    output_path: str,
) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {output_path}")


def generate_markdown_report(
    results: dict,
    report_path: str,
) -> None:
    """Write the 04_validation.md report."""
    gate = results["gate"]
    primary = results["primary_correlation"]
    ablations = results.get("ablations", {})
    dir_check = results.get("directional_check", {})

    r = primary["pearson_r"]
    p = primary["pearson_p"]
    rho = primary["spearman_rho"]
    rho_p = primary["spearman_p"]
    ci = primary.get("bootstrap_ci_95", [None, None])
    n = primary["n_observations"]

    gate_emoji = "✅" if gate["result"] == "PASS" else ("⚠️" if gate["result"] == "PARTIAL" else "❌")

    lines = [
        "# Phase 4 Validation Report: H-M3",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Hypothesis:** H-M3 — Contamination-Accuracy Correlation",
        f"**Gate Type:** SHOULD_WORK",
        "",
        "---",
        "",
        "## Gate Evaluation",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| **Gate Type** | SHOULD_WORK |",
        f"| **Gate Result** | {gate_emoji} {gate['result']} |",
        f"| **Gate Satisfied** | {gate['satisfied']} |",
        f"| **Reasoning** | {gate['reasoning']} |",
        "",
        "---",
        "",
        "## Primary Correlation Results",
        "",
        f"| Metric | Value | Threshold | Status |",
        f"|--------|-------|-----------|--------|",
        f"| Pearson r | {r:.4f} | ≥ 0.5 | {'✅ PASS' if r >= 0.5 else ('⚠️ PARTIAL' if r >= 0.3 else '❌ FAIL')} |",
        f"| Pearson p | {p:.4f} | < 0.05 | {'✅ PASS' if p < 0.05 else '❌ FAIL'} |",
        f"| Spearman ρ | {rho:.4f} | ≥ 0.5 | {'✅ PASS' if rho >= 0.5 else '❌ FAIL'} |",
        f"| Spearman p | {rho_p:.4f} | < 0.05 | {'✅ PASS' if rho_p < 0.05 else '❌ FAIL'} |",
        f"| N observations | {n} | 16 | {'✅' if n == 16 else '⚠️'} |",
    ]

    if ci and ci[0] is not None:
        lines.append(f"| Bootstrap 95% CI | [{ci[0]:.4f}, {ci[1]:.4f}] | CI > 0 | {'✅' if ci[0] > 0 else '⚠️'} |")

    dir_n = dir_check.get("n_correct_direction")
    if dir_n is not None:
        lines += [
            "",
            "### Directional Check",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Fraction concordant pairs | {dir_n:.3f} (of 6 benchmark pairs) |",
        ]
        signs = dir_check.get("benchmark_signs", {})
        for b, v in signs.items():
            lines.append(f"| {b} mean diff | {v:+.4f} |")

    lines += [
        "",
        "---",
        "",
        "## Ablation Studies",
        "",
    ]

    # Estimator comparison
    est = ablations.get("estimator_comparison", {})
    if est:
        lines += [
            "### Ablation 1: Estimator Comparison (13-gram vs min-k%)",
            "",
            f"| Estimator | Pearson r | p-value |",
            f"|-----------|-----------|---------|",
            f"| 13-gram overlap (H-M1) | {est['13gram']['pearson_r']:.4f} | {est['13gram']['pearson_p']:.4f} |",
        ]
        if est.get("mink"):
            lines.append(
                f"| min-k% differential (H-M2) | {est['mink']['pearson_r']:.4f} | {est['mink']['pearson_p']:.4f} |"
            )
        else:
            lines.append("| min-k% differential (H-M2) | N/A — H-M2 results unavailable | — |")
        lines.append("")

    # Aggregation strategy
    agg = ablations.get("aggregation_strategy", {})
    if agg:
        lines += [
            "### Ablation 2: Aggregation Strategy",
            "",
            f"| Strategy | N | Pearson r | p-value |",
            f"|----------|---|-----------|---------|",
            f"| Flattened (n=16, primary) | 16 | {agg['n16']['pearson_r']:.4f} | {agg['n16']['pearson_p']:.4f} |",
            f"| Benchmark mean (n=4) | 4 | {agg['n4']['pearson_r']:.4f} | {agg['n4']['pearson_p']:.4f} |",
            "",
        ]

    # Token vs step
    tvs = ablations.get("token_vs_step", {})
    if tvs:
        lines += [
            "### Ablation 3: Token-count vs Step-count Matching",
            "",
            f"| Matching | Pearson r | p-value |",
            f"|----------|-----------|---------|",
            f"| Token-count (primary) | {tvs['token']['pearson_r']:.4f} | {tvs['token']['pearson_p']:.4f} |",
        ]
        if tvs.get("step"):
            lines.append(
                f"| Step-count | {tvs['step']['pearson_r']:.4f} | {tvs['step']['pearson_p']:.4f} |"
            )
        else:
            lines.append("| Step-count | N/A | — |")
        lines.append("")

    # Per model size
    pms = ablations.get("per_model_size", {})
    if pms:
        lines += [
            "### Ablation 4: Per-Model-Size Correlation (n=4 per size)",
            "",
            f"| Model Size | Pearson r | p-value |",
            f"|------------|-----------|---------|",
        ]
        for size, res in pms.items():
            lines.append(f"| {size} | {res['pearson_r']:.4f} | {res['pearson_p']:.4f} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Figures",
        "",
        "| Figure | Description |",
        "|--------|-------------|",
        "| fig_scatter_contamination_vs_differential.png | Primary: contamination vs differential scatter |",
        "| fig_correlation_heatmap.png | Pearson r by estimator × model size |",
        "| fig_per_benchmark_bars.png | Per-benchmark differential by model size |",
        "| fig_bootstrap_ci.png | Bootstrap CI distribution |",
        "| fig_spearman_ranks.png | Spearman rank visualization |",
        "",
        "---",
        "",
        "## Contamination Estimates Used",
        "",
        "| Benchmark | 13-gram Overlap Rate | Source |",
        "|-----------|---------------------|--------|",
    ]

    cont_used = results.get("contamination_estimates", {})
    cont_source = results.get("contamination_source", "unknown")
    for b in ["mmlu", "hellaswag", "arc_challenge", "winogrande"]:
        v = cont_used.get(b, "N/A")
        lines.append(f"| {b} | {v:.4f} | {cont_source} |")

    lines += [
        "",
        "---",
        "",
        "## Conclusion",
        "",
    ]

    if gate["result"] == "PASS":
        lines += [
            f"H-M3 **PASS**: Pearson r={r:.3f} (p={p:.4f}) confirms contamination-accuracy correlation.",
            "Higher 13-gram overlap benchmarks show predicted accuracy differential direction.",
            "Hypothesis supported: deduplication removes contaminated documents, reducing Pile models' advantage.",
        ]
    elif gate["result"] == "PARTIAL":
        lines += [
            f"H-M3 **PARTIAL**: Pearson r={r:.3f} (p={p:.4f}) shows moderate correlation.",
            "Correlation exists but below r≥0.5 threshold. EXPLORE mode: investigate volume confound.",
        ]
    else:
        lines += [
            f"H-M3 **FAIL**: Pearson r={r:.3f} (p={p:.4f}). No significant contamination-accuracy correlation.",
            "SHOULD_WORK gate: failure does not block H-M4. Limitation recorded.",
        ]

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Report saved: {report_path}")
