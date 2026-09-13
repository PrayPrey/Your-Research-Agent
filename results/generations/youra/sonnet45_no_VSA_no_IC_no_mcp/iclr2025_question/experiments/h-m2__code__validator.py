"""Validation report writer."""

from pathlib import Path


class ValidationWriter:
    """Generate 04_validation.md report."""

    def __init__(self, output_path: str):
        """Initialize with output path."""
        self.output_path = Path(output_path)

    def write_results(self, sample_size: int, mean_reduction: float, p_value: float,
                     t_stat: float, dof: int, result: str,
                     mean_error_g1: float, mean_error_g2: float):
        """Write validation report to 04_validation.md."""
        report = f"""# Validation Report: H-M2 Bayesian Gate 2 Posterior Prediction

**Date:** 2026-08-25
**Hypothesis:** H-M2 (MECHANISM)
**Status:** {result}

---

## Hypothesis Statement

Under hypotheses that reach Gate 2 (100 samples), if we apply Bayesian updates combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full), then posterior prediction error will be >40% lower than Gate 1 prior error, because Bayesian inference reduces uncertainty by incorporating new evidence.

---

## Results Summary

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean Error Reduction | {mean_reduction:.2f}% | >40% | {'✓ PASS' if mean_reduction > 40 else '✗ FAIL'} |
| p-value (Paired t-test) | {p_value:.4f} | <0.05 | {'✓ PASS' if p_value < 0.05 else '✗ FAIL'} |

### Sample Statistics

- **Sample size:** {sample_size} hypotheses with Gate 2 data
- **Gate 1 mean error:** {mean_error_g1:.4f}
- **Gate 2 mean error:** {mean_error_g2:.4f}

### Statistical Analysis

- **Paired t-test:** t={t_stat:.3f}, p={p_value:.4f}, dof={dof}
- **Null hypothesis:** No difference between Gate 1 and Gate 2 errors
- **Result:** {'Rejected (significant improvement)' if p_value < 0.05 else 'Failed to reject (no significant improvement)'}

---

## Gate Verdict

**Gate Type:** SHOULD_WORK
**Result:** {result}

### Rationale

{'All thresholds met: mean error reduction exceeds 40% target and paired t-test shows statistical significance (p<0.05). Bayesian updates validated.' if result == 'PASS' else 'Modest improvement but below 40% target. Framework remains functional with Gate 1 only.' if result == 'PARTIAL' else 'Bayesian updates do not provide significant improvement. Use Gate 1 only.'}

---

## Artifacts

- `error_reduction_histogram.png`: Distribution of per-hypothesis error reduction
- `gate_comparison_scatter.png`: O_pred vs O_full for both gates
- `paired_errors.png`: Paired error comparison with connecting lines
- `statistical_comparison_boxplot.png`: Box plot with p-value annotation
- `metrics_comparison.png`: Target vs actual metrics bar chart (MANDATORY)

---

## Statistical Methods

- **Bayesian Inference:** scipy.stats Gaussian conjugate update
- **Error Computation:** Relative error (|pred - truth| / truth)
- **Statistical Test:** scipy.stats.ttest_rel (paired t-test, two-tailed)
- **Success Criteria:** Error reduction >40% AND p<0.05

---

## Conclusion

{'Gate 2 Bayesian updates successfully reduce prediction error by incorporating 100-sample measurements. Framework gains incremental refinement capability.' if result == 'PASS' else 'Gate 2 provides modest improvement but does not meet >40% threshold. Framework remains effective with Gate 1 linear extrapolation only.' if result == 'PARTIAL' else 'Gate 2 does not provide significant improvement over Gate 1. Framework will use Gate 1 linear extrapolation only.'}
"""
        self.output_path.write_text(report)
