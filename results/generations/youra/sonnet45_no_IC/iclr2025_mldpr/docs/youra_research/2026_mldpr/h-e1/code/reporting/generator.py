"""
E1-4: Visualization Module - ReportGenerator
Implements visualization generation for validation report (5 figures).
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List


class ReportGenerator:
    """
    Generate visualizations and validation reports.

    Features:
    - 5 required figures (gate metric, reproduction histogram, domain pie, timeline, power)
    - Conditional coloring (pass=green, fail=red)
    - Markdown report generation with embedded figures
    """

    def __init__(self, output_dir: str, dpi: int = 300):
        """
        Initialize generator.

        Args:
            output_dir: Output directory for figures
            dpi: Figure resolution
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def generate_gate_metric_chart(self, threshold: int, actual: int, passes: bool) -> str:
        """
        Generate gate metric comparison bar chart.

        Args:
            threshold: Gate threshold value
            actual: Actual benchmark count
            passes: Whether gate passed

        Returns:
            Figure file path
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Threshold', 'Actual Count']
        values = [threshold, actual]
        colors = ['gray', 'green' if passes else 'red']

        ax.bar(categories, values, color=colors, alpha=0.7)
        ax.set_ylabel('Benchmark Count', fontsize=12)
        ax.set_title('Gate Metric: Benchmark Count Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, (cat, val) in enumerate(zip(categories, values)):
            ax.text(i, val + 5, str(val), ha='center', fontsize=12, fontweight='bold')

        plt.tight_layout()

        output_path = self.output_dir / "gate_metric_comparison.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return str(output_path)

    def generate_reproduction_histogram(self, df: pd.DataFrame) -> str:
        """
        Generate reproduction depth distribution histogram.

        Args:
            df: Benchmark DataFrame with 'result_count' column

        Returns:
            Figure file path
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Create bins (ensure max bin is above data max)
        max_val = df['result_count'].max()
        bins = [5, 10, 20, 50, max(51, max_val + 1)]
        labels = ['5-10', '11-20', '21-50', '50+']

        df_copy = df.copy()
        df_copy['bin'] = pd.cut(df_copy['result_count'], bins=bins, labels=labels, right=False)
        bin_counts = df_copy['bin'].value_counts().reindex(labels, fill_value=0)

        ax.bar(labels, bin_counts.values, color='#3498db', alpha=0.7)
        ax.set_xlabel('Reproduction Count Range', fontsize=12)
        ax.set_ylabel('Frequency (Benchmark Count)', fontsize=12)
        ax.set_title('Reproduction Depth Distribution', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, val in enumerate(bin_counts.values):
            ax.text(i, val + 1, str(val), ha='center', fontsize=10)

        plt.tight_layout()

        output_path = self.output_dir / "reproduction_depth_histogram.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return str(output_path)

    def generate_domain_pie_chart(self, domain_counts: Dict[str, int]) -> str:
        """
        Generate domain coverage pie chart.

        Args:
            domain_counts: Dict mapping domain to count

        Returns:
            Figure file path
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        labels = list(domain_counts.keys())
        sizes = list(domain_counts.values())

        # Use distinct colors
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title('Domain Coverage Distribution', fontsize=14, fontweight='bold')
        ax.axis('equal')

        plt.tight_layout()

        output_path = self.output_dir / "domain_coverage_pie.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return str(output_path)

    def generate_timeline_chart(self, df: pd.DataFrame) -> str:
        """
        Generate timeline distribution line chart.

        Args:
            df: Benchmark DataFrame with 'publication_year' column

        Returns:
            Figure file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        year_counts = df['publication_year'].value_counts().sort_index()
        years = year_counts.index
        counts = year_counts.values

        ax.plot(years, counts, marker='o', linewidth=2, markersize=8, color='#2ecc71')
        ax.fill_between(years, counts, alpha=0.3, color='#2ecc71')

        ax.set_xlabel('Publication Year', fontsize=12)
        ax.set_ylabel('Benchmark Count', fontsize=12)
        ax.set_title('Timeline Distribution (2019-2024)', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / "timeline_distribution.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return str(output_path)

    def generate_power_chart(self, required_n: int, actual_n: int) -> str:
        """
        Generate power analysis bar chart.

        Args:
            required_n: Required sample size
            actual_n: Actual sample size

        Returns:
            Figure file path
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ['Required N\n(80% power)', 'Actual N']
        values = [required_n, actual_n]
        colors = ['gray', 'green' if actual_n >= required_n else 'orange']

        bars = ax.barh(categories, values, color=colors, alpha=0.7)
        ax.set_xlabel('Sample Size', fontsize=12)
        ax.set_title('Power Analysis: Sample Size Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (cat, val) in enumerate(zip(categories, values)):
            ax.text(val + 5, i, str(val), va='center', fontsize=12, fontweight='bold')

        plt.tight_layout()

        output_path = self.output_dir / "power_analysis.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return str(output_path)

    def generate_validation_report(
        self,
        validation_result: Dict,
        power_result: Dict,
        domain_result: Dict,
        depth_result: Dict,
        figure_paths: Dict[str, str]
    ) -> str:
        """
        Generate markdown validation report with embedded figures.

        Args:
            validation_result: Hypothesis validation results
            power_result: Power analysis results
            domain_result: Domain coverage results
            depth_result: Reproduction depth results
            figure_paths: Dict mapping figure name to file path

        Returns:
            Report content as string
        """
        gate_status = validation_result['status']

        # Format status badges
        status_badge = '✅ PASS' if gate_status == 'PASS' else '❌ FAIL'
        power_badge = '✅ Yes' if power_result['power_sufficient'] else '❌ No'
        coverage_badge = '✅ Yes' if domain_result['sufficient_coverage'] else '❌ No'

        # Executive summary text
        if gate_status == 'PASS':
            exec_summary = 'The Papers with Code benchmark database contains sufficient samples for a reproducibility meta-analysis. This hypothesis **PASSED** the MUST_WORK gate.'
        else:
            exec_summary = 'The Papers with Code benchmark database does NOT contain sufficient samples. This hypothesis **FAILED** the MUST_WORK gate. Study is INFEASIBLE.'

        # Conclusion text
        if gate_status == 'PASS':
            next_steps = """**Next Steps:**
- Proceed to Phase 5 (Baseline Comparison)
- Use these benchmarks for reproducibility meta-analysis
- Validated hypothesis supports main research question"""
        else:
            next_steps = """**Next Steps:**
- ABANDON study (infeasible per Phase 2B gate logic)
- Consider alternative: Qualitative case study with available benchmarks
- OR Pivot: Relax inclusion criteria (e.g., ≥3 results instead of ≥5)"""

        current_date = pd.Timestamp.now().strftime('%Y-%m-%d')

        report = f"""# Validation Report: H-E1 Benchmark Data Validation

**Date:** {current_date}
**Hypothesis:** Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each
**Gate Type:** MUST_WORK
**Gate Result:** **{gate_status}**

---

## Executive Summary

**Primary Metric:** Benchmark Count
- **Threshold:** {validation_result['threshold']}
- **Actual Count:** {validation_result['total_benchmarks']}
- **Status:** {status_badge}

{exec_summary}

---

## Data Collection Results

**API Query Summary:**
- Endpoint: Papers with Code REST API (https://paperswithcode.com/api/v1/)
- Task Filter: Classification
- Time Range: 2019-2024
- Inclusion Criteria: ≥5 independent results per benchmark

**Collection Status:** ✅ Completed

---

## Primary Metrics

### 1. Benchmark Count
![Gate Metric Comparison](figures/gate_metric_comparison.png)

**Result:** {validation_result['total_benchmarks']} benchmarks (threshold: {validation_result['threshold']})

### 2. Statistical Power
![Power Analysis](figures/power_analysis.png)

**Power Analysis Results:**
- Effect Size (Cohen's d): {power_result['effect_size']}
- Required N (80% power): {power_result['required_n']}
- Actual N: {power_result['actual_n']}
- Power Sufficient: {power_badge}

---

## Secondary Metrics

### 3. Domain Coverage
![Domain Coverage](figures/domain_coverage_pie.png)

**Coverage Results:**
- Unique Domains: {domain_result['domain_count']}
- Sufficient Coverage (≥2 domains): {coverage_badge}

**Distribution:**
{self._format_distribution(domain_result['distribution'])}

### 4. Reproduction Depth
![Reproduction Depth](figures/reproduction_depth_histogram.png)

**Depth Statistics:**
- Median: {depth_result['median']}
- Mean: {depth_result['mean']:.2f}
- Std: {depth_result['std']:.2f}
- Range: [{depth_result['min']}, {depth_result['max']}]

### 5. Timeline Distribution
![Timeline](figures/timeline_distribution.png)

---

## Conclusion

**Gate Decision:** {gate_status}

{next_steps}

---

*Generated by YouRA Phase 4: PoC Implementation & Validation*
*Experiment Type: EXISTENCE (API-based data validation)*
"""

        return report

    def _format_distribution(self, distribution: Dict[str, int]) -> str:
        """Format distribution dict as markdown list."""
        lines = []
        for domain, count in list(distribution.items())[:10]:
            lines.append(f"- {domain}: {count}")
        if len(distribution) > 10:
            lines.append(f"- ... ({len(distribution) - 10} more)")
        return '\n'.join(lines)
