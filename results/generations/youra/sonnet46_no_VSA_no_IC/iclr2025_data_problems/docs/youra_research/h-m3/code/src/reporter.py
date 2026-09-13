"""Generate panel summary and results markdown for H-M3."""
from __future__ import annotations
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def save_panel_summary(
    focal_coeffs: dict,
    p1_p2: dict,
    fdr: dict,
    gate: dict,
    p4: dict,
    r2_decomp: dict,
    vif_info: dict,
    output_dir: Path,
) -> None:
    """Save full panel summary JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "focal_coefficients": focal_coeffs,
        "p1_p2_tests": p1_p2,
        "fdr_lrt": fdr,
        "gate": gate,
        "p4_spearman": p4,
        "r2_decomposition": r2_decomp,
        "vif_diagnostics": vif_info,
    }
    (output_dir / "panel_summary.json").write_text(json.dumps(payload, indent=2, default=str))
    log.info("Panel summary saved")


def generate_results_markdown(
    gate: dict,
    p1_p2: dict,
    fdr: dict,
    focal_coeffs: dict,
    r2_decomp: dict,
    vif_info: dict,
    output_path: Path,
) -> None:
    """Generate 04_results_summary.md."""
    p1 = p1_p2["P1"]
    p2 = p1_p2["P2"]
    gate_status = gate.get("status", "UNKNOWN")
    route = gate.get("route", "UNKNOWN")

    lines = [
        "# H-M3 Results Summary",
        "## Panel OLS Regression — Domain Coefficient Benchmark-Specificity",
        "",
        f"**Gate Status:** {gate_status} → {route}",
        "",
        "## P1 Test (β_Wikipedia > β_Books3 for MMLU)",
        f"- Direction: {p1['direction']}",
        f"- β_Wikipedia: {p1.get('beta_wiki_mmlu', 'N/A')}",
        f"- β_Books3: {p1.get('beta_books_mmlu', 'N/A')}",
        f"- z-stat: {p1.get('z', 'N/A'):.4f}" if isinstance(p1.get("z"), float) else f"- z-stat: N/A",
        f"- p (one-tailed): {p1.get('p_one_tailed', 'N/A'):.4f}" if isinstance(p1.get("p_one_tailed"), float) else "- p: N/A",
        f"- **Passed: {p1['passed']}**",
        "",
        "## P2 Test (β_Books3 > β_Wikipedia for HellaSwag)",
        f"- Direction: {p2['direction']}",
        f"- β_Books3: {p2.get('beta_books_hs', 'N/A')}",
        f"- β_Wikipedia: {p2.get('beta_wiki_hs', 'N/A')}",
        f"- z-stat: {p2.get('z', 'N/A'):.4f}" if isinstance(p2.get("z"), float) else f"- z-stat: N/A",
        f"- p (one-tailed): {p2.get('p_one_tailed', 'N/A'):.4f}" if isinstance(p2.get("p_one_tailed"), float) else "- p: N/A",
        f"- **Passed: {p2['passed']}**",
        "",
        "## P3 Test (LRT: shared-β vs benchmark-specific-β)",
        f"- Significant pairs: {fdr.get('n_significant', 0)}/6",
        f"- **Passed: {fdr.get('p3_passed', False)}**",
        "",
        "## VIF Diagnostics",
        f"- PCA applied: {vif_info.get('pca_applied', False)}",
        f"- Max VIF: {vif_info.get('max_vif', 'N/A')}",
        "",
        "## R² Decomposition",
    ]
    for bench, r2 in r2_decomp.items():
        lines.append(f"- {bench}: domain_only={r2.get('domain_only_within', 'N/A')}, scale_only={r2.get('scale_only_pooled', 'N/A')}")

    lines += [
        "",
        "## Gate Summary",
        f"| Gate | Result |",
        f"|------|--------|",
        f"| P1 (MMLU β_wiki > β_books) | {'PASS' if p1['passed'] else 'FAIL'} |",
        f"| P2 (HellaSwag β_books > β_wiki) | {'PASS' if p2['passed'] else 'FAIL'} |",
        f"| P3 (LRT ≥2 pairs) | {'PASS' if fdr.get('p3_passed') else 'FAIL'} |",
        f"| P4 (Spearman ρ > 0.7) | {gate.get('P4_passed', 'N/A')} |",
        "",
        f"**Final Route: {route}**",
    ]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    log.info(f"Results summary written to {output_path}")
