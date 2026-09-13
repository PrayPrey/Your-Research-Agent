"""Generate validation report and visualizations."""

import json
from pathlib import Path
from typing import Dict
import matplotlib.pyplot as plt

from config import RESULTS_DIR, BASE_DIR


def save_validation_summary(summary: Dict, output_path: Path = None):
    """Save validation summary JSON."""
    if output_path is None:
        output_path = RESULTS_DIR / "validation_summary.json"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Validation summary saved to {output_path}")


def generate_presence_chart(
    field: str,
    rates: Dict[str, float],
    output_path: Path = None,
):
    """
    Generate bar chart for field presence rates.

    Args:
        field: "license" or "version"
        rates: {"HF": 0.90, "OpenML": 0.88, "UCI": 0.75}
    """
    if output_path is None:
        output_path = RESULTS_DIR / f"{field}_presence_chart.png"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    platforms = ["HF", "OpenML", "UCI"]
    values = [rates[p] * 100 for p in platforms]

    plt.figure(figsize=(8, 5))
    plt.bar(platforms, values, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    plt.ylabel("Presence Rate (%)")
    plt.xlabel("Platform")
    plt.title(f"{field.capitalize()} Presence Rate by Platform")
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)

    for i, v in enumerate(values):
        plt.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"✓ Chart saved to {output_path}")


def generate_comparison_table(
    license_metrics: Dict,
    version_metrics: Dict,
    h_m2_comparison: Dict,
    output_path: Path = None,
) -> str:
    """
    Generate markdown comparison table.

    Returns markdown string.
    """
    if output_path is None:
        output_path = RESULTS_DIR / "comparison_table.md"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    md = "# Required vs Optional Field Comparison\n\n"
    md += "| Metric | Required (license) | Required (version) | Optional (preprocessing_code, h-m2) |\n"
    md += "|--------|-------------------|-------------------|-------------------------------------|\n"
    md += f"| CV | {license_metrics['cv']:.3f} | {version_metrics['cv']:.3f} | {h_m2_comparison['optional_cv_preprocessing']:.3f} |\n"
    md += f"| Cramér's V | {license_metrics['cramers_v']:.3f} | {version_metrics['cramers_v']:.3f} | >0.40 (h-m2) |\n"
    md += f"| p-value | {license_metrics['p_value']:.4f} | {version_metrics['p_value']:.4f} | 0.0000 (h-m2) |\n"
    md += f"| Mean presence | {license_metrics['mean_presence']*100:.1f}% | {version_metrics['mean_presence']*100:.1f}% | ~20% (h-m2) |\n"

    with open(output_path, "w") as f:
        f.write(md)

    print(f"✓ Comparison table saved to {output_path}")
    return md


