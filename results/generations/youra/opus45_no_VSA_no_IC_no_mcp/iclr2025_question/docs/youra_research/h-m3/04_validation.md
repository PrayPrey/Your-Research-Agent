# H-M3 Validation Report: Orthogonal Signals Enable Complementary Detection

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Validation Date:** 2026-08-28

---

## Executive Summary

**Gate Result: PASS**

Token entropy (H-M1) and n-sample consistency (H-M2) capture orthogonal uncertainty signals. Low correlation (r = 0.228 < 0.3) confirms they measure different aspects of model uncertainty. Discordant cases (18.1% > 15%) show each method achieves high AUROC on its "winning" subset, demonstrating complementary predictive value.

---

## Success Criteria Evaluation

### Primary Criterion: Low Correlation

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| Pearson r | < 0.3 | 0.228 | **PASS** |
| Spearman ρ | < 0.3 | 0.241 | PASS |

Both correlation measures well below threshold. p-values highly significant (< 10^-10), confirming the measured correlation is reliable but weak.

### Secondary Criterion: Differential Predictive Value

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| Discordant proportion | > 15% | 18.1% | **PASS** |
| Entropy subset AUROC | > 0.6 | 0.764 | **PASS** |
| Consistency subset AUROC | > 0.6 | 0.797 | **PASS** |

- **Discordant cases:** 148 questions (18.1%) where entropy and consistency rankings differ by >50 percentile points
- **High-entropy-only:** 76 questions where entropy flags high uncertainty but consistency doesn't
- **High-inconsistency-only:** 72 questions where consistency flags instability but entropy doesn't

Each method achieves strong predictive performance on the subset where it uniquely detects problems.

---

## Detailed Results

### Correlation Analysis

```
Pearson r:  0.228 (p = 4.11e-11)
Spearman ρ: 0.241 (p = 3.18e-12)
```

Interpretation: ~5% shared variance. 95% of each signal's variance is independent.

### Discordant Case Breakdown

| Category | Count | Proportion |
|----------|-------|------------|
| Total discordant | 148 | 18.1% |
| High-entropy-only | 76 | 9.3% |
| High-inconsistency-only | 72 | 8.8% |
| Concordant | 669 | 81.9% |

### Subset AUROC Analysis

| Subset | AUROC | N | Interpretation |
|--------|-------|---|----------------|
| High-entropy-only | 0.764 | 76 | Entropy predicts well where consistency misses |
| High-inconsistency-only | 0.797 | 72 | Consistency predicts well where entropy misses |

Both >0.6 threshold with comfortable margin, confirming complementary detection capability.

---

## Visualizations

- `results/figures/scatter_entropy_consistency.png` — Scatter plot showing weak linear relationship
- `results/figures/quadrant_analysis.png` — Quadrant breakdown by median splits

---

## Implementation Files

| File | Purpose |
|------|---------|
| `orthogonality.py` | Main analysis script |
| `config.yaml` | Configuration (thresholds, paths) |
| `results/correlation_analysis.json` | Full results |
| `results/subset_auroc.json` | AUROC per subset |
| `results/discordant_cases.csv` | Per-question discordant flags |

---

## Conclusion

**H-M3 PASS** — Entropy and consistency signals are orthogonal (r = 0.228 < 0.3) with complementary predictive value. Each method captures unique failure modes:
- Entropy detects epistemic uncertainty (diffuse logit distribution)
- Consistency detects generation instability (variable sampling)

This validates the premise for combining both signals in a multi-signal hallucination detection approach.

---

**Key Findings:**
1. r = 0.228 (well below 0.3 threshold)
2. 18.1% discordant cases (>15% threshold)
3. Entropy subset AUROC = 0.764, Consistency subset AUROC = 0.797 (both >0.6)
4. Signals capture orthogonal failure modes suitable for ensemble combination
