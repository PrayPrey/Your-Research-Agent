# Phase 2B: Verification Plan
## Architecture-Aware Compression Sequencing

**Generated:** 2026-08-25  
**Main Hypothesis:** H-AACS-v1  
**Status:** READY for Phase 2C

---

## Overview

This plan decomposes the main hypothesis into 4 sub-hypotheses following the E→M→C dependency chain.

### Dependency Graph

```
h-e1 (EXISTENCE) ─┬─► h-m1 (MECHANISM) ─► h-m2 (MECHANISM) ─► h-c1 (COMPARISON)
   MUST_WORK      │      MUST_WORK           SHOULD_WORK        SHOULD_WORK
                  │
                  └─► [If fails: Main hypothesis falsified]
```

---

## Sub-Hypotheses

### h-e1: Ordering Effect Existence (MUST_WORK)

**Statement:** Compression ordering (prune-first vs quantize-first) produces measurably different accuracy outcomes on ResNet-18 at 50% reduction + INT8.

**Gate Type:** MUST_WORK — Pipeline stops if this fails.

**Protocol:**
1. Load pretrained ResNet-18
2. For each of 3 seeds:
   - Apply prune-first ordering: prune 50% → quantize INT8
   - Apply quantize-first ordering: quantize INT8 → prune 50%
   - Measure top-1 accuracy on ImageNet-1K (10% subset)
3. Compute per-layer accuracy differences

**Success Criteria:**
- Mean accuracy difference > 0.5% between orderings
- Paired t-test p < 0.05 across seeds

**Early Stop:** Effect size < 0.5% across 80% of layers → Stop pipeline

---

### h-m1: Feature-Ordering Correlation (MUST_WORK)

**Statement:** Pre-compression weight statistics (sparsity, kurtosis) correlate with per-layer ordering preference.

**Gate Type:** MUST_WORK — Core mechanism validation.

**Depends On:** h-e1 (ordering effect must exist)

**Protocol:**
1. For each layer in ResNet-18:
   - Compute pre-compression features: sparsity (% weights < 1e-4), kurtosis
   - Record ordering preference from h-e1 results (+1 prune-first, -1 quantize-first)
2. Compute Pearson correlation for each feature

**Success Criteria:**
- At least one feature with r > 0.3
- At least 2 features with r > 0.2

**Early Stop:** All correlations r < 0.2 → Features lack predictive signal

---

### h-m2: Predictive Classifier (SHOULD_WORK)

**Statement:** A simple classifier (logistic regression) trained on weight features can predict optimal ordering above chance.

**Gate Type:** SHOULD_WORK — Strengthens but not required.

**Depends On:** h-m1 (features must correlate)

**Protocol:**
1. Build dataset: (features, ordering_preference) per layer
2. Train logistic regression with leave-one-out CV
3. Evaluate prediction accuracy

**Success Criteria:**
- LOO accuracy > 55%
- AUC > 0.6

**Early Stop:** Accuracy < 52% → Features insufficient for classification

---

### h-c1: Prediction Utility (SHOULD_WORK)

**Statement:** Predicted ordering yields higher model accuracy than fixed default or random ordering.

**Gate Type:** SHOULD_WORK — Practical value demonstration.

**Depends On:** h-m2 (classifier must work)

**Protocol:**
1. Compare three strategies:
   - Default: always prune-first
   - Random: flip coin per layer
   - Predicted: use h-m2 classifier
2. Measure final model accuracy for each

**Success Criteria:**
- Predicted wins > 70% of layer comparisons
- Overall accuracy improvement > 0.3%

---

## Execution Order

| Phase | Hypothesis | Gate | Action if Fail |
|-------|------------|------|----------------|
| 2C.1 | h-e1 | MUST_WORK | Stop pipeline |
| 2C.2 | h-m1 | MUST_WORK | Stop pipeline |
| 2C.3 | h-m2 | SHOULD_WORK | Continue to h-c1 |
| 2C.4 | h-c1 | SHOULD_WORK | Note limitation |

---

## Resource Estimates

| Hypothesis | GPU Hours | Complexity |
|------------|-----------|------------|
| h-e1 | 2-4 | Low |
| h-m1 | 0.5 | Low (analysis only) |
| h-m2 | 0.5 | Low |
| h-c1 | 1-2 | Low |
| **Total** | **4-7** | — |

---

## Risk Assessment

1. **h-e1 fails:** Ordering may not matter for this architecture/operating point. Mitigation: try different compression ratios.

2. **h-m1 fails:** Static features may be insufficient; dynamic features needed. Mitigation: add gradient-based features.

3. **Small sample size:** Only ~17 layers in ResNet-18. Mitigation: aggregate across layer types; extend to ResNet-34.

---

## Next Steps

Proceed to Phase 2C with h-e1 (READY status). Design detailed experiment specification.