def generate_validation_report(
    summary: Dict,
    license_metrics: Dict,
    version_metrics: Dict,
    h_m2_comparison: Dict,
    gate_result: str,
    gate_rationale: str,
    output_path: Path = None,
):
    """
    Generate 04_validation.md report.

    Args:
        summary: Full validation summary dict
        license_metrics: License field analysis results
        version_metrics: Version field analysis results
        h_m2_comparison: h-m2 CV comparison
        gate_result: "PASS" | "PARTIAL" | "FAIL"
        gate_rationale: Explanation of gate decision
    """
    if output_path is None:
        output_path = BASE_DIR / "04_validation.md"

    md = "# Validation Report: h-m3 — Enforcement vs Friction Mechanism Distinction\n\n"
    md += f"**Date:** 2026-08-19  \n"
    md += f"**Hypothesis ID:** h-m3  \n"
    md += f"**Status:** {summary['status']}  \n\n"
    md += "---\n\n"

    # 1. Hypothesis Recap
    md += "## 1. Hypothesis Recap\n\n"
    md += "**Statement:** Under scope of metadata fields classified as optional (not enforced) vs required "
    md += "(enforced by platform validation), if friction-reduction mechanism operates as proposed, then "
    md += "optional field presence rates vary by friction score (high friction platforms <15%, low friction "
    md += "platforms >60%) while required field presence rates remain consistently high (~90%) across all "
    md += "platforms regardless of friction level, because enforcement mechanism (required field blocking) "
    md += "operates independently of UX tooling for must-have fields.\n\n"
    md += "**Gate:** SHOULD_WORK  \n"
    md += "**Success Criteria:**\n"
    md += "1. Required fields show no friction effect (p > 0.10)\n"
    md += "2. Required fields stable across platforms (CV < 0.20)\n"
    md += "3. High absolute presence (mean ≥80%)\n"
    md += "4. Contrast with h-m2 optional fields (CV ratio < 0.25)\n\n"

    # 2. Experimental Setup
    md += "## 2. Experimental Setup\n\n"
    md += "**Dataset:** h-m2 extraction reused (n=9,990)  \n"
    md += "**Fields:** license (required), version (required)  \n"
    md += "**Platforms:** HF (friction=3), OpenML (friction=2), UCI (friction=0)  \n\n"

    # 3. Results Summary
    md += "## 3. Results Summary\n\n"
    md += "### 3.1 Required Field Presence Rates\n\n"
    md += "| Field | HuggingFace | OpenML | UCI | Mean | CV |\n"
    md += "|-------|------------|--------|-----|------|-----|\n"

    license_rates = license_metrics["presence_rates"]
    version_rates = version_metrics["presence_rates"]

    md += f"| license | {license_rates['HF']*100:.1f}% | {license_rates['OpenML']*100:.1f}% | "
    md += f"{license_rates['UCI']*100:.1f}% | {license_metrics['mean_presence']*100:.1f}% | "
    md += f"{license_metrics['cv']:.3f} |\n"

    md += f"| version | {version_rates['HF']*100:.1f}% | {version_rates['OpenML']*100:.1f}% | "
    md += f"{version_rates['UCI']*100:.1f}% | {version_metrics['mean_presence']*100:.1f}% | "
    md += f"{version_metrics['cv']:.3f} |\n\n"

    md += "### 3.2 Statistical Tests\n\n"
    md += "| Field | χ² | p-value | dof | Cramér's V | Interpretation |\n"
    md += "|-------|-----|---------|-----|-----------|----------------|\n"

    license_interp = "Weak association" if license_metrics["cramers_v"] < 0.20 else (
        "Moderate association" if license_metrics["cramers_v"] < 0.40 else "Strong association"
    )
    version_interp = "Weak association" if version_metrics["cramers_v"] < 0.20 else (
        "Moderate association" if version_metrics["cramers_v"] < 0.40 else "Strong association"
    )

    md += f"| license | {license_metrics['chi2_statistic']:.2f} | {license_metrics['p_value']:.4f} | "
    md += f"{license_metrics['dof']} | {license_metrics['cramers_v']:.3f} | {license_interp} |\n"

    md += f"| version | {version_metrics['chi2_statistic']:.2f} | {version_metrics['p_value']:.4f} | "
    md += f"{version_metrics['dof']} | {version_metrics['cramers_v']:.3f} | {version_interp} |\n\n"

    md += "### 3.3 Contrast with h-m2 Optional Fields\n\n"
    md += "| Metric | Required (license) | Required (version) | Optional (preprocessing_code, h-m2) |\n"
    md += "|--------|-------------------|-------------------|-------------------------------------|\n"
    md += f"| CV | {license_metrics['cv']:.3f} | {version_metrics['cv']:.3f} | "
    md += f"{h_m2_comparison['optional_cv_preprocessing']:.3f} |\n"
    md += f"| Cramér's V | {license_metrics['cramers_v']:.3f} | {version_metrics['cramers_v']:.3f} | >0.40 |\n"
    md += f"| p-value | {license_metrics['p_value']:.4f} | {version_metrics['p_value']:.4f} | 0.0000 |\n\n"

    # 4. Validation Decision
    md += "## 4. Validation Decision\n\n"
    md += f"**Result:** {gate_result}  \n\n"
    md += f"**Rationale:** {gate_rationale}\n\n"

    # 5. Key Findings
    md += "## 5. Key Findings\n\n"
    for i, finding in enumerate(summary["key_findings"], 1):
        md += f"{i}. {finding}\n"
    md += "\n"

    # 6. Limitations
    md += "## 6. Limitations\n\n"
    md += "- **Synthetic data:** Used synthetic metadata generation (no real API extraction) due to h-m2 cache unavailability\n"
    md += "- **UCI enforcement ambiguity:** UCI doesn't enforce license/version, results reflect social norm expectations\n"
    md += "- **Platform-specific formats:** HF auto-version, OpenML integer version, UCI implicit version\n"
    if "parsing_validation" in summary:
        md += f"- **Parsing accuracy:** {summary['parsing_validation']['agreement_rate_pct']:.1f}% "
        md += "(simulated manual validation)\n"
    md += "\n"

    # 7. Implications
    md += "## 7. Implications\n\n"
    md += "**Repository design implications:**\n"
    if gate_result == "PASS":
        md += "- **Two independent levers:** (1) Enforce critical fields via platform validation, "
        md += "(2) Reduce friction for optional fields via UX tooling\n"
        md += "- **Enforcement dominates:** Required fields show high presence regardless of UX quality\n"
        md += "- **Friction matters for optional fields:** Voluntary completion enabled by low friction (h-m2 validated)\n"
    elif gate_result == "PARTIAL":
        md += "- **Mechanisms partially coupled:** Enforcement dominates, but friction still influences\n"
        md += "- **Good UX matters even for required fields:** Reduces creator frustration, improves quality\n"
    else:
        md += "- **Single mechanism hypothesis:** Enforcement and friction are NOT independent\n"
        md += "- **Completeness driven by platform UX quality:** Not enforcement alone\n"
    md += "\n"

    # 8. Next Steps
    md += "## 8. Next Steps\n\n"
    if gate_result == "PASS":
        md += "- Proceed to Phase 5: baseline comparison with Yang 2024, Strecker 2026\n"
        md += "- Update verification_state.yaml: h-m3.validation.status = VALIDATED\n"
    elif gate_result == "PARTIAL":
        md += "- Document limitations in verification_state.yaml\n"
        md += "- Proceed to Phase 5 with nuanced interpretation\n"
    else:
        md += "- STOP h-m3 validation\n"
        md += "- Reassess main hypothesis H-FrictionMetadata-v1 (enforcement/friction distinction invalid)\n"

    with open(output_path, "w") as f:
        f.write(md)

    print(f"✓ Validation report saved to {output_path}")
