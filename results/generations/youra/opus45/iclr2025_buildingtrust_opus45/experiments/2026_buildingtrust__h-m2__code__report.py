"""
Reporting module for H-M2 Percentile-Normalized Monotonicity Attenuation.
Generates YAML results and markdown validation report.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import RESULTS_YAML, VALIDATION_MD, GATE_TYPE


def evaluate_gate(family_results: dict[str, dict]) -> str:
    """
    Evaluate overall gate result based on per-family results.

    Gate passes if ALL families have gate_pass=True.
    (β_instruct < β_base AND p < 0.05 for each family)

    Args:
        family_results: Dict mapping family name to analysis results

    Returns:
        "PASS" if all families have gate_pass=True, else "FAIL"
    """
    if not family_results:
        return "FAIL"

    all_pass = all(r["gate_pass"] for r in family_results.values())
    return "PASS" if all_pass else "FAIL"


def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None:
    """
    Write experiment_results.yaml with β values, CIs, p-values, effect sizes, gate.

    Args:
        family_results: Dict mapping family name to analysis results
        gate_result: "PASS" or "FAIL"
        output_path: Path to output file
    """
    if output_path is None:
        output_path = RESULTS_YAML

    # Build results structure
    results = {
        "hypothesis_id": "h-m2",
        "hypothesis_type": "MECHANISM",
        "statement": "Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2x2 prompt controls.",
        "generated_at": datetime.now().isoformat(),
        "gate": {
            "type": GATE_TYPE,
            "result": gate_result,
            "criteria": {
                "direction": "β_instruct < β_base",
                "significance": "p < 0.05",
                "requirement": "All families must pass",
            },
        },
        "families": {},
    }

    # Add per-family results (without numpy arrays)
    for family, r in family_results.items():
        results["families"][family] = {
            "base_beta": round(r["base_beta"], 4),
            "base_ci": {
                "mean": round(r["base_ci"][0], 4),
                "lower": round(r["base_ci"][1], 4),
                "upper": round(r["base_ci"][2], 4),
            },
            "inst_beta": round(r["inst_beta"], 4),
            "inst_ci": {
                "mean": round(r["inst_ci"][0], 4),
                "lower": round(r["inst_ci"][1], 4),
                "upper": round(r["inst_ci"][2], 4),
            },
            "delta_beta": round(r["delta_beta"], 4),
            "delta_ci": {
                "lower": round(r["delta_ci_lower"], 4),
                "upper": round(r["delta_ci_upper"], 4),
            },
            "p_value": round(r["p_value"], 4),
            "effect_size": round(r["effect_size"], 4),
            "direction_correct": r["direction_correct"],
            "statistically_significant": r["statistically_significant"],
            "gate_pass": r["gate_pass"],
            "n_samples": r["n_samples"],
        }

    # Write YAML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None:
    """
    Write 04_validation.md: markdown summary table + gate pass/fail section.

    Args:
        family_results: Dict mapping family name to analysis results
        gate_result: "PASS" or "FAIL"
        output_path: Path to output file
    """
    if output_path is None:
        output_path = VALIDATION_MD

    lines = []
    lines.append("# Validation Report: H-M2")
    lines.append("")
    lines.append("**Hypothesis:** Percentile-Normalized Monotonicity Attenuation")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Gate Type:** {GATE_TYPE}")
    lines.append(f"**Gate Result:** **{gate_result}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("This experiment tests whether RLHF instruction tuning attenuates the monotonic relationship between confidence (margin) and correctness.")
    lines.append("")
    lines.append("**Hypothesis Statement:** Margin inflation decouples confidence-correctness relationship, measurable via attenuated percentile-normalized slope (β_percentile_instruct < β_percentile_base) under 2x2 prompt controls.")
    lines.append("")
    lines.append("**Gate Criteria:**")
    lines.append("1. β_instruct < β_base (direction check)")
    lines.append("2. p < 0.05 (statistical significance via paired bootstrap)")
    lines.append("3. All families must pass")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Results by Family")
    lines.append("")

    # Summary table
    lines.append("| Family | β_base | β_instruct | Δβ | p-value | Effect Size | Gate |")
    lines.append("|--------|--------|------------|-----|---------|-------------|------|")

    for family, r in family_results.items():
        gate_emoji = "✅" if r["gate_pass"] else "❌"
        lines.append(
            f"| {family.capitalize()} | "
            f"{r['base_beta']:.4f} | "
            f"{r['inst_beta']:.4f} | "
            f"{r['delta_beta']:.4f} | "
            f"{r['p_value']:.4f} | "
            f"{r['effect_size']:.4f} | "
            f"{gate_emoji} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Results")
    lines.append("")

    for family, r in family_results.items():
        lines.append(f"### {family.capitalize()}")
        lines.append("")
        lines.append(f"**Sample Size:** {r['n_samples']}")
        lines.append("")
        lines.append("**β_percentile (with 95% CI):**")
        lines.append(f"- Base: {r['base_beta']:.4f} [{r['base_ci'][1]:.4f}, {r['base_ci'][2]:.4f}]")
        lines.append(f"- Instruct: {r['inst_beta']:.4f} [{r['inst_ci'][1]:.4f}, {r['inst_ci'][2]:.4f}]")
        lines.append("")
        lines.append("**Difference Test (paired bootstrap):**")
        lines.append(f"- Δβ = β_base - β_instruct: {r['delta_beta']:.4f} [{r['delta_ci_lower']:.4f}, {r['delta_ci_upper']:.4f}]")
        lines.append(f"- p-value: {r['p_value']:.4f}")
        lines.append(f"- Effect size (Δβ / σ): {r['effect_size']:.4f}")
        lines.append("")
        lines.append("**Gate Check:**")
        lines.append(f"- Direction (β_inst < β_base): {'✅ Yes' if r['direction_correct'] else '❌ No'}")
        lines.append(f"- Significance (p < 0.05): {'✅ Yes' if r['statistically_significant'] else '❌ No'}")
        lines.append(f"- **Gate Pass:** {'✅ PASS' if r['gate_pass'] else '❌ FAIL'}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Gate Verdict")
    lines.append("")

    if gate_result == "PASS":
        lines.append("### ✅ GATE PASSED")
        lines.append("")
        lines.append("All model families show statistically significant monotonicity attenuation:")
        lines.append("- β_instruct < β_base (the instruct models have weaker confidence-correctness relationship)")
        lines.append("- p < 0.05 (the difference is statistically significant)")
        lines.append("")
        lines.append("**Interpretation:** RLHF instruction tuning degrades the discriminative quality of confidence signals by inflating margins for incorrect predictions, which weakens the monotonic relationship between margin and correctness probability.")
    else:
        lines.append("### ❌ GATE FAILED")
        lines.append("")
        lines.append("Not all model families show the expected monotonicity attenuation pattern.")
        lines.append("")
        failing_families = [f for f, r in family_results.items() if not r["gate_pass"]]
        lines.append(f"**Failing Families:** {', '.join(failing_families)}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Figures")
    lines.append("")
    lines.append("- `figures/gate_metrics_beta_percentile.png`: β comparison bar chart")
    lines.append("- `figures/bootstrap_distributions.png`: Bootstrap β distributions")
    lines.append("- `figures/logistic_curves.png`: Pr(correct) vs z(margin) curves")
    lines.append("- `figures/forest_plot.png`: Effect size forest plot")
    lines.append("")

    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
