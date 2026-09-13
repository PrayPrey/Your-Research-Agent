# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-19T00:00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Ours | Threshold | Gap |
|--------|------|-----------|-----|
| AUC | 0.0 | 0.75 | -0.75 (100%) |

## Experiment Metrics

- background_cv: 0.0393
- bird_type_cv: 0.0360
- auc: 0.0
- best_f1: 0.6667

## Root Cause Analysis

- CV probe computation yielded near-zero coefficients of variation
- AUC calculation resulted in 0.0, indicating mechanism not detecting spurious features
- CLIP features may not encode spurious correlation signals as expected

## Lessons Learned

1. CV-based spurious correlation detection requires features that actually vary with spurious attributes
2. CLIP embeddings may not preserve fine-grained spurious correlation signals (background type)
3. Need different feature extraction or probing methodology

---
*For cross-phase reference*
*Written at: 2026-08-19*