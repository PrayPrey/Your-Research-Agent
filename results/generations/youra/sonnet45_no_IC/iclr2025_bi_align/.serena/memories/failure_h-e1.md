# H-E1 Hypothesis Failure Record

**Date:** 2026-07-12  
**Hypothesis:** H-E1 (EXISTENCE)  
**Status:** FAILED  
**Gate Type:** MUST_WORK  
**Gate Result:** FAIL

## Hypothesis Statement

Under HH-RLHF multi-turn conversation settings, if we train a self-supervised model on interaction features (turn count, lexical diversity, follow-up rate) from high-reward conversations, then it will predict user engagement with AUC ≥0.65 on held-out data.

## Failure Summary

**Test AUC:** 0.4953 (threshold: 0.65)  
**Gate Status:** FAILED  
**Failure Reason:** Features lack predictive signal - model performs worse than random baseline

### Key Findings

1. Model Performance: AUC=0.4953 < random (0.5026) < heuristic (0.5085)
2. Training Dynamics: Severe overfitting (train loss → 0.0018, val AUC flat ~0.50)
3. Stratified Evaluation: No engagement signal (high/low reward both AUC=0.50)

## Root Cause

Synthetic data limitation - used locally-generated conversations due to HH-RLHF repository inaccessibility. Synthetic data lacks realistic engagement patterns.

## Gate Decision

**Type:** MUST_WORK  
**Result:** FAIL  
**Action:** ABANDON - blocks H-M1, H-M2, H-M3 (saves ~80% compute)

## Recommendations

1. Obtain real HH-RLHF dataset and re-run
2. If still fails: Route to Phase 2A for hypothesis redesign
3. Alternative: H-E1-v2 with learned embeddings or H-E1-v3 with sequence modeling

## Files Generated

- Code: 14 Python modules (docs/youra_research/h-e1/code/)
- Reports: 04_validation.md, 04_checkpoint.yaml
- Outputs: evaluation.json, best_model.pt, 5 figures

---
**Created:** 2026-07-12 Phase 4 Coding
