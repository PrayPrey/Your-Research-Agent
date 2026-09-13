# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-05T12:55:21Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Routing:** ROUTED_TO_PHASE_0

## Hypothesis Statement

Under ResNet-50 H-E1 checkpoints (3 seeds × 4 methods = 12 checkpoints), full-model gradient cosine similarity between background-stratified Waterbirds test batches (N=100 land-bg vs N=100 water-bg) is measurable, valid (scalar in [-1,1]), and shows between-method variance with Cohen's d (ERM vs DFR) > 0.8.

## Gate Evaluation

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Valid cosine_sim (12/12) | 12/12 | 12/12 | PASS |
| Cohen's d (ERM vs DFR) | -0.330 | > 0.8 | FAIL |

## Per-Method Results

| Method | Mean cosine_sim | Std | CV |
|--------|----------------|-----|-----|
| ERM | 0.185 | 0.736 | 3.98 |
| SAM | -0.460 | 0.404 | 0.88 |
| GroupDRO | 0.453 | 0.568 | 1.25 |
| DFR | 0.387 | 0.454 | 1.17 |

## Root Cause Analysis

- Full-model gradient vector (D≈25M) too noisy at N=100 samples per stratum
- 10-epoch PoC checkpoints insufficient: ERM has not overfit to spurious features enough to produce distinct gradient patterns
- Within-method CV = 1.17–3.98: 3 seeds cannot detect any effect at this noise level
- Sign instability: ERM seed3=+0.94 vs seed1=-0.53 — metric has no discriminative signal

## Lessons Learned

1. Full-model gradient cosine similarity requires N>>100 samples to stabilize
2. Discriminative signal requires fully trained checkpoints (100 epochs minimum)
3. Cohen's d > 0.8 is unachievable with CV > 1 at n=3 seeds
4. Alternative: last-layer gradients (D=2048) or GraSP-style centered cosine similarity
5. Batch size N=500+ or full background-stratified test set needed

## Feedback for Phase 0 Redesign

### What NOT To Do
- Full-model gradient cosine similarity with N=100 samples
- PoC checkpoints trained < 50 epochs for spurious feature studies
- Cohen's d gate with n=3 seeds when CV > 1 expected

### What Showed Promise
- WILDS loading and stratified sampling worked correctly
- PyTorch autograd backward + cosine_similarity is numerically stable
- All 12 cosine_sim values valid (existence of measurability proven)

### Suggested Redesign Direction
- Last-layer gradient cosine similarity (reduce D from 25M to 2048)
- Use author-released checkpoints (izmailovpavel/spurious_feature_learning) for true ERM/GroupDRO/DFR method differentiation
- Increase N per stratum to 500+ or full background split

## Dependent Hypotheses Blocked

- h-m1: BLOCKED (prerequisite h-e1 FAIL)
- h-m2: BLOCKED (prerequisite chain broken)
- h-m3: BLOCKED (prerequisite chain broken)
