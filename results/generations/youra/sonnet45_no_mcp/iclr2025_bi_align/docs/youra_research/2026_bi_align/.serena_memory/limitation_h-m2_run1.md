# Limitation Record: h-m2 (Run 1)

**Date:** 2026-04-19T16:50:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

RoBERTa-base embeddings insufficient for alignment structure detection. Cohen's d=0.034 (93% below threshold of 0.5), indicating no statistically significant clustering of chosen vs rejected responses in pretrained semantic embedding space.

## Failed Checks

- Primary gate: Cohen's d ≥ 0.5 (actual: 0.034)
- Secondary gate: Cohen's d > 0.3 (actual: 0.034)
- Statistical significance: p < 0.05 (actual p=0.797)

## Partial Results

| Metric | Value |
|--------|-------|
| cohens_d | 0.034 |
| baseline_d_mean | 0.004 |
| p_value | 0.797 |
| pca_variance_2d | 0.349 |
| n_samples | 160800 |

## Experiment Summary

Extracted 768-dimensional RoBERTa-base CLS token embeddings from 160,800 HH-RLHF chosen/rejected response pairs. MANOVA analysis revealed minimal group separation (Cohen's d=0.034), only marginally above random baseline (d=0.004). Effect size is 93% below SHOULD_WORK threshold (0.5), indicating standard pretrained encoders do not capture geometric structure of alignment failures.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial
3. Alternative approaches that might avoid this limitation

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-04-19T16:50:00+00:00*
*For cross-phase reference*
