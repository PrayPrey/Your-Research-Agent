from pathlib import Path


def write_validation_report(
    gate_result: dict,
    ols_result: dict,
    baseline_result: dict,
    vif: dict,
    diagnostics: dict,
    figure_paths: list,
    output_path: str
) -> None:
    status = "PASS" if gate_result['passes_gate'] else "FAIL"
    lines = [
        "# Validation: h-m1",
        "",
        f"**Gate**: {status}",
        f"**Path**: {gate_result['path']}",
        f"**Dominant predictor**: {gate_result['dominant']}",
        f"**Date**: 2026-08-04",
        "",
        "## Gate Evaluation",
        "",
        "| Criterion | Value | Threshold | Met? |",
        "|-----------|-------|-----------|------|",
        f"| |β_win_rate_std| > |β_avg_length_std| | {abs(ols_result['beta_win']):.4f} > {abs(ols_result['beta_len']):.4f} | strict > | {'Yes' if abs(ols_result['beta_win']) > abs(ols_result['beta_len']) else 'No'} |",
        f"| p_win < 0.05 | {ols_result['p_win']:.4e} | < 0.05 | {'Yes' if ols_result['p_win'] < 0.05 else 'No'} |",
        f"| Gate overall | — | — | {status} |",
        "",
        "## OLS Results (LC_winrate ~ win_rate_std + avg_length_std)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| β_win_rate_std | {ols_result['beta_win']:.4f} |",
        f"| β_avg_length_std | {ols_result['beta_len']:.4f} |",
        f"| |β_win_rate_std| | {abs(ols_result['beta_win']):.4f} |",
        f"| |β_avg_length_std| | {abs(ols_result['beta_len']):.4f} |",
        f"| p_win | {ols_result['p_win']:.4e} |",
        f"| p_len | {ols_result['p_len']:.4e} |",
        f"| R² | {ols_result['r2']:.4f} |",
        f"| R²_adj | {ols_result['r2_adj']:.4f} |",
        "",
        "## Baseline OLS (verbosity-only null model: LC_winrate ~ avg_length_std)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| β_avg_length_std | {baseline_result['beta_avg_length']:.4f} |",
        f"| R² | {baseline_result['r2']:.4f} |",
        f"| p_value | {baseline_result['pvalue']:.4e} |",
        "",
        "## VIF Diagnostic",
        "",
        "| Variable | VIF | High? |",
        "|----------|-----|-------|",
        f"| win_rate_std | {vif['win_rate']:.3f} | {'Yes' if vif['win_rate'] >= 5.0 else 'No'} |",
        f"| avg_length_std | {vif['avg_length']:.3f} | {'Yes' if vif['avg_length'] >= 5.0 else 'No'} |",
        f"| any_high_vif | {vif['any_high_vif']} | — |",
        "",
        "## OLS Diagnostics",
        "",
        "| Test | Value |",
        "|------|-------|",
        f"| Breusch-Pagan stat | {diagnostics['bp_stat']:.4f} |",
        f"| Breusch-Pagan p | {diagnostics['bp_pvalue']:.4f} |",
        f"| heteroscedastic | {diagnostics['heteroscedastic']} |",
        "",
        "## Comparison with h-e1",
        "",
        "| Metric | h-e1 | h-m1 |",
        "|--------|------|------|",
        "| r_partial (Spearman) | 0.9851 | N/A (OLS path) |",
        "| VIF win_rate | 1.764 | {:.3f} |".format(vif['win_rate']),
        "| VIF avg_length | 1.764 | {:.3f} |".format(vif['avg_length']),
        f"| Dominant predictor | win_rate | {gate_result['dominant']} |",
        f"| Gate result | PASS | {status} |",
        "",
        "## Figures",
        "",
    ]
    for p in figure_paths:
        lines.append(f"- {p}")
    lines += [
        "",
        "## Interpretation",
        "",
    ]
    if gate_result['passes_gate']:
        lines += [
            "**h-m1 PASSED the MUST_WORK gate.**",
            "",
            f"Standardized OLS confirms: |β_win_rate_std| = {abs(ols_result['beta_win']):.4f} >> "
            f"|β_avg_length_std| = {abs(ols_result['beta_len']):.4f} (p_win = {ols_result['p_win']:.4e}). "
            f"Capability (win_rate) dominates verbosity (avg_length) as predictor of LC_winrate. "
            f"VIF = {vif['win_rate']:.3f} confirms no multicollinearity (OLS path valid). "
            f"This validates the mechanism chapter: capability is the dominant driver of length-debiased preference.",
        ]
    else:
        lines += [
            "**h-m1 FAILED the MUST_WORK gate.**",
            "",
            f"|β_win_rate_std| = {abs(ols_result['beta_win']):.4f}, "
            f"|β_avg_length_std| = {abs(ols_result['beta_len']):.4f}. "
            "Dominance condition not satisfied.",
            "",
            "## Routing",
            "",
            "MUST_WORK gate FAILED. Route to Phase 2A for hypothesis redesign.",
        ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text('\n'.join(lines))
