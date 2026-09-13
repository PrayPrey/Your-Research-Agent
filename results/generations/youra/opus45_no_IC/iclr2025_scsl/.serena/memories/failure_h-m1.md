# Failure Record: H-M1

**Date:** 2026-08-12
**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Result:** FAIL

## Hypothesis Statement

SGD's implicit regularization drives parameters toward flat regions of the loss landscape, evidenced by decreasing Hessian trace during training.

## Experiment Summary

- **Dataset:** Waterbirds (4795 train, 1199 val, 5794 test)
- **Model:** ResNet-18 (ImageNet pretrained)
- **Optimizer:** SGD (lr=0.001, momentum=0.9, weight_decay=0.0001)
- **Epochs:** 100
- **Trace logging:** Every 10 epochs using PyHessian Hutchinson method

## Key Results

| Metric | Expected | Observed |
|--------|----------|----------|
| Trace trend | Decreasing | INCREASING |
| Initial trace | - | 1460.46 |
| Final trace | < Initial | 6758.14 (+363%) |
| Correlation | Negative | +0.822 (p=0.0019) |

## Failure Analysis

The hypothesis was **NOT supported**. Hessian trace INCREASED significantly during training:

1. **Sharp early increase:** Trace jumped from 1460 to 4406 at epoch 10
2. **Continued growth:** Peaked at 6804 at epoch 50, remained elevated
3. **Strong positive correlation:** r=+0.822 indicates statistically significant INCREASING trend

## Possible Explanations

- SGD may not exhibit implicit sharpness minimization in this pretrained + fine-tuning setting
- The mechanism may depend on learning rate regime or batch size
- Hessian trace may not capture the relevant geometric property
- ImageNet pretrained initialization may dominate the Hessian behavior

## Impact

- H-M2 (spurious features offer flatter paths) is BLOCKED as it depends on H-M1
- The mechanistic explanation for group-conditional geometry needs revision
- H-E1's finding (minority groups show higher curvature) stands but lacks this mechanistic explanation

## Recommendations

1. Reconsider the theoretical basis for H-M1
2. Test with different learning rates or training from scratch
3. Consider alternative metrics (largest eigenvalue, spectral density)
4. Route to Phase 0 for hypothesis redesign

## Files

- Validation report: `h-m1/04_validation.md`
- Figure: `h-m1/figures/trace_vs_epoch.png`
- Results: `h-m1/code/outputs/results.json`
