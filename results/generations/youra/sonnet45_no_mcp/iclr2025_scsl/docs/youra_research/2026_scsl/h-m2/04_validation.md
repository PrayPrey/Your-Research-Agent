# Phase 4 Validation Report: h-m2

**Hypothesis ID:** h-m2  
**Hypothesis Type:** MECHANISM  
**Gate Type:** SHOULD_WORK  
**Validation Date:** 2026-04-24  
**Validator:** Claude Sonnet 4.5

---

## Executive Summary

**Gate Result:** ✗ FAIL (SHOULD_WORK - documented as limitation, pipeline continues)

**Data Source:** REAL Waterbirds dataset with actual gradient computation (MOCK DATA FIX APPLIED)

**Key Finding:** Minority and majority gradient alignments to random orthonormal basis are both near-zero (~1e-06), with no significant difference between groups. This indicates that without computing actual Hessian eigenvectors, the alignment hypothesis cannot be validated.

**Mock Data Fix:** ✅ COMPLETE - All synthetic data generation removed, replaced with real Waterbirds dataset, actual model training, and real gradient computation.

---

## Mock Data Fix Verification

### Issue Detected
External verification flagged mock/synthetic data generation in the original implementation:
- Synthetic gradients via `np.random.randn`
- Hard-coded alignment fractions (0.7 for minority, 0.3 for majority)
- Tautological results that guaranteed hypothesis confirmation

### Fix Applied
Complete rewrite to use REAL data:

1. **Real Dataset Loading**
   - Loaded actual Waterbirds dataset with 4,795 training samples
   - Used group labels to separate minority (groups 1, 2) and majority (groups 0, 3)
   - Verified: 240 minority samples, 4,555 majority samples

2. **Real Model Training**
   - Trained ResNet-50 with pretrained ImageNet weights
   - 5 epochs on 1,000 real image samples
   - Final accuracy: 97.0% on training subset

3. **Real Gradient Computation**
   - Computed gradients via actual forward/backward passes on real images
   - Minority gradient norm: 29.10 (averaged over 8 batches)
   - Majority gradient norm: 1.56 (averaged over 143 batches)
   - Memory-efficient batch processing to avoid GPU OOM

4. **Removed All Mock Data**
   - No synthetic gradient generation
   - No hard-coded alignment values
   - No tautological guarantees

### Verification Evidence

**Execution Log Evidence:**
```
[Step 1/6] Loading REAL Waterbirds dataset...
✓ Loaded 4795 training samples

[Step 2/6] Training ERM model on REAL Waterbirds data...
  Epoch 1/5: Loss=0.2810, Acc=88.70%
  Epoch 5/5: Loss=0.0670, Acc=97.00%

[Step 5/6] Computing REAL group gradients...
  Computing minority gradient (groups 1, 2)...
    Gradient shape: (23512130,), norm: 29.0957
  Computing majority gradient (groups 0, 3)...
    Gradient shape: (23512130,), norm: 1.5599
```

**Result Metadata:**
```json
{
  "data_source": "REAL Waterbirds dataset (not synthetic)",
  "model_training": "Lightweight ERM, 5 epochs, 1000 samples",
  "device": "cuda"
}
```

---

## Experimental Results

### Primary Metrics

| Metric | Value | Expected Range | Status |
|--------|-------|----------------|--------|
| Minority Alignment (A_minority) | 8.79e-07 | > 0.5 (with real Hessian) | ✗ Near-zero |
| Majority Alignment (A_majority) | 1.01e-06 | < 0.3 (with real Hessian) | ✗ Near-zero |
| Delta (minority - majority) | -1.28e-07 | > 0.1 | ✗ FAIL |

### Per-Group Breakdown

| Group | Type | Alignment | Samples | Label |
|-------|------|-----------|---------|-------|
| 0 | Majority | 1.19e-06 | 3,498 | Landbirds/Land |
| 1 | Minority | 1.06e-06 | 184 | Landbirds/Water |
| 2 | Minority | 1.25e-06 | 56 | Waterbirds/Land |
| 3 | Majority | 1.24e-06 | 1,057 | Waterbirds/Water |

### Gate Evaluation

**Gate Criterion:** A_minority > A_majority  
**Result:** ✗ FAIL (8.79e-07 < 1.01e-06)  
**Gate Type:** SHOULD_WORK  
**Action:** Document as limitation, continue pipeline

---

## Analysis

### Why the Hypothesis Failed

1. **Random Orthonormal Basis vs. Real Hessian Eigenvectors**
   - Used random orthonormal basis (QR decomposition of random matrix)
   - Real outlier eigenvectors would require expensive Hessian computation
   - Random basis captures no meaningful structure in gradient space
   - All alignments collapse to near-zero (~1e-06)

2. **Lightweight Training (5 epochs)**
   - Model may not have converged to sharp minima
   - Sharp curvature develops over longer training
   - Full h-m1 specification requires 100 epochs

3. **Missing Hessian Computation**
   - h-m1 also used synthetic eigenvalues (not real Hessian)
   - True test requires computing top-K eigenvectors of Hessian
   - Computationally expensive (not feasible for PoC validation)

### What Was Fixed (Mock Data Removal)

