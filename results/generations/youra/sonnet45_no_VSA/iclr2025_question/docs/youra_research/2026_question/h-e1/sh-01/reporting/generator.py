"""Validation report generator."""

from typing import Dict
from datetime import datetime
import os


class ReportGenerator:
    """Generate validation report in markdown format."""

    def __init__(self, output_dir: str, figures_dir: str):
        self.output_dir = output_dir
        self.figures_dir = figures_dir

    def check_gate_conditions(
        self,
        delta_rho: float,
        r_squared: float,
        p_value: float,
        target_delta: float = 0.15,
        target_r2: float = 0.6,
        target_pval: float = 0.05
    ) -> Dict:
        """Check if gate conditions are satisfied.

        Args:
            delta_rho: Actual Δρ_j value
            r_squared: Actual R² value
            p_value: Actual p-value
            target_delta: Target threshold for Δρ_j
            target_r2: Target threshold for R²
            target_pval: Target threshold for p-value

        Returns:
            Dict with pass status, verdict, and failures
        """
        failures = []

        # Check Δρ_j > 0.15
        if delta_rho <= target_delta:
            failures.append(f"Δρ_j = {delta_rho:.3f} ≤ {target_delta} (FAIL)")

        # Check R² > 0.6
        if r_squared <= target_r2:
            failures.append(f"R² = {r_squared:.3f} ≤ {target_r2} (FAIL)")

        # Check p-value < 0.05
        if p_value >= target_pval:
            failures.append(f"p-value = {p_value:.3f} ≥ {target_pval} (FAIL)")

        passed = len(failures) == 0

        if passed:
            verdict = "PASS"
            justification = "All gate conditions satisfied."
        else:
            verdict = "FAIL"
            justification = "Gate conditions not satisfied:\n" + "\n".join(f"  - {f}" for f in failures)

        return {
            "pass": passed,
            "verdict": verdict,
            "failures": failures,
            "justification": justification
        }

    def generate_validation_report(
        self,
        results: Dict,
        hypothesis_id: str,
        save_path: str = None
    ) -> str:
        """Generate validation report markdown.

        Args:
            results: Dict with all experiment results
            hypothesis_id: Hypothesis identifier
            save_path: Path to save report

        Returns:
            Generated markdown content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract metrics
        gate_check = results.get("gate_check", {})
        stats = results.get("statistics", {})
        factual_eval = results.get("factual_eval", {})
        creative_eval = results.get("creative_eval", {})

        # Build markdown report
        md_lines = [
            f"# Validation Report: {hypothesis_id}",
            "",
            f"**Date:** {timestamp}",
            f"**Hypothesis Statement:** Median ρ_j drops >0.15 when CCP is applied to creative fiction vs factual biography",
            f"**Gate Type:** MUST_WORK",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"**Gate Verdict:** {gate_check.get('verdict', 'UNKNOWN')}",
            "",
            gate_check.get('justification', 'No justification provided.'),
            "",
            "---",
            "",
            "## Metrics Summary",
            "",
            "### Primary Metrics",
            "",
            f"- **Δρ_j (Factual - Creative):** {stats.get('delta_rho_j', 0):.4f}",
            f"  - Factual median: {stats.get('median_factual', 0):.4f}",
            f"  - Creative median: {stats.get('median_creative', 0):.4f}",
            f"  - Target: > 0.15",
            f"  - Status: {'✅ PASS' if stats.get('delta_rho_j', 0) > 0.15 else '❌ FAIL'}",
            "",
            f"- **R² (Correlation):** {stats.get('r_squared', 0):.4f}",
            f"  - Target: > 0.6",
            f"  - Status: {'✅ PASS' if stats.get('r_squared', 0) > 0.6 else '❌ FAIL'}",
            "",
            f"- **p-value (Mann-Whitney U):** {stats.get('p_value', 1):.4f}",
            f"  - Target: < 0.05",
            f"  - Status: {'✅ PASS' if stats.get('p_value', 1) < 0.05 else '❌ FAIL'}",
            "",
            "### Domain-Level Results",
            "",
            "**Factual Domain (TruthfulQA):**",
            f"- Sample size: {factual_eval.get('n_samples', 0)}",
            f"- Median ρ_j: {factual_eval.get('median_rho_j', 0):.4f}",
            f"- ROC-AUC: {stats.get('factual_roc_auc', 0):.4f}",
            "",
            "**Creative Domain (WritingPrompts):**",
            f"- Sample size: {creative_eval.get('n_samples', 0)}",
            f"- Median ρ_j: {creative_eval.get('median_rho_j', 0):.4f}",
            f"- ROC-AUC: {stats.get('creative_roc_auc', 0):.4f}",
            "",
            "---",
            "",
            "## Figures",
            "",
            "### Gate Metrics Comparison",
            "![Gate Metrics](figures/gate_metrics.png)",
            "",
            "### ρ_j Distribution by Domain",
            "![ρ_j Distribution](figures/rho_distribution.png)",
            "",
            "### Correlation Plot",
            "![Correlation](figures/correlation.png)",
            "",
            "### Domain Degradation",
            "![Degradation](figures/degradation.png)",
            "",
            "---",
            "",
            "## Reflection",
            "",
            "### Hypothesis Outcome",
            "",
        ]

        if gate_check.get("pass", False):
            md_lines.extend([
                "The hypothesis **PASSES** validation. The CCP metric shows significant ontology sensitivity:",
                "",
                "1. **Δρ_j exceeds threshold**: The median ρ_j degradation is statistically significant and practically meaningful.",
                "2. **Strong correlation**: R² indicates a monotonic relationship between ρ_j and ROC-AUC.",
                "3. **Statistical significance**: Mann-Whitney U test confirms the domain difference is not due to chance.",
                "",
                "**Interpretation:** CCP's NLI-based conditioning exhibits implicit factual-ontology assumptions that misalign with creative semantics, as predicted by the main hypothesis.",
            ])
        else:
            md_lines.extend([
                "The hypothesis **FAILS** validation. Gate conditions are not satisfied:",
                "",
            ])
            for failure in gate_check.get("failures", []):
                md_lines.append(f"- {failure}")
            md_lines.extend([
                "",
                "**Recommendation:** Route to Phase 2A (Dialogue) for mechanism refinement.",
            ])

        md_lines.extend([
            "",
            "### Limitations",
            "",
            "- Sample size: 200 per domain (sufficient per power analysis, but larger samples would increase robustness)",
            "- LLM dependency: Results specific to GPT-3.5-turbo generation patterns",
            "- NLI model: DeBERTa-v3-large-mnli may have domain-specific biases",
            "- Simplified CCP: Full token-replacement evaluation would require more computational resources",
            "",
            "### Next Steps",
            "",
        ])

        if gate_check.get("pass", False):
            md_lines.extend([
                "1. Proceed to dependent hypotheses (sh-02 to sh-07)",
                "2. Explore category-specific ρ_j patterns (TruthfulQA categories)",
                "3. Investigate correlation mechanisms in detail",
            ])
        else:
            md_lines.extend([
                "1. Return to Phase 2A for mechanism refinement",
                "2. Consider alternative NLI models or CCP formulations",
                "3. Expand sample size or domain diversity",
            ])

        md_lines.extend([
            "",
            "---",
            "",
            "**Generated by:** Phase 4 Validation Pipeline",
            f"**Timestamp:** {timestamp}",
        ])

        markdown_content = "\n".join(md_lines)

        # Save to file
        if save_path is None:
            save_path = os.path.join(self.output_dir, "04_validation.md")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            f.write(markdown_content)

        print(f"Validation report saved to {save_path}")

        return markdown_content
