# Phase 4 Validation Report — H-E1

**Generated:** 2026-04-30T11:21:53.127614
**Gate Type:** MUST_WORK
**Gate Result:** **PASS**

## Gate Evaluation

| Pair | Partial ρ | BCa CI 95% | Passes |
|------|-----------|------------|--------|
| ECE vs TruthfulQA_pct | -0.758 | [-0.894, -0.504] | ✓ |
| ECE vs AdvGLUE_drop | -0.718 | [-0.890, -0.380] | ✓ |

## Partial Spearman Correlation Matrix (Top 5 by |ρ|)

| x | y | ρ | CI low | CI high | p-value |
|---|---|---|--------|---------|---------|
| ECE | TruthfulQA_pct | -0.758 | -0.894 | -0.504 | 0.0000 |
| Brier | TruthfulQA_pct | -0.738 | -0.894 | -0.460 | 0.0000 |
| ECE | Brier | 0.723 | 0.325 | 0.899 | 0.0000 |
| ECE | AdvGLUE_drop | -0.718 | -0.890 | -0.380 | 0.0000 |
| ECE | ANLI_drop | -0.667 | -0.821 | -0.407 | 0.0001 |

## Factor Analysis

- KMO adequacy: 0.879
- Variance explained (Factor 1): 72.1%
- Tucker's congruence (greedy vs T=0.7): 1.000
  - Threshold: ≥ 0.85 → ✓ PASS

## LOO Logistic Regression (AUC)

- Composite AUC: N/A
- MMLU-only AUC: N/A

## Summary

The MUST_WORK gate for H-E1 has **PASSED**.

The experiment verified whether partial Spearman correlations between epistemic
reliability metrics (ECE, TruthfulQA%, AdvGLUE drop) exceed the |ρ| ≥ 0.40 threshold
with BCa 95% CIs excluding zero.