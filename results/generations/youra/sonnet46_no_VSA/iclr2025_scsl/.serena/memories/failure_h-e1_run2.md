# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-04T01:00:00+00:00
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** SIGNAL_INVERTED

## Performance Gap

| Metric | Ours | Threshold | Gap |
|--------|------|-----------|-----|
| AUROC | 0.2828 | 0.80 | -0.5172 (-64.7%) |
| Inverted AUROC (1-CV) | ~0.72 | 0.80 | -0.08 |

## Root Cause Analysis

- CV across B=20 SGD micro-steps at epoch t*=1 is INVERTED for Waterbirds + pretrained ResNet50
- Majority samples (landbird-on-land, group 0, 73% of data) have 2.24× HIGHER gradient CV than minority at epoch 1
- Pretrained initialization causes gradient CV to reflect dataset imbalance adaptation, not memorization difficulty
- Epoch 1 gradient dynamics dominated by class imbalance correction, not sample difficulty signal
- minority_mean_cv=0.5355 < majority_mean_cv=1.1981 — opposite of hypothesis prediction

## Lessons Learned

1. Gradient norm CV across consecutive SGD mini-steps at early epochs reflects imbalance adaptation, not minority membership
2. Pretrained backbone (IMAGENET1K_V1) initialization fundamentally changes gradient dynamics at t*=1
3. AUROC ≈ 0.72 for INVERTED signal (1-CV) — signal is real and group-informative, but directionally wrong
4. Infrastructure (dataset.py, model.py, vmap+grad pipeline) is correct and validated — reusable for future hypotheses
5. vmap+grad over direct FC linear computation (feat @ fc_weight.T + fc_bias) is more reliable than functional_call
6. Minority groups 1+2 have only 240/4795 = 5.0% of training data — AUROC estimates have high variance

## Feedback for Next Phase (Phase 0 Re-route)

### Suggested Modifications
- Test gradient signals at multiple epochs (1, 10, 40) — epoch 1 is dominated by imbalance
- Consider gradient magnitude (not variability) as primary signal — consistent with PGD methodology
- Explore loss-based signals (e.g., per-sample loss trajectory) instead of gradient CV
- Consider using inverted CV signal (1 - CV) with adjusted threshold
- Investigate later training epochs where memorization effects dominate over imbalance

### What NOT To Do
- Do not use CV across mini-steps at epoch 1 for Waterbirds + pretrained ResNet50 — validated inverted
- Do not use functional_call inside vmap context — causes model routing issues

### What Showed Promise
- vmap+grad over direct FC linear computation: efficient, numerically stable
- WaterbirdsDataset with derived group labels (group = 2*y + place): correct for WILDS format
- End-to-end gradient pipeline infrastructure: fully functional, all 16 unit tests pass
- Gradient CV IS group-informative (systematic, not random) — signal exists but in wrong direction

---
*Routing: ROUTED_TO_PHASE_0 — fundamental signal inversion requires hypothesis redesign*
*Written at: 2026-08-04T01:00:00+00:00*
