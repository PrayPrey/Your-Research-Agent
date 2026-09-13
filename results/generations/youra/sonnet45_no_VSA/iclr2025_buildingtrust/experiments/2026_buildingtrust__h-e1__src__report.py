"""Report generation for validation results."""
import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import pandas as pd

from meta_analysis import AnalysisResults


logger = logging.getLogger(__name__)


class ValidationReportGenerator:
    """Generate validation reports and export artifacts."""

    def __init__(self, hypothesis_id: str = "h-e1", output_dir: str = "."):
        """Initialize report generator.

        Args:
            hypothesis_id: Hypothesis identifier
            output_dir: Base output directory
        """
        self.hypothesis_id = hypothesis_id
        self.output_dir = Path(output_dir)
        self.results_dir = self.output_dir / "results"
        self.data_dir = self.output_dir / "data"
        self.figures_dir = self.output_dir / "figures"

        # Create directories
        for dir_path in [self.results_dir, self.data_dir, self.figures_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def save_artifacts(
        self,
        results: AnalysisResults,
        benchmark_dict: Dict[str, pd.DataFrame]
    ) -> None:
        """Save all analysis artifacts.

        Args:
            results: Analysis results
            benchmark_dict: Benchmark corpus
        """
        logger.info("Saving analysis artifacts...")

        # Save CSV results
        results.cv_per_benchmark.to_csv(
            self.results_dir / "cv_per_benchmark.csv", index=False
        )
        results.mean_rho_per_benchmark.to_csv(
            self.results_dir / "mean_rho_per_benchmark.csv", index=False
        )
        results.pairwise_rho_matrix.to_csv(
            self.results_dir / "pairwise_rho_matrix.csv"
        )

        # Save hypothesis test results
        test_results = {
            "pearson_r": float(results.pearson_r),
            "pearson_p": float(results.pearson_p),
            "ci_lower": float(results.ci_lower),
            "ci_upper": float(results.ci_upper),
            "gate_passed": bool(results.gate_passed)
        }
        with open(self.results_dir / "hypothesis_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        # Save summary JSON
        summary = self.generate_summary_json(results)
        with open(self.results_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Save benchmark corpus
        with open(self.data_dir / "benchmark_corpus.pkl", "wb") as f:
            pickle.dump(benchmark_dict, f)

        logger.info("✓ All artifacts saved")

    def generate_summary_json(self, results: AnalysisResults) -> Dict[str, Any]:
        """Generate machine-readable summary.

        Args:
            results: Analysis results

        Returns:
            Summary dictionary
        """
        return {
            "hypothesis_id": self.hypothesis_id,
            "timestamp": datetime.now().isoformat(),
            "gate_type": "MUST_WORK",
            "gate_passed": bool(results.gate_passed),
            "hypothesis_test": {
                "pearson_r": float(results.pearson_r),
                "pearson_p": float(results.pearson_p),
                "ci_95_lower": float(results.ci_lower),
                "ci_95_upper": float(results.ci_upper)
            },
            "gate_criteria": {
                "target_r": -0.5,
                "target_p": 0.05,
                "actual_r": float(results.pearson_r),
                "actual_p": float(results.pearson_p)
            },
            "data_summary": {
                "n_benchmarks": int(len(results.cv_per_benchmark)),
                "cv_range": [
                    float(results.cv_per_benchmark["cv"].min()),
                    float(results.cv_per_benchmark["cv"].max())
                ],
                "mean_rho_range": [
                    float(results.mean_rho_per_benchmark["mean_rho"].min()),
                    float(results.mean_rho_per_benchmark["mean_rho"].max())
                ]
            }
        }

    def generate_validation_md(self, results: AnalysisResults) -> str:
        """Generate validation report in markdown.

        Args:
            results: Analysis results

        Returns:
            Markdown report content
        """
        gate_status = "✅ PASSED" if results.gate_passed else "❌ FAILED"

        report = f"""# Validation Report: H-E1

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Hypothesis:** Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05).
**Gate Type:** MUST_WORK
**Gate Status:** {gate_status}

---

## Executive Summary

This validation report presents results for hypothesis H-E1, testing whether coefficient of variation (CV) predicts cross-benchmark ranking stability (measured by mean Spearman ρ).

**Key Findings:**
- Pearson r = {results.pearson_r:.3f} (95% CI: [{results.ci_lower:.3f}, {results.ci_upper:.3f}])
- p-value = {results.pearson_p:.4f}
- Gate decision: {'PASS - CV is a valid stability predictor' if results.gate_passed else 'FAIL - CV is not a valid stability predictor'}

---

## Data Summary

### Benchmarks Analyzed
{self._format_benchmark_table(results.cv_per_benchmark, results.mean_rho_per_benchmark)}

**Total Benchmarks:** {len(results.cv_per_benchmark)}
**CV Range:** [{results.cv_per_benchmark['cv'].min():.3f}, {results.cv_per_benchmark['cv'].max():.3f}]
**Mean ρ Range:** [{results.mean_rho_per_benchmark['mean_rho'].min():.3f}, {results.mean_rho_per_benchmark['mean_rho'].max():.3f}]

---

## Hypothesis Test Results

### Primary Test: Pearson Correlation
- **Pearson r:** {results.pearson_r:.3f}
- **p-value:** {results.pearson_p:.4f}
- **95% CI:** [{results.ci_lower:.3f}, {results.ci_upper:.3f}]
- **Sample Size:** {len(results.cv_per_benchmark)} benchmarks

### Gate Criteria
- **Target r:** < -0.5 (negative moderate-to-strong correlation)
- **Actual r:** {results.pearson_r:.3f} {'✓' if results.pearson_r < -0.5 else '✗'}
- **Target p:** < 0.05 (statistical significance)
- **Actual p:** {results.pearson_p:.4f} {'✓' if results.pearson_p < 0.05 else '✗'}

### Interpretation
{self._generate_interpretation(results)}

---

## Cross-Benchmark Correlation Matrix

Pairwise Spearman ρ between all benchmarks:
{results.pairwise_rho_matrix.to_string()}

---

## Visualizations

The following figures were generated:
1. `figures/cv_vs_rho_scatter.png` - Scatter plot with regression line
2. `figures/cv_rho_per_benchmark_bars.png` - Dual bar chart
3. `figures/pairwise_rho_heatmap.png` - Correlation heatmap
4. `figures/gate_metrics_comparison.png` - Gate threshold comparison

---

## Next Steps

{self._generate_next_steps(results)}

---

## Artifacts

All analysis artifacts saved to:
- **Data:** `data/benchmark_corpus.pkl`
- **Results:** `results/*.csv`, `results/*.json`
- **Figures:** `figures/*.png`
"""
        return report

    def _format_benchmark_table(
        self,
        cv_df: pd.DataFrame,
        rho_df: pd.DataFrame
    ) -> str:
        """Format benchmark summary table."""
        merged = cv_df.merge(rho_df, on="benchmark_name")
        merged = merged.sort_values("cv")

        lines = ["| Benchmark | CV | Mean ρ | n_pairs |", "|-----------|-----|--------|---------|"]
        for _, row in merged.iterrows():
            lines.append(
                f"| {row['benchmark_name']} | {row['cv']:.3f} | "
                f"{row['mean_rho']:.3f} | {row['n_pairs']} |"
            )
        return "\n".join(lines)

    def _generate_interpretation(self, results: AnalysisResults) -> str:
        """Generate result interpretation."""
        if results.gate_passed:
            return """The hypothesis is **VALIDATED**. The negative moderate-to-strong correlation
(r < -0.5, p < 0.05) confirms that coefficient of variation (CV) is a predictive meta-feature
for cross-benchmark stability. High CV benchmarks exhibit lower ranking agreement with other
benchmarks, indicating that CV can be used as a quality signal for benchmark reliability.

This validates the foundation hypothesis and enables proceeding to mechanism hypotheses
(H-M1, H-M2) to explore *why* CV predicts stability."""
        else:
            return f"""The hypothesis is **REJECTED**. The correlation (r = {results.pearson_r:.3f})
{'does not reach' if abs(results.pearson_r) < 0.5 else 'is not statistically significant at'}
the required threshold (r < -0.5, p < 0.05).

This indicates that CV is **not a valid predictor** of cross-benchmark stability in this dataset.
The MUST_WORK gate failure requires **routing to Phase 0** for fundamental redesign. Alternative
quality signals or different meta-features should be explored."""

    def _generate_next_steps(self, results: AnalysisResults) -> str:
        """Generate next steps based on gate result."""
        if results.gate_passed:
            return """**Gate PASSED** - Proceed to dependent hypotheses:
- H-M1: Mechanism hypothesis (dispersion-driven rank instability)
- H-M2: Mechanism hypothesis (measurement noise amplification)
- H-C1: Robustness condition (minimum sample size for CV validity)"""
        else:
            return """**Gate FAILED** - Route to Phase 0:
- Fundamental redesign required
- Explore alternative quality signals (e.g., score distribution skewness, inter-rater reliability)
- Consider different meta-features for benchmark quality assessment
- Preserve partial results for failure analysis"""
