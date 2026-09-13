# H-C1 Validation Report

## Summary Statistics
- **Sample Size**: 32
- **Mean**: 10.3
- **Std Dev**: 3.8
- **CV**: 0.36 (36%)
- **Median**: 10.0
- **IQR**: 6.0
- **95% CI for Mean**: [8.9, 11.6]

## Budget Recommendation
- **Budget**: 15 tactic evaluations
- **Estimator**: mean+1σ
- **Coverage**: 90.6% of baseline solves

## Gate Decision
- **Criterion**: CV ≤ 1.0
- **Observed CV**: 0.36
- **Result**: PASS

## Interpretation
CV=0.36 ≤ 1.0, tactic budget feasible

## Downstream Implications
- Apply budget=15 to H-M1/M2/M3 LeanCopilot runs for fair comparison
- Report both raw and budget-constrained success rates in Phase 5
- Tactic count is a reliable fairness metric (CV < 100%)

## Sensitivity Analysis

| Budget | Coverage | Interpretation |
|--------|----------|----------------|
| 10 | 0.0% | Mean only (restrictive) |
| 15 | 90.6% | Recommended (balanced) |
| 20 | 100.0% | Permissive (captures outliers) |

## Validation Metadata
- **Data Source**: H-E1 baseline results
- **Analysis Date**: 2026-08-20
- **Script**: analyze_tactic_budget.py
- **Hypothesis**: h-c1 (CONDITION gate)
