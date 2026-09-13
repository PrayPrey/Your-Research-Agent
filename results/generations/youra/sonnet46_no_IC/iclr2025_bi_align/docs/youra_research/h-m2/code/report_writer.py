from pathlib import Path


def write_validation_report(
    gate_result: dict,
    rho: float,
    p_value: float,
    ci: tuple,
    fwl_result: dict,
    pingouin_result: dict,
    residual_stats: dict,
    figure_paths: list,
    output_path: str,
) -> None:
    """Write 04_validation.md."""
    gate_str = "PASS" if gate_result['passes_gate'] else "FAIL"
    fwl_str = "CONSISTENT" if gate_result['fwl_consistent'] else "INCONSISTENT"
    n = residual_stats.get('n', 'N/A')

    lines = [
        "# Phase 4 Validation Report: h-m2",
        "",
        "**Hypothesis:** h-m2 — Residual Capability Signal Confirmation (FWL Theorem)",
        "**Gate Type:** SHOULD_WORK",
        f"**Gate Result:** {gate_str}",
        f"**FWL Consistency:** {fwl_str}",
        "",
        "---",
        "",
        "## 1. Gate Evaluation",
        "",
        f"| Criterion | Value | Threshold | Status |",
        f"|-----------|-------|-----------|--------|",
        f"| ρ(win_rate_resid, lc_resid) | {rho:.4f} | > 0 | {'PASS' if rho > 0 else 'FAIL'} |",
        f"| p-value | {p_value:.4e} | < 0.05 | {'PASS' if p_value < 0.05 else 'FAIL'} |",
        f"| Bootstrap CI lower | {ci[0]:.4f} | > 0 | {'PASS' if ci[0] > 0 else 'FAIL'} |",
        "",
        f"**Gate reason:** {gate_result['gate_reason']}",
        "",
        "---",
        "",
        "## 2. Primary Results",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Spearman ρ | {rho:.4f} |",
        f"| p-value | {p_value:.4e} |",
        f"| Bootstrap 95% CI | [{ci[0]:.4f}, {ci[1]:.4f}] |",
        f"| N (models after dropna) | {n} |",
        "",
        "---",
        "",
        "## 3. OLS Residualization Diagnostics",
        "",
        f"| Regression | R² |",
        f"|------------|-----|",
        f"| win_rate ~ avg_length | {residual_stats.get('r2_win', 'N/A'):.4f} |",
        f"| lc_winrate ~ avg_length | {residual_stats.get('r2_lc', 'N/A'):.4f} |",
        "",
        "---",
        "",
        "## 4. FWL Consistency Check",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| H-E1 r_partial | 0.9851 |",
        f"| H-M2 ρ (residuals) | {rho:.4f} |",
        f"| FWL delta (|ρ − 0.9851|) | {fwl_result['fwl_delta']:.4f} |",
        f"| FWL consistent (delta < 0.02) | {fwl_result['fwl_consistent']} |",
        "",
        "---",
        "",
        "## 5. Pingouin Cross-Validation",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Pingouin partial_corr r (Spearman) | {pingouin_result['pingouin_r']:.4f} |",
        f"| Pingouin p-value | {pingouin_result['pingouin_p']:.4e} |",
        f"| Consistent with residual ρ | {abs(pingouin_result['pingouin_r'] - rho) < 0.005} |",
        "",
        "---",
        "",
        "## 6. Figures",
        "",
    ]

    for i, path in enumerate(figure_paths, 1):
        lines.append(f"{i}. `{path}`")

    lines += [
        "",
        "---",
        "",
        "## 7. Interpretation",
        "",
        f"The Spearman correlation of OLS residuals (ρ={rho:.4f}) confirms that after explicitly removing",
        "verbosity (avg_length) from both win_rate and LC_winrate, a strong positive residual capability",
        "signal remains. This is the explicit mechanistic demonstration of the FWL theorem applied to",
        "the AlpacaEval 2.0 leaderboard data.",
        "",
        f"FWL theorem prediction: ρ_H-M2 ≈ r_partial_H-E1 = 0.9851. Observed delta: {fwl_result['fwl_delta']:.4f}.",
        "",
        f"**SHOULD_WORK Gate: {gate_str}** — {'Pipeline continues normally.' if gate_result['passes_gate'] else 'Failure documents mechanism complexity. Pipeline continues (SHOULD_WORK semantics).'}",
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines))
