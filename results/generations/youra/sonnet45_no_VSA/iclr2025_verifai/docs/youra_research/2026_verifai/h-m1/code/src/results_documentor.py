"""Results Documentation Module - Generate validation report"""

from pathlib import Path
from typing import Dict
from datetime import datetime

from .ablation_experiment import AblationResults
from .statistical_analyzer import GateDecision, MonotonicTest, GapTest, RegressionResult


class ResultsDocumentor:
    """Generate comprehensive validation report"""

    def __init__(self, hypothesis_folder: str):
        self.hypothesis_folder = Path(hypothesis_folder)

    def generate_validation_report(
        self,
        ablation_results: AblationResults,
        stats: Dict,
        gate_decision: GateDecision
    ) -> str:
        """Generate 04_validation.md content"""

        monotonic: MonotonicTest = stats['monotonic_test']
        gaps: GapTest = stats['gap_test']
        regression: RegressionResult = stats['regression']

        report = f"""# Validation Report: H-M1 Information Gradient Hypothesis

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate Type:** MUST_WORK

---

## Executive Summary

**Gate Status:** {gate_decision.status}
**Reason:** {gate_decision.reason}

**Passing Tests:** {', '.join(gate_decision.passing_tests) if gate_decision.passing_tests else 'None'}
**Failing Tests:** {', '.join(gate_decision.failing_tests) if gate_decision.failing_tests else 'None'}

---

## Experiment Configuration

### Dataset
- **Source:** ACSL-by-Example benchmark
- **Programs Tested:** {len(set(t.program_id for t in ablation_results.raw_trials))}
- **Total Trials:** {len(ablation_results.raw_trials)}

### Feedback Conditions
1. **RawError:** Unstructured Frama-C output
2. **TagOnly:** Structure dimension only
3. **ObligationSlice:** Structure + Dependency dimensions
4. **FullStructured:** All 3 dimensions (Witness + Structure + Dependency)

### LLM Configuration
- **Model:** Claude Opus 4.5
- **Temperature:** 0.7
- **Max Iterations:** 10 per program

---

## Per-Condition Statistics

"""

        for condition_name in ['RawError', 'TagOnly', 'ObligationSlice', 'FullStructured']:
            if condition_name in ablation_results.results_by_condition:
                cond_results = ablation_results.results_by_condition[condition_name]
                report += f"""### {condition_name}

- **Mean Discharge Rate:** {cond_results.mean_rate:.2f}%
- **Std Deviation:** {cond_results.std_rate:.2f}%
- **Mean Iterations:** {cond_results.mean_iterations:.1f}
- **Total API Calls:** {cond_results.total_compute['api_calls']}

"""

        report += f"""---

## Hypothesis Test Results

### Test 1: Monotonic Ordering

**Status:** {'PASS' if monotonic.passed else 'FAIL'}

**Expected Ordering:** {' > '.join(monotonic.expected)}
**Actual Ordering:** {' > '.join(monotonic.ordering)}

"""
        if monotonic.violations:
            report += f"**Violations:**\n"
            for v in monotonic.violations:
                report += f"- {v}\n"
        else:
            report += "**Violations:** None\n"

        report += f"""
### Test 2: Adjacent Gaps

**Status:** {'PASS' if gaps.passed else 'FAIL'}
**Threshold:** {gaps.threshold} percentage points

**Gaps:**
"""
        for gap_name, gap_value in gaps.gaps.items():
            status = '✓' if gap_value >= gaps.threshold else '✗'
            report += f"- {gap_name}: {gap_value:.2f}pp {status}\n"

        if gaps.failed_gaps:
            report += f"\n**Failed Gaps:** {', '.join(gaps.failed_gaps)}\n"
        else:
            report += "\n**Failed Gaps:** None\n"

        report += f"""
### Test 3: Regression Analysis

**Status:** {'PASS' if regression.significant else 'FAIL'}

- **Coefficient (β):** {regression.coefficient:.4f}
- **P-value:** {regression.p_value:.6f}
- **R-squared:** {regression.r_squared:.4f}
- **Significance Level:** 0.05

**Interpretation:** {'Significant positive correlation between feedback richness and discharge rate' if regression.significant else 'No significant correlation detected'}

---

## Visualizations

All figures are available in `figures/` directory:

1. **gate_metrics_comparison.png** - Required gate plot showing target vs actual metrics
2. **monotonic_ordering.png** - Line plot with confidence intervals
3. **per_program_heatmap.png** - Program × Condition performance matrix
4. **regression_plot.png** - Feedback richness vs. discharge rate with regression line

---

## Gate Decision

**Status:** {gate_decision.status}

**Rationale:**
{gate_decision.reason}

**Test Summary:**
- Monotonic Ordering: {'PASS' if monotonic.passed else 'FAIL'}
- Adjacent Gaps: {'PASS' if gaps.passed else 'FAIL'}
- Regression Significance: {'PASS' if regression.significant else 'FAIL'}

**Conclusion:**
"""
        if gate_decision.status == "SATISFIED":
            report += """The information gradient hypothesis is VALIDATED. Proof discharge rate scales monotonically with feedback richness, with all three hypothesis tests passing. This confirms that structured verifier feedback provides a causal mechanism for improved specification synthesis.
"""
        else:
            report += f"""The information gradient hypothesis is NOT VALIDATED. {gate_decision.reason}. This suggests that either (1) the feedback dimensions tested do not capture the critical information content, or (2) the LLM cannot effectively utilize incremental feedback richness.
"""

        report += """
---

## Appendix: Raw Trial Data

"""
        report += f"Total trials: {len(ablation_results.raw_trials)}\n\n"
        report += "Sample trials (first 10):\n\n"
        report += "| Program | Condition | Discharge Rate | Iterations |\n"
        report += "|---------|-----------|----------------|------------|\n"

        for trial in ablation_results.raw_trials[:10]:
            report += f"| {trial.program_id} | {trial.condition} | {trial.discharge_rate:.2f}% | {trial.iterations} |\n"

        report += "\n... (see results/trials/ for complete data)\n"

        report += f"""
---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Validation Status:** {'COMPLETED' if gate_decision.status in ['SATISFIED', 'FAILED'] else 'IN_PROGRESS'}
"""

        return report

    def save_validation_report(self, report_content: str, output_path: str):
        """Save validation report to file"""
        output_file = self.hypothesis_folder / output_path
        with output_file.open('w') as f:
            f.write(report_content)
        print(f"\nValidation report saved to: {output_file}")
