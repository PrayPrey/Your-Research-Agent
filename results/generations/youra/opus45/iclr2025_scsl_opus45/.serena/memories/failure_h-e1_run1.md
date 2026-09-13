# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-04-14T07:52:36+00:00
**Hypothesis:** h-e1 (Attribution Divergence Existence)
**Run:** 1
**Final Status:** ABANDON
**Failure Type:** HYPOTHESIS_PREMISE_INVALID
**Gate Type:** MUST_WORK

## Hypothesis Statement

Under spurious correlation in image classification (Waterbirds), if we compute group-stratified Integrated Gradients attribution maps and measure IoU between group-averaged top-10% regions, then we will observe IoU < 0.3 with p < 0.05, because minority and majority groups rely on different input features.

## Performance Gap

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| IoU | < 0.3 | 0.6477 | FAILED |
| P-value | < 0.05 | 1.0000 | FAILED |
| IoU Abandon | < 0.5 | 0.6477 | ABANDON TRIGGERED |

## Model Performance (Context)

| Metric | Value |
|--------|-------|
| Overall Accuracy | 88.21% |
| Worst-Group Accuracy | 70.25% |
| Group 0 (Landbird-Land) | 99.73% |
| Group 1 (Landbird-Water) | 79.82% |
| Group 2 (Waterbird-Land) | 70.25% |
| Group 3 (Waterbird-Water) | 95.17% |

## Root Cause Analysis

- **Primary cause:** No attribution divergence exists between minority and majority groups on Waterbirds dataset
- **Evidence:** IoU = 0.6477 indicates substantial overlap (>64%) in top-10% attribution regions between groups
- **P-value = 1.0:** Permutation test shows observed IoU is HIGHER than all null permutations, not lower
- **Conclusion:** The hypothesis premise is fundamentally invalid - minority and majority groups do NOT rely on different input features as hypothesized

## Technical Details

- **Attribution Method:** Integrated Gradients (Captum) with 50 steps, Gauss-Legendre quadrature
- **Convergence:** Multiple warnings (delta ~0.09 > 0.01 threshold), but unlikely to change fundamental result
- **Groups Compared:** Group 2 (waterbird-land, minority) vs Group 3 (waterbird-water, majority)
- **Samples:** 200 samples per group, top-10% threshold for IoU computation

## Lessons Learned

1. **Attribution divergence is not a reliable signal for spurious correlation detection on Waterbirds**
   - Despite the ~25% WGA gap (70% vs 95%), attribution patterns are similar between groups
   - This suggests the accuracy gap may not be due to different feature reliance

2. **The "spurious correlation → different features" assumption may be incorrect**
   - ERM model appears to use similar features for both minority and majority groups
   - The difficulty may be in feature extraction quality, not feature selection

3. **Alternative explanations for WGA gap:**
   - Feature extraction difficulty (waterbird features harder to extract from land backgrounds)
   - Dataset bias in feature representation (land backgrounds may occlude waterbird features)
   - Model capacity/training dynamics rather than spurious correlation reliance

4. **Integrated Gradients convergence is difficult with ResNet-50**
   - Higher n_steps or different methods may be needed for better convergence
   - However, even with poor convergence, the high IoU is unlikely to change fundamentally

## Cascade Effects

The following hypotheses were blocked due to h-e1 ABANDON:

- **h-m1:** BLOCKED - Cannot measure attribution mass in regions when no divergence exists
- **h-m2:** BLOCKED - Cascade blocked (depends on h-m1)
- **h-m3:** BLOCKED - Cascade blocked (depends on h-m2)

## Feedback for Future Research

### Suggested Alternative Approaches

- Consider GradCAM or attention-based attribution methods
- Examine feature space directly (t-SNE/UMAP of penultimate layer)
- Try per-sample analysis instead of group-averaged attributions
- Investigate other spurious correlation datasets (CelebA, ColoredMNIST)

### What NOT To Do

- Do not assume attribution divergence exists without verification
- Do not build mechanism hypotheses on unverified existence hypotheses
- Do not use group-averaged IoU as the sole divergence measure

### What Showed Promise

- The ERM training achieved expected performance (88% overall, 70% WGA)
- The attribution computation pipeline works correctly
- The permutation test methodology is sound

## Routing Decision

**Route to Phase 0:** The entire ADDM hypothesis chain is invalidated. The attribution divergence mechanism does not appear to be suitable for detecting spurious correlations on Waterbirds.

---
*For cross-phase reference*
*Written at: 2026-04-14T07:52:36+00:00*
*Pipeline will route to Phase 0 for alternative hypothesis brainstorming*
