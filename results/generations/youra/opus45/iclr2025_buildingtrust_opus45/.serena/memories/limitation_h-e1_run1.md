# Limitation Record: h-e1 (Run 1)

**Date:** 2026-03-23T15:30:00+00:00
**Hypothesis:** h-e1
**Run:** 1
**Gate Type:** MUST_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Hypothesis Statement

CFS (attention stability on anchors) predicts answer correctness with AUROC >= 0.55

## Limitation Details

The CFS mechanism achieved AUROC = 0.5500, exactly at the pass threshold. However, the 95% confidence interval [0.4701, 0.6334] includes 0.50, meaning we cannot statistically exclude random chance at the 95% confidence level.

This represents a **marginal result** - the mechanism shows weak signal but is not robust.

## Failed Checks

- 95% CI lower bound (0.4701) does not exclude 0.50
- Cannot claim statistical significance at p < 0.05

## Partial Results

| Metric | Value |
|--------|-------|
| AUROC | 0.5500 (threshold: 0.55) |
| CI Lower | 0.4701 |
| CI Upper | 0.6334 |
| CFS Mean | 1.18e-06 |
| CFS Std | 6.38e-06 |
| Samples | 1000 |
| Runtime | 122.5 minutes |

## Key Observations

1. **Marginal Signal Detected:** The AUROC of 0.55 suggests there may be a weak relationship between CFS and answer correctness, but it's at the boundary of statistical significance.

2. **High Variance:** The wide confidence interval [0.47, 0.63] indicates substantial uncertainty in the estimate.

3. **Very Small CFS Values:** The CFS scores are extremely small (mean ~1e-6), suggesting either:
   - The JSD computation produces very small divergences
   - The attention distributions are very similar across CoT steps
   - The normalization/scaling may need adjustment

4. **Correctness Bias:** The model achieved 61.8% correctness rate, providing reasonable signal for classification.

## Experiment Summary

- **Model:** Qwen/Qwen2.5-7B-Instruct
- **Dataset:** MMLU (800) + TruthfulQA (200) = 1000 samples
- **CFS Layers:** 16-24
- **Anchor K:** 10
- **Train/Test Split:** 80%/20%

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed (CI exclusion of 0.50)
2. Whether the limitation is fundamental (weak signal) or circumstantial (sample size, hyperparameters)
3. Alternative approaches that might avoid this limitation:
   - Larger sample sizes for tighter CI
   - Different anchor identification methods
   - Alternative stability metrics beyond JSD
   - Different layer combinations

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL), this limitation informs brainstorming to avoid similar issues
- **Phase 2A:** Informs hypothesis refinement - consider stronger signal extraction methods
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-23T15:30:00+00:00*
*For cross-phase reference*
