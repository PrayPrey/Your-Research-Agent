"""
Reporting module for H-M1 Conditional Margin Inflation Analysis.
Generates YAML results and markdown validation report.
"""

import yaml
from pathlib import Path
from datetime import datetime

from config import HYPOTHESIS_DIR, GATE_TYPE


def evaluate_gate(family_results: dict[str, dict]) -> str:
    """
    Evaluate overall gate result based on per-family results.

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
    output_path: Path = None,
) -> None:
    """
    Write experiment_results.yaml conforming to PRD schema.

    Args:
        family_results: Dict mapping family name to analysis results
        gate_result: "PASS" or "FAIL"
        output_path: Path to output file
    """
    if output_path is None:
        output_path = HYPOTHESIS_DIR / "experiment_results.yaml"

    # Build results structure
    results = {
        "hypothesis_id": "h-m1",
        "hypothesis_type": "MECHANISM",
        "statement": "RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions, measurable as E[margin|incorrect]_instruct > E[margin|incorrect]_base.",
        "gate": {
            "type": GATE_TYPE,
            "result": gate_result,
            "timestamp": datetime.now().isoformat(),
        },
        "families_analyzed": list(family_results.keys()),
        "per_family_results": {},
    }

    for family, r in family_results.items():
        results["per_family_results"][family] = {
            "n_samples": r["n_samples"],
            "base": {
                "mean_correct": round(r["base_stats"]["mean_correct"], 6),
                "mean_incorrect": round(r["base_stats"]["mean_incorrect"], 6),
                "se_incorrect": round(r["base_stats"]["se_incorrect"], 6),
                "n_correct": r["base_stats"]["n_correct"],
                "n_incorrect": r["base_stats"]["n_incorrect"],
            },
            "instruct": {
                "mean_correct": round(r["inst_stats"]["mean_correct"], 6),
                "mean_incorrect": round(r["inst_stats"]["mean_incorrect"], 6),
                "se_incorrect": round(r["inst_stats"]["se_incorrect"], 6),
                "n_correct": r["inst_stats"]["n_correct"],
                "n_incorrect": r["inst_stats"]["n_incorrect"],
            },
            "statistical_test": {
                "method": "scipy.stats.permutation_test",
                "permutation_type": "independent",
                "alternative": "greater",
                "n_resamples": 9999,
                "p_value": round(r["permutation_test"]["p_value"], 6),
                "statistic": round(r["permutation_test"]["statistic"], 6),
            },
            "effect_size": {
                "raw_diff": round(r["effect_size"]["raw_diff"], 6),
                "inflation_ratio": round(r["effect_size"]["inflation_ratio"], 4),
                "cohens_d": round(r["effect_size"]["cohens_d"], 4),
            },
            "bootstrap_ci_95": {
                "lower": round(r["bootstrap_ci"]["ci_lower"], 6),
                "upper": round(r["bootstrap_ci"]["ci_upper"], 6),
            },
            "kl_divergence": round(r["kl_divergence"], 6),
            "kl_divergence_incorrect": round(r["kl_divergence_incorrect"], 6),
            "direction_correct": r["direction_correct"],
            "statistically_significant": r["statistically_significant"],
            "gate_pass": r["gate_pass"],
        }

    # Summary
    results["summary"] = {
        "all_families_pass": gate_result == "PASS",
        "families_passed": sum(1 for r in family_results.values() if r["gate_pass"]),
        "families_total": len(family_results),
        "mean_inflation_ratio": round(
            sum(r["effect_size"]["inflation_ratio"] for r in family_results.values()) / len(family_results),
            4
        ),
        "mean_p_value": round(
            sum(r["permutation_test"]["p_value"] for r in family_results.values()) / len(family_results),
            6
        ),
    }

    with open(output_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Path = None,
) -> None:
    """
    Write 04_validation.md markdown report.

    Args:
        family_results: Dict mapping family name to analysis results
        gate_result: "PASS" or "FAIL"
        output_path: Path to output file
    """
    if output_path is None:
        output_path = HYPOTHESIS_DIR / "04_validation.md"

    lines = [
        "# H-M1 Validation Report",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Hypothesis:** H-M1 (MECHANISM)",
        f"**Gate Type:** {GATE_TYPE}",
        f"**Gate Result:** {gate_result}",
        "",
        "---",
        "",
        "## Hypothesis Statement",
        "",
        "> RLHF instruction tuning inflates logit margins uniformly including for incorrect predictions,",
        "> measurable as E[margin|incorrect]_instruct > E[margin|incorrect]_base.",
        "",
        "---",
        "",
        "## Results Summary",
        "",
    ]

    # Per-family results table
    lines.append("| Family | Base E[m|inc] | Inst E[m|inc] | p-value | Inflation Ratio | Pass |")
    lines.append("|--------|---------------|---------------|---------|-----------------|------|")

    for family, r in family_results.items():
        base_mean = r["base_stats"]["mean_incorrect"]
        inst_mean = r["inst_stats"]["mean_incorrect"]
        p_value = r["permutation_test"]["p_value"]
        ratio = r["effect_size"]["inflation_ratio"]
        passed = "PASS" if r["gate_pass"] else "FAIL"

        lines.append(f"| {family.capitalize()} | {base_mean:.4f} | {inst_mean:.4f} | {p_value:.4f} | {ratio:.2f}x | {passed} |")

    lines.extend([
        "",
        "---",
        "",
        "## Detailed Results",
        "",
    ])

    for family, r in family_results.items():
        lines.extend([
            f"### {family.capitalize()}",
            "",
            f"**Sample Size:** {r['n_samples']:,}",
            "",
            "**Conditional Margin Statistics:**",
            f"- Base: E[m|correct]={r['base_stats']['mean_correct']:.4f}, E[m|incorrect]={r['base_stats']['mean_incorrect']:.4f}",
            f"- Instruct: E[m|correct]={r['inst_stats']['mean_correct']:.4f}, E[m|incorrect]={r['inst_stats']['mean_incorrect']:.4f}",
            "",
            "**Statistical Test (Permutation):**",
            f"- Statistic (diff): {r['permutation_test']['statistic']:.4f}",
            f"- p-value: {r['permutation_test']['p_value']:.6f}",
            f"- Significant (p < 0.05): {'Yes' if r['statistically_significant'] else 'No'}",
            "",
            "**Effect Size:**",
            f"- Raw difference: {r['effect_size']['raw_diff']:.4f}",
            f"- Inflation ratio: {r['effect_size']['inflation_ratio']:.2f}x",
            f"- Cohen's d: {r['effect_size']['cohens_d']:.3f}",
            "",
            "**Bootstrap 95% CI:**",
            f"- [{r['bootstrap_ci']['ci_lower']:.4f}, {r['bootstrap_ci']['ci_upper']:.4f}]",
            "",
            f"**Gate Pass:** {'PASS' if r['gate_pass'] else 'FAIL'}",
            "",
        ])

    # Gate evaluation
    lines.extend([
        "---",
        "",
        "## Gate Evaluation",
        "",
        f"**Gate Type:** {GATE_TYPE}",
        f"**Overall Result:** {gate_result}",
        "",
        "**Pass Conditions:**",
        "1. E[margin|incorrect]_instruct > E[margin|incorrect]_base (direction)",
        "2. p-value < 0.05 (statistical significance)",
        "",
        "**Families Passing:** " + ", ".join(
            f.capitalize() for f, r in family_results.items() if r["gate_pass"]
        ),
        "",
    ])

    if gate_result == "PASS":
        lines.extend([
            "**Conclusion:** The hypothesis is supported. Instruction tuning inflates margins for incorrect predictions,",
            "which explains why AUROC degrades (margins become less discriminative between correct and incorrect predictions).",
        ])
    else:
        lines.extend([
            "**Conclusion:** The hypothesis is not fully supported.",
            "Not all families show statistically significant margin inflation for incorrect predictions.",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Figures",
        "",
        "- `figures/gate_metrics.png`: E[margin|incorrect] comparison bar chart",
        "- `figures/kde_distributions.png`: Margin distribution KDE plots",
        "- `figures/box_plots.png`: Box plots by condition",
        "- `figures/inflation_ratios.png`: Inflation ratio comparison",
        "- `figures/forest_plot.png`: Effect size forest plot with CIs",
        "",
        "---",
        "",
        "*Generated by H-M1 Conditional Margin Inflation Analysis*",
    ])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
