"""Report generation for H-M3 Brier decomposition experiment.

Generates YAML results file and markdown validation report.
"""
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import GATE_TYPE, RESULTS_YAML, VALIDATION_MD


def save_experiment_results_yaml(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None:
    """Save structured experiment results to YAML.

    Args:
        family_results: Analysis results from analyze_family
        gate_result: Overall gate result ('PASS' or 'FAIL')
        output_path: Output path (default: RESULTS_YAML from config)
    """
    output_path = output_path or RESULTS_YAML

    results = {
        "experiment": "H-M3: Geometric vs Scalar Distortion",
        "gate_type": GATE_TYPE,
        "gate_result": gate_result,
        "timestamp": datetime.now().isoformat(),
        "families": {},
    }

    for family, data in family_results.items():
        base = data["base"]
        inst = data["instruct"]
        ref_diff = data["refinement_difference"]
        rel_diff = data["reliability_difference"]

        results["families"][family] = {
            "n_samples": int(data["n_samples"]),
            "gate_pass": bool(data["gate_pass"]),
            "base": {
                "brier_score": float(round(base["decomposition"]["brier_score"], 6)),
                "reliability": float(round(base["decomposition"]["reliability"], 6)),
                "resolution": float(round(base["decomposition"]["resolution"], 6)),
                "refinement": float(round(base["decomposition"]["refinement"], 6)),
                "uncertainty": float(round(base["decomposition"]["uncertainty"], 6)),
                "refinement_ci": [
                    float(round(base["confidence_intervals"]["refinement"][1], 6)),
                    float(round(base["confidence_intervals"]["refinement"][2], 6)),
                ],
            },
            "instruct": {
                "brier_score": float(round(inst["decomposition"]["brier_score"], 6)),
                "reliability": float(round(inst["decomposition"]["reliability"], 6)),
                "resolution": float(round(inst["decomposition"]["resolution"], 6)),
                "refinement": float(round(inst["decomposition"]["refinement"], 6)),
                "uncertainty": float(round(inst["decomposition"]["uncertainty"], 6)),
                "refinement_ci": [
                    float(round(inst["confidence_intervals"]["refinement"][1], 6)),
                    float(round(inst["confidence_intervals"]["refinement"][2], 6)),
                ],
            },
            "refinement_difference": {
                "delta_mean": float(round(ref_diff["delta_mean"], 6)),
                "delta_ci": [
                    float(round(ref_diff["delta_ci_lower"], 6)),
                    float(round(ref_diff["delta_ci_upper"], 6)),
                ],
                "p_value": float(round(ref_diff["p_value"], 4)),
                "effect_size": float(round(ref_diff["effect_size"], 4)),
            },
            "reliability_difference": {
                "delta_mean": float(round(rel_diff["delta_mean"], 6)),
                "delta_ci": [
                    float(round(rel_diff["delta_ci_lower"], 6)),
                    float(round(rel_diff["delta_ci_upper"], 6)),
                ],
                "p_value": float(round(rel_diff["p_value"], 4)),
                "effect_size": float(round(rel_diff["effect_size"], 4)),
            },
            "gate_details": {
                "direction_correct": bool(data["gate_details"]["direction_correct"]),
                "ci_excludes_zero": bool(data["gate_details"]["ci_excludes_zero"]),
                "p_significant": bool(data["gate_details"]["p_significant"]),
            },
        }

    with open(output_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_validation_report(
    family_results: dict[str, dict],
    gate_result: str,
    output_path: Optional[Path] = None,
) -> None:
    """Generate markdown validation report.

    Args:
        family_results: Analysis results
        gate_result: Overall gate result
        output_path: Output path (default: VALIDATION_MD from config)
    """
    output_path = output_path or VALIDATION_MD

    lines = [
        "# Validation Report: H-M3",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Gate Type:** {GATE_TYPE}",
        f"**Gate Result:** {gate_result}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]

    # Determine overall finding
    if gate_result == "PASS":
        lines.append(
            "The hypothesis that RLHF-induced distortion is **geometric** (not scalar) "
            "is **SUPPORTED**. Both model families show statistically significant "
            "refinement degradation in instruct models, indicating the probability "
            "landscape shape is affected, not just rescaled."
        )
    else:
        lines.append(
            "The hypothesis that RLHF-induced distortion is geometric is "
            "**NOT FULLY SUPPORTED**. Not all model families show significant "
            "refinement degradation in instruct models."
        )

    lines.extend([
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Family | Base Refinement | Instruct Refinement | Δ Refinement | p-value | Gate Pass |",
        "|--------|-----------------|---------------------|--------------|---------|-----------|",
    ])

    for family, results in family_results.items():
        base_ref = results["base"]["decomposition"]["refinement"]
        inst_ref = results["instruct"]["decomposition"]["refinement"]
        delta = results["refinement_difference"]["delta_mean"]
        p_val = results["refinement_difference"]["p_value"]
        gate_pass = "PASS" if results["gate_pass"] else "FAIL"

        lines.append(
            f"| {family.title()} | {base_ref:.4f} | {inst_ref:.4f} | "
            f"{delta:+.4f} | {p_val:.4f} | {gate_pass} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Detailed Results",
        "",
    ])

    for family, results in family_results.items():
        base = results["base"]
        inst = results["instruct"]
        ref_diff = results["refinement_difference"]
        rel_diff = results["reliability_difference"]

        lines.extend([
            f"### {family.title()}",
            "",
            f"**N samples:** {results['n_samples']}",
            "",
            "#### Brier Decomposition",
            "",
            "| Component | Base | Instruct | Δ (Base - Instruct) |",
            "|-----------|------|----------|---------------------|",
        ])

        for comp in ["brier_score", "reliability", "resolution", "uncertainty"]:
            b_val = base["decomposition"][comp]
            i_val = inst["decomposition"][comp]
            delta = b_val - i_val
            lines.append(f"| {comp.title()} | {b_val:.4f} | {i_val:.4f} | {delta:+.4f} |")

        lines.extend([
            "",
            "#### Refinement Difference (Primary Metric)",
            "",
            f"- **Δ Refinement:** {ref_diff['delta_mean']:+.4f} "
            f"(95% CI: [{ref_diff['delta_ci_lower']:+.4f}, {ref_diff['delta_ci_upper']:+.4f}])",
            f"- **p-value:** {ref_diff['p_value']:.4f}",
            f"- **Effect size (Cohen's d):** {ref_diff['effect_size']:.4f}",
            f"- **Direction correct:** {'Yes' if results['gate_details']['direction_correct'] else 'No'}",
            f"- **CI excludes zero:** {'Yes' if results['gate_details']['ci_excludes_zero'] else 'No'}",
            f"- **Gate pass:** {'PASS' if results['gate_pass'] else 'FAIL'}",
            "",
            "#### Reliability Difference (Secondary)",
            "",
            f"- **Δ Reliability:** {rel_diff['delta_mean']:+.4f} "
            f"(95% CI: [{rel_diff['delta_ci_lower']:+.4f}, {rel_diff['delta_ci_upper']:+.4f}])",
            f"- **p-value:** {rel_diff['p_value']:.4f}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Interpretation",
        "",
        "### Hypothesis: Geometric vs Scalar Distortion",
        "",
        "The Murphy (1973) Brier score decomposition separates prediction quality into:",
        "",
        "- **Reliability (REL):** Calibration error - how well probabilities match observed frequencies",
        "- **Resolution/Refinement (RES):** Discrimination - how well predictions distinguish outcomes",
        "- **Uncertainty (UNC):** Base rate entropy - inherent unpredictability",
        "",
        "**Scalar distortion** (temperature-like rescaling) would primarily affect Reliability,",
        "as rescaling shifts probabilities toward or away from extremes without changing discrimination.",
        "",
        "**Geometric distortion** affects the shape of the probability landscape, degrading",
        "the model's ability to discriminate between correct and incorrect answers (Refinement).",
        "",
    ])

    if gate_result == "PASS":
        lines.extend([
            "### Findings",
            "",
            "The observed Refinement degradation in instruct models across both families",
            "supports the **geometric distortion** interpretation. This is consistent with",
            "the hypothesis chain:",
            "",
            "1. **H-E1:** AUROC degradation (discriminative ability decreases)",
            "2. **H-M1:** Margin inflation for incorrect predictions",
            "3. **H-M2:** Percentile-normalized slope attenuation",
            "4. **H-M3:** Refinement degradation (THIS EXPERIMENT)",
            "",
            "The probability landscape is fundamentally reshaped by RLHF, not merely rescaled.",
        ])
    else:
        lines.extend([
            "### Limitations",
            "",
            "The results do not fully support the geometric distortion hypothesis.",
            "This may indicate:",
            "",
            "- The effect is model-specific",
            "- Scalar rescaling may be the dominant effect",
            "- Additional confounds need investigation",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Figures",
        "",
        "1. `figures/brier_decomposition_comparison.png` - Component comparison",
        "2. `figures/reliability_diagram.png` - Calibration curves",
        "3. `figures/refinement_delta_forest.png` - Forest plot of Δ refinement",
        "4. `figures/decomposition_verification.png` - BS = REL - RES + UNC check",
        "",
        "---",
        "",
        "*Generated by Phase 4 Validation Pipeline*",
    ])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
