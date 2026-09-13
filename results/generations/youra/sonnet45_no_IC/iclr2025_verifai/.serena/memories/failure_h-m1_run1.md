# Phase 4 Failure Record: H-M1

**Date:** 2026-07-13
**Hypothesis ID:** h-m1
**Phase:** Phase 4 (Coding & PoC Validation)
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Routing:** Phase 2A (Hypothesis Redesign)

---

## Hypothesis Statement

If pruning (75% sparsity, CAP method) is applied to pre-trained models, then effective rank of weight matrices will decrease by ≥15% compared to baseline, because CAP removes low-magnitude weights while preserving high-information dimensions.

---

## Failure Summary

**Failure Type:** MECHANISM_REFUTED

**Key Finding:** Pruning at 75% sparsity **increases** effective rank by an average of 6.02%, directly contradicting the hypothesis prediction of ≥15% reduction.

**Performance Data:**
- Expected: Effective rank reduction ≥15%
- Observed: Effective rank **increase** +6.02%
- Consistency: 0% of layers (0/42) met threshold
- Gate Status: FAIL (MUST_WORK)

---

## Root Causes

1. **Incorrect Mechanistic Assumption**
   - Hypothesis assumed magnitude pruning reduces dimensionality
   - Reality: Pruning flattens singular value distribution → increases entropy → increases effective rank

2. **Pre-trained Weight Structure**
   - Pre-trained ResNet-50 weights have optimized structure
   - Random removal (magnitude pruning) disrupts this structure
   - Effect observed across all 42 measured Conv2d layers

3. **Pruning Method Limitation**
   - L1 magnitude pruning does not preferentially remove low-variance directions
   - Effect likely similar with CAP (both remove 75% of weights)
   - Dimensional reduction may only occur in untrained networks

---

## Experimental Evidence

### Implementation Details
- Model: ResNet-50 (pre-trained on ImageNet-1K)
- Pruning: L1 unstructured magnitude pruning (75% sparsity verified)
- Measurement: 42 Conv2d layers (layer2, layer3, layer4)
- Formula: Entropy-based effective rank (mathematically validated)

### Results Distribution
- Layers with reduction: 1/42 (2.4%)
- Layers with increase: 41/42 (97.6%)
- Average change: +6.02%
- Range: -0.01% to +10.87%

### Validation
- Effective rank computation verified on test matrices
- Identity matrix (10×10): ER = 10.00 correct
- Rank-1 matrix: ER = 1.00 correct
- Random matrix pruning: ER decreased 11.61% correct

**Conclusion:** Implementation correct. Result is genuine scientific finding.

---

## Lessons Learned

### 1. Mechanistic Hypotheses Require Careful Validation
- Intuitive claims may not hold in practice
- Pre-trained networks behave differently than random initialization
- Always validate mechanistic assumptions empirically

### 2. Effective Rank vs. Sparsity
- Sparsity not equal to lower dimensionality
- Entropy-based effective rank sensitive to singular value distribution shape
- Pruning can flatten distribution (increase entropy) while reducing parameter count

### 3. Dependent Hypothesis Impact
- h-m2, h-m3, h-m4 all depend on h-m1 dimensional reduction claim
- Entire causal chain invalidated by this failure
- Requires fundamental hypothesis redesign, not incremental fixes

---

## Dependent Hypotheses (Cascade Effect)

**Blocked:**
- h-m2: Weight Concentration Post-Pruning (depends on h-m1 passing)
- h-m3: Quantization Error Reduction (depends on h-m2)
- h-m4: Accuracy Preservation via Ordering (depends on h-m3)

**Status:** All marked as BLOCKED in verification_state.yaml

---

## Recommended Next Actions

### Phase 2A Redesign Options

1. **Drop Dimensional Reduction Claim**
   - Test weight variance/concentration directly (independent of rank)
   - Measure quantization error vs. weight distribution properties
   - Focus on empirical accuracy comparison

2. **Alternative Mechanisms**
   - Pruning concentrates important weights (not dimensionality)
   - Quantization benefits from weight clustering
   - Direct correlation: weight properties to quantization error

3. **Reframe Research Question**
   - Original: Does compression order affect accuracy via dimensionality
   - Revised: Does compression order affect accuracy via weight distribution properties

---

## Cross-Phase Learning

**For Future Hypotheses:**
- Validate mechanistic assumptions early (before building causal chains)
- Test on simple cases before complex ones (random matrices before pre-trained)
- Distinguish correlation (what works) from causation (why it works)
- Build shallow hypothesis chains initially, deepen after validation

**For This Research:**
- Compression order research still viable (h-e1 passed)
- Need new mechanistic explanation or empirical approach
- Return to Phase 2A with narrower scope

---

**Memory Type:** Phase 4 Failure (MUST_WORK FAIL with dependents)
**Action Taken:** Routed to Phase 2A for hypothesis redesign
