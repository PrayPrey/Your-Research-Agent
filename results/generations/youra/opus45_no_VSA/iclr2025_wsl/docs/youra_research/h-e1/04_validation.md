# Phase 4 Validation Report: H-E1

**Hypothesis**: CV_PR can be reliably extracted from 100+ timm models using randomized SVD with 20 seeds  
**Type**: EXISTENCE (Proof of Concept)  
**Gate**: MUST_WORK  
**Date**: 2026-08-10

---

## Summary

| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Completion rate | 100.00% | ≥ 95% | ✓ |
| CV_PR finite range | [0.0014, 0.0326] | (0, 10) | ✓ |
| Models processed | 100 | ≥ 100 | ✓ |

**Result: PASS**

---

## Experiment Results

```
Models processed: 100
Models valid: 100
Completion rate: 100.00%
Mean CV_PR: 0.0116
Std CV_PR: 0.0059
Range: [0.0014, 0.0326]
```

---

## Mechanism Verification

1. **Randomized SVD**: Implemented via QR-based random projection (Halko algorithm)
2. **Participation Ratio**: PR = (Σλ)² / Σλ² computed from squared singular values
3. **CV aggregation**: 20 seeds per layer, CV = std/mean across seeds
4. **Model-level aggregation**: Mean CV_PR across all conv2d/linear layers

All CV_PR values are finite and within expected range (0, 10), confirming reliable extraction.

---

## Code Artifacts

- `h-e1/code/model.py`: Core SVD+PR functions
- `h-e1/code/extract.py`: Model loading and layer extraction
- `h-e1/code/main_fast.py`: Optimized extraction script
- `h-e1/h-e1/results/summary.json`: Summary statistics
- `h-e1/h-e1/results/results.csv`: Per-model results
- `h-e1/h-e1/figures/`: Visualizations

---

## Gate Verdict

**MUST_WORK gate: SATISFIED**

CV_PR metric can be reliably extracted from 100+ diverse pretrained models using randomized SVD with 20 seeds. The methodology is feasible for subsequent hypotheses (H-E2, H-M1, H-M2).
