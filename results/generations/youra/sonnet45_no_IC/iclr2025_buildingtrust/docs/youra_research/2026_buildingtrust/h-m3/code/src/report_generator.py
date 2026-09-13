"""
Validation Report Generator for H-M3
"""

import json
from pathlib import Path
from typing import Dict
from datetime import datetime


class ValidationReportGenerator:
    """Generate 04_validation.md report."""

    def __init__(self, output_path: str):
        """
        Initialize report generator.

        Args:
            output_path: Path to save 04_validation.md
        """
        self.output_path = Path(output_path)

    def generate_report(
        self,
        fisher_result: Dict,
        gate_result: Dict,
        correlations: Dict,
        effect_size: Dict
    ) -> None:
        """
        Generate 04_validation.md report.

        Args:
            fisher_result: Fisher z-test results
            gate_result: Gate evaluation results
            correlations: {"factual": dict, "misinfo": dict}
            effect_size: Effect size results
        """
        report_lines = []

        # Header
        report_lines.append("# Validation Report: h-m3")
        report_lines.append("")
        report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append("**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)")
        report_lines.append("**Gate Type:** SHOULD_WORK")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # Summary
        report_lines.append("## Summary")
        report_lines.append("")
        gate_status = "✓ PASS" if gate_result['passed'] else "✗ FAIL"
        report_lines.append(f"**Gate Result:** {gate_status}")
        report_lines.append("")

        # Test Results
        report_lines.append("## Fisher z-Test Results")
        report_lines.append("")
        report_lines.append(self.format_statistics_table(fisher_result, correlations, effect_size))
        report_lines.append("")

        # Gate Evaluation
        report_lines.append("## Gate Evaluation")
        report_lines.append("")
        report_lines.append(self.format_gate_evaluation(gate_result, fisher_result))
        report_lines.append("")

        # Visualizations
        report_lines.append("## Visualizations")
        report_lines.append("")
        report_lines.append("Generated figures:")
        report_lines.append("- `figures/gate_metrics_comparison.png` - MANDATORY gate metrics")
        report_lines.append("- `figures/forest_plot.png` - Correlation comparison with 95% CI")
        report_lines.append("- `figures/effect_size.png` - Cohen's q effect size")
        report_lines.append("")

        # Conclusion
        report_lines.append("## Conclusion")
        report_lines.append("")
        if gate_result['passed']:
            report_lines.append("**PASS:** All SHOULD_WORK gate criteria satisfied.")
            report_lines.append("")
            report_lines.append("- Fisher z-test shows significant difference (p < 0.05)")
            report_lines.append("- Correlation difference magnitude is meaningful (|Δr| ≥ 0.1)")
            report_lines.append("- Directional pattern matches theory (r_factual > 0.4, r_misinfo < 0.3)")
        else:
            report_lines.append(f"**{gate_result['result']}:** SHOULD_WORK gate criteria not fully satisfied.")
            report_lines.append("")
            report_lines.append("Failed criteria:")
            if not gate_result['primary']:
                report_lines.append("- Primary: Fisher z-test not significant (p ≥ 0.05)")
            if not gate_result['secondary']:
                report_lines.append("- Secondary: Correlation difference too small (|Δr| < 0.1)")
            if not gate_result['tertiary']:
                report_lines.append("- Tertiary: Directional pattern not satisfied")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("**Status:** COMPLETED")

        # Write report
        self.output_path.write_text('\n'.join(report_lines))
        print(f"✓ Report saved: {self.output_path}")

    def format_statistics_table(
        self,
        fisher_result: Dict,
        correlations: Dict,
        effect_size: Dict
    ) -> str:
        """Format Fisher z-test statistics as markdown table."""
        lines = []
        lines.append("| Metric | Factual | Misinformation | Comparison |")
        lines.append("|--------|---------|----------------|------------|")

        factual = correlations['factual']
        misinfo = correlations['misinfo']

        lines.append(f"| **Correlation (r)** | {factual['r']:.4f} | {misinfo['r']:.4f} | Δr = {fisher_result['delta_r']:.4f} |")
        lines.append(f"| **p-value** | {factual['p_value']:.6f} | {misinfo['p_value']:.6f} | Fisher p = {fisher_result['p_value']:.6f} |")
        lines.append(f"| **95% CI** | [{factual['ci_lower']:.4f}, {factual['ci_upper']:.4f}] | [{misinfo['ci_lower']:.4f}, {misinfo['ci_upper']:.4f}] | - |")
        lines.append(f"| **Sample size (n)** | {factual['n']} | {misinfo['n']} | - |")
        lines.append(f"| **Fisher z** | {fisher_result['z1']:.4f} | {fisher_result['z2']:.4f} | z-stat = {fisher_result['z_stat']:.4f} |")

        lines.append("")
        lines.append(f"**Effect Size:** Cohen's q = {effect_size['cohens_q']:.4f} ({effect_size['magnitude']})")

        return '\n'.join(lines)

    def format_gate_evaluation(self, gate_result: Dict, fisher_result: Dict) -> str:
        """Format gate evaluation as markdown section."""
        lines = []
        lines.append("### SHOULD_WORK Gate Criteria")
        lines.append("")

        # Primary
        status_primary = "✓ PASS" if gate_result['primary'] else "✗ FAIL"
        lines.append(f"1. **Primary (Fisher z-test significance):** {status_primary}")
        lines.append(f"   - Observed: p = {fisher_result['p_value']:.6f}")
        lines.append(f"   - Threshold: p < {gate_result['criteria']['p_threshold']}")
        lines.append("")

        # Secondary
        status_secondary = "✓ PASS" if gate_result['secondary'] else "✗ FAIL"
        lines.append(f"2. **Secondary (Effect magnitude):** {status_secondary}")
        lines.append(f"   - Observed: |Δr| = {gate_result['delta_r']:.4f}")
        lines.append(f"   - Threshold: |Δr| ≥ {gate_result['criteria']['delta_r_threshold']}")
        lines.append("")

        # Tertiary
        status_tertiary = "✓ PASS" if gate_result['tertiary'] else "✗ FAIL"
        lines.append(f"3. **Tertiary (Directional pattern):** {status_tertiary}")
        lines.append(f"   - Criteria: r_factual > 0.4 AND r_misinfo < 0.3")
        lines.append("")

        lines.append(f"**Final Gate Result:** {gate_result['result']}")

        return '\n'.join(lines)

    def save_results_json(self, results: Dict, output_path: str) -> None:
        """Save results to JSON file."""
        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved: {output_file}")
