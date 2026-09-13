# Phase 4 Validation Report: h-c2

**Date:** 2026-08-09
**Hypothesis:** The metadata-variance effect persists within RandomForest-only analysis, ruling out algorithm mix confound
**Type:** CONDITION (Permutation Control)
**Gate:** SHOULD_WORK

---

## Executive Summary

**GATE VERDICT: PASS**

The permutation test confirms that the metadata-variance correlation observed in h-e1 persists within the RandomForest-only subset. The true coefficient is more extreme than all 1000 permuted coefficients, with p-value < 0.001.

---

## Experiment Results

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| True coefficient (β_metadata) | -0.00995 | — | — |
| P-value | 0.000 | < 0.05 | ✓ |
| Percentile rank | 0.0% | < 2.5% or > 97.5% | ✓ |
| Effect ratio (95th pctl / true) | 0.168 | Informational | — |

### Interpretation

- **True coefficient = -0.00995**: Higher metadata completeness → lower IQR (reproducibility variance) within RandomForest runs
- **Percentile rank = 0%**: The true coefficient is more negative than ALL 1000 permuted coefficients
- **P-value = 0.000**: Zero permutations produced a coefficient as extreme as the true value (two-sided test)
- **Effect ratio = 0.168**: The 95th percentile of |permuted coefficients| is ~17% of the true |coefficient|, meaning permuted effects are much smaller

---

## Dataset

- **Source:** h-e1/code/data/processed/analysis.parquet
- **Filter:** algo_family == "RandomForest"
- **Sample size:** 165 runs across 133 datasets
- **Permutations:** 1000 (seed=42)

---

## Statistical Analysis

The permutation test shuffled `metadata_score` values 1000 times, refitting the mixed-effects regression each time:

```
iqr ~ metadata_score + stability + log_popularity
groups = dataset_id (random intercept)
```

The true coefficient lies entirely outside the permutation distribution (0th percentile), confirming the correlation is not due to chance.

---

## Artifacts

- **Code:** h-c2/code/
- **Results:** h-c2/code/results/h_c2_permutation.json
- **Figures:**
  - h-c2/code/figures/permutation_histogram.png
  - h-c2/code/figures/effect_comparison.png

---

## Conclusion

The metadata-variance effect holds within the RandomForest-only subset. This rules out algorithm family mix as a confounding explanation for the h-e1 correlation. The SHOULD_WORK gate is satisfied.

---

## State Update

```yaml
h-c2:
  validation:
    status: COMPLETED
    result: PASS
    key_findings:
      - "True coefficient: -0.00995 (more extreme than all permutations)"
      - "P-value: 0.000 (highly significant)"
      - "Percentile rank: 0% (true < all permuted)"
      - "Effect persists within RandomForest-only analysis"
  gate:
    satisfied: true
  completed: true
  completed_at: "2026-08-09T06:02:00Z"
```
