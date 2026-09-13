"""Generate JSON results and Markdown summary report."""
import json
import os
from datetime import datetime

from config import RESULTS_JSON, SUMMARY_MD


def save_results_json(
    gate_result: dict,
    reg_results: dict,
    sample_sizes: dict,
    depth_stats_mohawk: dict,
    depth_stats_lawcat: dict,
) -> str:
    """Save structured results to h_m2_results.json."""
    ssm = reg_results["mohawk_ssm"]
    lawcat = reg_results["lawcat"]
    holm_p = reg_results["holm_corrected_p_values"]

    output = {
        "gate_pass": gate_result["gate_pass"],
        "verdict": gate_result["verdict"],
        "ratio": gate_result["ratio"],
        "ci_overlap": gate_result["ci_overlap"],
        "mohawk_ssm": {
            "beta": round(ssm["beta"], 6),
            "ci_low": round(ssm["ci_low"], 6),
            "ci_high": round(ssm["ci_high"], 6),
            "p_value": round(ssm["p_value"], 6),
            "method": ssm["method"],
        },
        "lawcat": {
            "beta": round(lawcat["beta"], 6),
            "ci_low": round(lawcat["ci_low"], 6),
            "ci_high": round(lawcat["ci_high"], 6),
            "p_value": round(lawcat["p_value"], 6),
            "method": lawcat["method"],
        },
        "sample_sizes": sample_sizes,
        "holm_corrected_p_values": {
            "mohawk_ssm": round(holm_p["mohawk_ssm"], 6),
            "lawcat": round(holm_p["lawcat"], 6),
        },
        "depth_percentile_stats": {
            "mohawk_ssm": depth_stats_mohawk,
            "lawcat": depth_stats_lawcat,
        },
        "analysis_timestamp": datetime.now().isoformat(),
    }

    with open(RESULTS_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[Reporter] Results saved: {RESULTS_JSON}")
    return RESULTS_JSON


def save_summary_md(
    gate_result: dict,
    reg_results: dict,
    sample_sizes: dict,
    depth_stats_mohawk: dict,
    figure_paths: list[str],
) -> str:
    """Save Markdown summary report."""
    ssm = reg_results["mohawk_ssm"]
    lawcat = reg_results["lawcat"]
    holm_p = reg_results["holm_corrected_p_values"]

    verdict = gate_result["verdict"]
    ratio = gate_result["ratio"]
    gate_icon = "✅" if gate_result["gate_pass"] else ("⚠️" if verdict == "PARTIAL" else "❌")

    lines = [
        "# H-M2 Analysis Summary",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Gate:** SHOULD_WORK | **Verdict:** {gate_icon} {verdict}",
        "",
        "## Gate Criterion",
        f"| Metric | Value | Threshold | Pass? |",
        f"|--------|-------|-----------|-------|",
        f"| Ratio \\|β_SSM\\|/\\|β_LAWCAT\\| | {ratio:.3f} | ≥2.0 | {'✅' if ratio >= 2.0 else '❌'} |",
        f"| CI non-overlap | {not gate_result['ci_overlap']} | True | {'✅' if not gate_result['ci_overlap'] else '❌'} |",
        "",
        "## Regression Results",
        "| Model | β_depth | 95% CI | Holm-p | Method |",
        "|-------|---------|--------|--------|--------|",
        f"| MOHAWK-SSM | {ssm['beta']:.4f} | [{ssm['ci_low']:.4f}, {ssm['ci_high']:.4f}] | {holm_p['mohawk_ssm']:.4f} | {ssm['method']} |",
        f"| LAWCAT | {lawcat['beta']:.4f} | [{lawcat['ci_low']:.4f}, {lawcat['ci_high']:.4f}] | {holm_p['lawcat']:.4f} | {lawcat['method']} |",
        "",
        "## Sample Sizes (Retrieval Subset)",
        f"- MOHAWK-SSM: {sample_sizes.get('mohawk_ssm', 'N/A')} examples",
        f"- LAWCAT: {sample_sizes.get('lawcat', 'N/A')} examples",
        f"- Depth fallback rate (MOHAWK): {depth_stats_mohawk.get('fallback_fraction', 0):.1%}",
        "",
        "## Figures",
    ]

    for fp in figure_paths:
        fname = os.path.basename(fp)
        lines.append(f"- [{fname}](figures/{fname})")

    lines.extend([
        "",
        "## Interpretation",
        f"{'The hypothesis is supported.' if gate_result['gate_pass'] else 'The hypothesis is not supported at this threshold.'}",
        f"MOHAWK-SSM β_depth = {ssm['beta']:.4f}, LAWCAT β_depth = {lawcat['beta']:.4f}.",
        f"Ratio = {ratio:.3f} (threshold = 2.0).",
        "",
        "**Note on data source:** H-E1 distillation failed due to port conflict (EADDRINUSE).",
        "H-M2 analysis uses proxy prediction data generated from the base LLaMA-3.1-8B model.",
        "This tests the statistical pipeline end-to-end; results reflect base model behavior,",
        "not converted MOHAWK-SSM / LAWCAT models. Re-run after H-E1 completes for true hypothesis test.",
    ])

    content = "\n".join(lines)
    with open(SUMMARY_MD, "w") as f:
        f.write(content)
    print(f"[Reporter] Summary saved: {SUMMARY_MD}")
    return SUMMARY_MD