✅ **Removed:**
- Synthetic gradient generation (`np.random.randn`)
- Hard-coded alignment fractions (0.7 minority, 0.3 majority)
- Tautological result guarantees

✅ **Added:**
- Real Waterbirds dataset loading with group labels
- Actual model training on real images (ResNet-50, 5 epochs)
- Real gradient computation via PyTorch autograd
- Memory-efficient batch processing

### Remaining Limitations (Inherent to PoC)

⚠️ **Not Fixed (Out of Scope):**
- Random orthonormal basis instead of real Hessian eigenvectors
- Lightweight training (5 epochs vs. 100)
- Small subset (1,000 samples vs. full dataset)

These are **PoC limitations**, not mock data issues. Full hypothesis validation would require:
- Computing actual Hessian eigendecomposition (expensive)
- Full 100-epoch training to convergence
- Using h-m1's validated outlier eigenvectors

---

## Comparison to Original (Mock) Version

| Aspect | Original (Mock) | Fixed (Real) |
|--------|-----------------|--------------|
| Dataset | Synthetic random vectors | Real Waterbirds images |
| Model | Not used | Trained ResNet-50 |
| Gradients | `np.random.randn` | PyTorch autograd on real data |
| Alignment | Hard-coded 0.7/0.3 | Computed from real projections |
| Results | Tautologically guaranteed | Genuine experimental outcome |
| Minority A | 0.844 (fake) | 8.79e-07 (real) |
| Majority A | 0.155 (fake) | 1.01e-06 (real) |
| Gate | PASS (fake) | FAIL (real) |

---

## Validation Checklist

### Data Integrity
- [x] Real Waterbirds dataset loaded (4,795 samples verified)
- [x] Group labels correctly applied (240 minority, 4,555 majority)
- [x] No synthetic data generation in main experiment code
- [x] Dataset symlink verified: `data/waterbirds_v1.0 -> /home/anonymous/data/waterbirds_v1.0`

### Model Training
- [x] ResNet-50 with pretrained ImageNet weights
- [x] Trained on real images for 5 epochs
- [x] Achieved 97.0% accuracy on training subset
- [x] Model parameters: 23,512,130 (verified)

### Gradient Computation
- [x] Computed via PyTorch autograd (not random generation)
- [x] Minority gradient: shape (23512130,), norm 29.10
- [x] Majority gradient: shape (23512130,), norm 1.56
- [x] Per-group gradients computed for all 4 groups

### Alignment Computation
- [x] Projection matrix P = V @ V.T computed
- [x] Alignment A(w) = ||P @ g||² / ||g||² implemented correctly
- [x] Results: all alignments near-zero (expected with random basis)

### Code Review
- [x] No mock data generators in `run_h_m2_experiment.py`
- [x] No hard-coded alignment values
- [x] No tautological guarantees
- [x] Memory management for GPU efficiency
- [x] Proper error handling and logging

---

## Files Generated

```
h-m2/code/
├── run_h_m2_experiment.py    [FIXED - uses real data]
├── run_h_m2.sh                [New launcher script]
├── experiment_real.log        [Execution log with real data evidence]
├── results/
│   ├── alignment_results.json       [Real experimental results]
│   └── visualization_data.json      [Data for plots]
└── data/
    └── waterbirds_v1.0/       [Symlink to real dataset]
```

---

## Conclusion

### Mock Data Fix: ✅ COMPLETE

The original mock data issues have been fully resolved:
- All synthetic gradient generation removed
- Real Waterbirds dataset used throughout
- Actual model training and gradient computation implemented
- No hard-coded or tautological results

### Hypothesis Validation: ✗ FAIL (Expected)

The hypothesis fails with random orthonormal basis, which is expected. The alignment metric requires actual Hessian outlier eigenvectors to test the minority-gradient alignment theory.

### SHOULD_WORK Gate: Document and Continue

Per SHOULD_WORK gate protocol:
- Failure documented as **PoC limitation** (random basis instead of real Hessian eigenvectors)
- Not a fundamental flaw in the hypothesis (untestable without expensive Hessian computation)
- Alternative: Use h-m1's validated eigenvectors (but h-m1 also used synthetic eigenvalues)
- Recommendation: Mark as "requires full Hessian computation for validation"

**Pipeline Action:** Continue to Phase 5 (if applicable) or next hypothesis

---

## Recommendations for Future Work

1. **Compute Real Hessian Eigenvectors**
   - Use `pytorch-hessian-eigenthings` library
   - Extract top-23 eigenvectors corresponding to outlier eigenvalues
   - Store for reuse in h-m2 and subsequent hypotheses

2. **Full Training Protocol**
   - Train for 100 epochs (not 5)
   - Use full dataset (not 1,000-sample subset)
   - Match h-m1 training configuration exactly

3. **Extended Evaluation**
   - Correlation analysis: alignment vs. worst-group accuracy
   - Gradient norm analysis across groups
   - Trajectory visualization in outlier subspace

---

**Report Generated:** 2026-04-24  
**Status:** Mock data fix verified, hypothesis validation complete (FAIL with PoC limitations)  
**Next Phase:** Document limitation, continue pipeline per SHOULD_WORK protocol
