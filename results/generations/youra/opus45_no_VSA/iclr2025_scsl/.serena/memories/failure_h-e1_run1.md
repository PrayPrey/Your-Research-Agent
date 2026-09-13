# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-09T08:20:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Gate Type:** MUST_WORK
**Failure Type:** HYPOTHESIS_NOT_SUPPORTED

## Hypothesis Statement

CKA inversion (environment > species similarity) occurs during ERM training on Waterbirds by epoch 30

## Performance Summary

| Metric | Value | Expected |
|--------|-------|----------|
| CKA_species | 0.52-0.71 | Lower than CKA_env |
| CKA_env | Always lower | Higher than CKA_species |
| Test Accuracy | 91.51% | N/A |
| Worst-Group Accuracy | 75.08% | N/A |

## Root Cause Analysis

- No CKA inversion detected at any epoch (1-30)
- CKA_species consistently > CKA_env throughout training (ratio 0.52-0.71)
- The hypothesized phenomenon (environment alignment dominating species alignment) did not occur
- Code executed correctly; experimental methodology valid; hypothesis simply not supported by data

## Lessons Learned

1. CKA similarity to species labels remains dominant over environment labels throughout ERM training
2. Pretrained ResNet-50 features maintain species-aligned representations even under spurious correlations
3. The "simplicity bias favoring environment" may not manifest as CKA inversion in this experimental setup
4. Consider alternative metrics or experimental designs to detect spurious learning dynamics

## Feedback for Phase 0/2A

### Suggested Modifications
- Consider different similarity metrics beyond CKA (e.g., SVCCA, linear probing accuracy)
- Try different feature extraction points (earlier layers, attention maps)
- Examine per-group CKA trajectories rather than aggregate measures
- Consider training from scratch vs pretrained to isolate initialization effects

### What NOT To Do
- Do not assume CKA inversion is the only signal of spurious learning
- Do not retry with same methodology expecting different results

### What Showed Promise
- Experimental infrastructure works correctly
- GradCAM masking pipeline functional
- CKA computation validated

---
*For cross-phase reference*
*Written at: 2026-08-09T08:20:00Z*
*Route: Phase 2A-Dialogue for hypothesis refinement*