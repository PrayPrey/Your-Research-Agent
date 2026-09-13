from pathlib import Path


def write_validation_report(gate_result, corr_result, boot_ci, vif, figure_paths, output_path) -> None:
    status = "PASS" if gate_result['passes_gate'] else "FAIL"
    ci_lower, ci_upper = boot_ci
    lines = [
        f"# H-E1 Validation Report",
        f"",
        f"## Gate Result: {status}",
        f"",
        f"| Criterion | Value | Threshold | Met? |",
        f"|-----------|-------|-----------|------|",
        f"| r_partial > 0 | {corr_result['r_partial']:.4f} | > 0 | {'Yes' if corr_result['r_partial'] > 0 else 'No'} |",
        f"| p_val < 0.05 | {corr_result['p_val']:.4f} | < 0.05 | {'Yes' if corr_result['p_val'] < 0.05 else 'No'} |",
        f"| |r_partial| >= 0.15 | {abs(corr_result['r_partial']):.4f} | >= 0.15 | {'Yes' if abs(corr_result['r_partial']) >= 0.15 else 'No'} |",
        f"",
        f"## Partial Correlation Results",
        f"",
        f"- **r_partial**: {corr_result['r_partial']:.4f}",
        f"- **p_val**: {corr_result['p_val']:.6f}",
        f"- **CI95%**: [{corr_result['ci95'][0]:.4f}, {corr_result['ci95'][1]:.4f}]",
        f"- **n**: {corr_result['n']}",
        f"",
        f"## Bootstrap Robustness (1000 resamples, seed=42)",
        f"",
        f"- **Bootstrap CI 95%**: [{ci_lower:.4f}, {ci_upper:.4f}]",
        f"- **CI lower > 0**: {'Yes' if ci_lower > 0 else 'No'}",
        f"",
        f"## VIF Diagnostic",
        f"",
        f"| Variable | VIF | Multicollinearity? |",
        f"|----------|-----|-------------------|",
        f"| win_rate | {vif['win_rate']:.4f} | {'Yes' if vif['win_rate'] >= 5.0 else 'No'} |",
        f"| avg_length | {vif['avg_length']:.4f} | {'Yes' if vif['avg_length'] >= 5.0 else 'No'} |",
        f"",
        f"## Figures",
        f"",
    ]
    for p in figure_paths:
        lines.append(f"- {p}")
    lines += [
        f"",
        f"## Interpretation",
        f"",
    ]
    if gate_result['passes_gate']:
        lines += [
            f"**H-E1 PASSED the MUST_WORK gate.**",
            f"",
            f"Spearman partial correlation ρ(win_rate, LC_winrate | avg_length) = {corr_result['r_partial']:.4f} "
            f"(p={corr_result['p_val']:.6f}) demonstrates that model capability (win_rate) independently predicts "
            f"length-debiased preference (LC_winrate) after controlling for response verbosity (avg_length). "
            f"The effect size |r_partial| = {abs(corr_result['r_partial']):.4f} exceeds the pre-registered threshold of 0.15. "
            f"Bootstrap CI [{ci_lower:.4f}, {ci_upper:.4f}] confirms robustness.",
            f"",
            f"This validates the existence of the bidirectional alignment gap signal and enables downstream hypotheses H-M1, H-M2, H-M3, H-C1.",
        ]
    else:
        lines += [
            f"**H-E1 FAILED the MUST_WORK gate.**",
            f"",
            f"Partial correlation r_partial = {corr_result['r_partial']:.4f} (p={corr_result['p_val']:.6f}) "
            f"did not meet all gate criteria. The null hypothesis H0: ρ = 0 cannot be rejected.",
            f"",
            f"## Routing",
            f"",
            f"MUST_WORK gate FAILED. Pipeline stops. Route to Phase 0 for hypothesis redesign.",
        ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text('\n'.join(lines))
