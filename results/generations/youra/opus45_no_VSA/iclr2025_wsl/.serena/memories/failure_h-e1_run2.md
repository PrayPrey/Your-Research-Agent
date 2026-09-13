# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-10T07:30:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** PARTIAL
**Failure Type:** PARTIAL_CRITERIA_MET

## Performance Gap

| Metric | Achieved | Target | Gap |
|--------|----------|--------|-----|
| Models with CV < 0.3 | 36.4% (4/11) | >50% | -13.6% |
| Median CV | 0.3044 | <0.3 | +0.0044 |
| Mean CV | 0.4062 | <0.3 | +0.1062 |

## Root Cause Analysis

- Feature extraction methodology WORKS - all spectral features computable
- CV stability varies significantly by model architecture
- Larger models (resnet152) show high instability (CV > 1.0)
- Group normalization models (resnet50_gn) show perfect stability (CV = 0.0)
- Sample size (11 models) insufficient for statistical confidence

## Lessons Learned

1. Spectral features ARE extractable from pretrained models - existence confirmed
2. Feature stability correlates with model size and normalization type
3. Per-architecture tuning may improve CV consistency
4. Need extended run on full 150+ model pool before final gate decision

## Feedback for Next Phase

### Suggested Modifications
- Increase model pool to full 150+ target
- Test ViT and ConvNeXt families for architecture-specific patterns
- Consider adaptive probe set size based on model capacity

### What NOT To Do
- Don't assume all architectures behave uniformly
- Don't use single CV threshold without architecture awareness

### What Showed Promise
- Group normalization models achieve perfect stability
- Smaller models (resnet10t) consistently stable
- Core spectral feature computation is reliable

---
*For cross-phase reference*
*Written at: 2026-08-10T07:30:00Z*
