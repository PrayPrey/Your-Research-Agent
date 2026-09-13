"""Validation report writer."""

from pathlib import Path
from typing import Dict


class ValidationWriter:
    """Write 04_validation.md report."""

    def __init__(self, output_path: str):
        """Initialize with output file path."""
        self.output_path = Path(output_path)

    def write_results(
        self,
        r: float,
        p: float,
        k: float,
        r2: float,
        cv: float,
        k_by_type: Dict[str, float],
        passed: bool
    ):
        """Write validation report with all metrics."""

        content = f"""# Validation Report: H-M1 Correlation Analysis

**Date:** 2026-08-25
**Hypothesis:** H-M1 (MECHANISM)
**Status:** {"PASS" if passed else "FAIL"}

---

## Hypothesis Statement

Under retrospective validation using the corpus from H-E1, if we measure correlation between 10-sample overhead (O_10) and full-dataset overhead (O_full), then correlation r will exceed 0.7, because overhead operations scale predictably across sample sizes.

---

## Results Summary

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Pearson r | {r:.3f} | >0.7 | {"✓ PASS" if r > 0.7 else "✗ FAIL"} |
| p-value | {p:.4f} | <0.05 | {"✓ PASS" if p < 0.05 else "✗ FAIL"} |
| R² | {r2:.3f} | >0.5 | {"✓ PASS" if r2 > 0.5 else "✗ FAIL"} |

### Secondary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Scaling CV | {cv:.2%} | <30% | {"✓ PASS" if cv < 0.3 else "✗ FAIL"} |

### Global Scaling Factor

- **k = {k:.3f}** (O_full ≈ {k:.2f} × O_10)

---

## Per-Type Scaling Factors

| Type | k | R² | Interpretation |
|------|---|----|-----------------|
"""

        for hyp_type in sorted(k_by_type.keys()):
            k_val = k_by_type[hyp_type]
            content += f"| {hyp_type} | {k_val:.3f} | - | "
            if abs(k_val - k) / k < 0.1:
                content += "Consistent with global k |\n"
            else:
                content += f"Deviates {abs(k_val - k) / k:.1%} from global |\n"

        content += f"""
**CV across types:** {cv:.2%} ({"consistent" if cv < 0.3 else "high variance"})

---

## Gate Verdict

**Gate Type:** MUST_WORK
**Result:** {"PASS" if passed else "FAIL"}

### Rationale

"""

        if passed:
            content += f"""All thresholds met:
- Pearson correlation r={r:.3f} exceeds 0.7 threshold
- Statistical significance p={p:.4f} < 0.05
- Scaling CV={cv:.2%} < 30% shows consistent scaling across hypothesis types
- Linear model explains {r2*100:.1f}% of variance (R²={r2:.3f})

**Conclusion:** Micro-pilot overhead (10-sample) reliably predicts full-scale overhead with scaling factor k≈{k:.2f}. Gate 1 extrapolation is validated.
"""
        else:
            failures = []
            if r <= 0.7:
                failures.append(f"r={r:.3f} ≤ 0.7")
            if p >= 0.05:
                failures.append(f"p={p:.4f} ≥ 0.05 (not significant)")
            if cv >= 0.3:
                failures.append(f"CV={cv:.2%} ≥ 30% (inconsistent scaling)")
            if r2 < 0.5:
                failures.append(f"R²={r2:.3f} < 0.5 (poor fit)")

            content += "Failed thresholds:\n"
            for failure in failures:
                content += f"- {failure}\n"

            if 0.5 <= r < 0.7:
                content += "\n**Recommendation:** Moderate correlation detected. Explore non-linear models in Phase 5.\n"
            elif r < 0.5:
                content += "\n**Recommendation:** Low correlation. Consider abandoning linear extrapolation assumption.\n"

        content += """
---

## Artifacts

- `correlation_scatter.png`: O_10 vs O_full scatter plot with regression line
- `scaling_factors.png`: Per-type scaling factors bar chart
- `residuals.png`: Residual plot for linearity validation

---

## Statistical Methods

- **Pearson Correlation:** scipy.stats.pearsonr (two-tailed test)
- **Linear Regression:** sklearn.linear_model.LinearRegression (OLS)
- **Goodness of Fit:** sklearn.metrics.r2_score
- **Coefficient of Variation:** std(k_values) / mean(k_values)
"""

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write(content)

        print(f"Validation report written to: {self.output_path}")
