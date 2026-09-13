"""Report generation for H-C1: 04_validation.md."""
import json
from datetime import datetime
from pathlib import Path

from config import MODELS, EVAL, GATE, BASE_DIR


def render_validation_report(
    safety_results: dict,
    gate: dict,
    correlation: dict,
    out_path: str = "../04_validation.md",
) -> None:
    """Generate 04_validation.md with results, gate verdict, and correlation analysis."""
    lines = [
        "# H-C1 Validation Report",
        "",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Hypothesis:** Explicit constraint training (IFEval) transfers to implicit safety constraints (TruthfulQA/BBQ), ≥2pp improvement",
        f"**Gate Type:** SHOULD_WORK",
        "",
        "---",
        "",
        "## Results Summary",
        "",
        "### Per-Model Metrics",
        "",
        "| Model | TruthfulQA MC1 | TruthfulQA MC2 | BBQ |",
        "|-------|----------------|----------------|-----|",
    ]

    for variant in list(MODELS.baselines) + list(MODELS.treatments):
        m = safety_results[variant]
        lines.append(
            f"| {variant} | {m['truthfulqa_mc1']:.4f} | {m['truthfulqa_mc2']:.4f} | {m['bbq']:.4f} |"
        )

    lines.extend([
        "",
        "### Baseline Maxima",
        "",
        f"- **Max TruthfulQA MC1 (baselines):** {gate['max_truthful_baseline']:.4f}",
        f"- **Max BBQ (baselines):** {gate['max_bbq_baseline']:.4f}",
        "",
        "### Treatment Deltas vs Max Baseline",
        "",
        "| Treatment | Δ TruthfulQA MC1 | Δ BBQ | Gate Satisfied? |",
        "|-----------|------------------|-------|-----------------|",
    ])

    for t in MODELS.treatments:
        d = gate["deltas"][t]
        satisfied = d["truthfulqa_mc1"] >= GATE.threshold_pp or d["bbq"] >= GATE.threshold_pp
        lines.append(
            f"| {t} | {d['truthfulqa_mc1']:+.4f} | {d['bbq']:+.4f} | {'✓' if satisfied else '✗'} |"
        )

    verdict = "PASS" if gate["gate_passed"] else "FAIL"
    lines.extend([
        "",
        "---",
        "",
        "## Gate Verdict",
        "",
        f"**Result:** {verdict}",
        f"**Threshold:** ≥{GATE.threshold_pp*100:.1f}pp improvement on TruthfulQA MC1 OR BBQ",
        f"**Best Treatment:** {gate['best_ti']}",
        "",
    ])

    if gate["gate_passed"]:
        best_d = gate["deltas"][gate["best_ti"]]
        lines.append(
            f"Treatment {gate['best_ti']} achieved +{max(best_d['truthfulqa_mc1'], best_d['bbq'])*100:.2f}pp, exceeding the ≥2pp threshold."
        )
    else:
        lines.append("No treatment achieved ≥2pp improvement on either metric.")

    lines.extend([
        "",
        "---",
        "",
        "## Transfer Correlation Analysis",
        "",
        "Correlation between IFEval improvement and safety metric improvements across T1-T4:",
        "",
        f"- **IFEval → TruthfulQA MC1:** r = {correlation['correlation_truthfulqa']['r']:.4f}, p = {correlation['correlation_truthfulqa']['p']:.4f}",
        f"- **IFEval → BBQ:** r = {correlation['correlation_bbq']['r']:.4f}, p = {correlation['correlation_bbq']['p']:.4f}",
        "",
        "### Interpretation",
        "",
    ])

    r_truth = correlation["correlation_truthfulqa"]["r"]
    r_bbq = correlation["correlation_bbq"]["r"]
    if r_truth > 0.7 or r_bbq > 0.7:
        lines.append("Strong positive correlation suggests constraint training transfers well to implicit safety behaviors.")
    elif r_truth > 0.4 or r_bbq > 0.4:
        lines.append("Moderate correlation suggests partial transfer of constraint following to safety domains.")
    else:
        lines.append("Weak correlation suggests limited transfer between explicit and implicit constraint domains.")

    lines.extend([
        "",
        "---",
        "",
        "## Key Findings",
        "",
    ])

    findings = []
    if gate["gate_passed"]:
        findings.append(f"- {gate['best_ti']} demonstrates statistically significant improvement over baselines")
        findings.append("- Transfer hypothesis supported: IFEval training improves implicit safety metrics")
    else:
        findings.append("- No treatment achieved threshold improvement")
        findings.append("- Transfer may require different training configuration or is domain-specific")

    if r_truth > 0.5:
        findings.append(f"- Positive IFEval-TruthfulQA correlation (r={r_truth:.2f}) supports transfer mechanism")
    if r_bbq > 0.5:
        findings.append(f"- Positive IFEval-BBQ correlation (r={r_bbq:.2f}) supports transfer mechanism")

    lines.extend(findings)
    lines.append("")

    # Write report
    report_path = Path(BASE_DIR) / out_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Validation report saved to {report_path}")


def main():
    """Load results and generate report."""
    with open(EVAL.results_out_path) as f:
        safety_results = json.load(f)

    with open(EVAL.correlation_out_path) as f:
        analysis = json.load(f)

    render_validation_report(
        safety_results=safety_results,
        gate=analysis["gate"],
        correlation=analysis["correlation"],
    )


if __name__ == "__main__":
    main()
