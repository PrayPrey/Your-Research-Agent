# H-M2 Validation Report

**Date:** 2026-08-10
**Hypothesis:** Benchmarks testing similar error processes exhibit similar uncertainty distributions (JS-divergence < 0.15)
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Executive Summary

**GATE RESULT: PASS**

H-M2 validates that benchmarks sharing error family membership exhibit significantly lower JS-divergence than cross-family pairs. The Mann-Whitney U test confirms that same-family pairs have statistically significantly lower JS-divergence (p < 0.001), with a mean of 0.082 (below the 0.15 threshold).

---

## Results

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mann-Whitney U p-value | 0.0002 | < 0.05 | PASS |
| Same-family mean JS-div | 0.0823 | < 0.15 | PASS |
| Cliff's delta | -1.0 | < -0.5 (large) | PASS |

### Statistical Analysis

**Same-Family Pairs (n=6):**
- Mean: 0.0823 ± 0.0424
- Values: [0.056, 0.041, 0.072, 0.142, 0.139, 0.043]
- All pairs: TriviaQA-NQ, TriviaQA-SQuAD, NQ-SQuAD (Factual Recall) + PopQA-HaluEval, PopQA-FEVER, HaluEval-FEVER (Entity/Claim)

**Cross-Family Pairs (n=9):**
- Mean: 0.4813 ± 0.0527
- Values: [0.422, 0.526, 0.530, 0.388, 0.498, 0.501, 0.418, 0.522, 0.526]
- All Factual-Entity combinations

### Effect Size Interpretation

Cliff's delta = -1.0 indicates **perfect separation**: every same-family JS-divergence value is lower than every cross-family value. This is the strongest possible effect size, demonstrating that the error family structure is not just statistically significant but practically meaningful.

---

## Visualizations

| Figure | Description |
|--------|-------------|
| `figures/boxplot.png` | Box plot comparing same-family vs cross-family distributions |
| `figures/violin.png` | Violin plot with individual data points |
| `figures/heatmap.png` | 6×6 JS-divergence matrix with family boundaries |
| `figures/forest.png` | Cliff's delta effect size with confidence interval |

---

## Gate Decision

### SHOULD_WORK Gate Evaluation

**Condition:** Same-family JS-div < Cross-family (p < 0.05) AND mean same-family < 0.15

**Result:** PASS
- p = 0.0002 < 0.05 ✓
- mean = 0.0823 < 0.15 ✓

### Mechanism Verified

The error family hypothesis is strongly supported:
1. **Factual Recall family** (TriviaQA, NQ, SQuAD): Benchmarks testing knowledge retrieval produce similar entropy distributions
2. **Entity/Claim family** (PopQA, HaluEval, FEVER): Benchmarks testing entity/claim verification produce similar entropy distributions
3. **Cross-family pairs** show 5.8× higher divergence than same-family pairs

---

## Implications for Transfer Learning

This result directly supports the conditional transfer hypothesis:
- Within-family transfer (H-M3) should show low AUROC degradation
- Cross-family transfer (H-M4) should show high AUROC degradation
- The family structure provides a principled basis for predicting transfer success

---

## Files Generated

| File | Description |
|------|-------------|
| `results.json` | Complete statistical results |
| `figures/boxplot.png` | Primary gate visualization |
| `figures/violin.png` | Distribution comparison |
| `figures/heatmap.png` | JS-divergence matrix heatmap |
| `figures/forest.png` | Effect size visualization |

---

## Next Steps

1. **H-M3:** Validate within-cluster threshold transfer (AUROC degradation ≤ 0.08)
2. **H-M4:** Validate cross-cluster threshold transfer (AUROC degradation > 0.15)

---

*Validation completed: 2026-08-10T22:27:21Z*
