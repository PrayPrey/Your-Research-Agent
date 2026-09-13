# Phase 4 Failure Record: h-e2 (Run 1)

**Date:** 2026-08-03T23:45:00Z
**Hypothesis:** h-e2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** PRETRAINED_ARTIFACT — between-centroid signal does not require ERM adaptation

## Performance Gap

| Metric | Ours (epoch1) | Baseline (epoch0) | Gap |
|--------|--------------|-------------------|-----|
| AUROC_y1_mean | 0.9825 | 0.9872 | -0.0047 (-0.5%) |

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Threshold:** gap_mean ≥ 0.10
- **Result:** FAIL (gap_mean = -0.0047, well below threshold)
- **Routing:** CONTINUE_TO_PHASE_5_WITH_CAVEAT (per 02c failure routing)

## Root Cause Analysis

- Pretrained ResNet-50 (ImageNet) achieves AUROC_y1 ≈ 0.987 without any Waterbirds training
- ERM fine-tuning for 1 epoch slightly decreases AUROC_y1 (gap ≈ -0.005 across all 5 seeds)
- Between-centroid direction is a pretrained ImageNet feature geometry artifact, not an ERM adaptation effect
- The 0.10 AUROC threshold was not approached; all seeds show negative gaps [-0.0066, -0.0022]

## Lessons Learned

1. Pretrained ResNet-50 backbone encodes minority/majority structure intrinsically — no fine-tuning needed
2. H-E2 FAIL is scientifically informative: the method works as pretrained feature extraction, not adaptation detection
3. Thin adapter (--reuse) pattern was correct and efficient; the hypothesis itself was wrong, not the implementation
4. Paper contribution should be reframed: "pretrained backbone encodes between-centroid minority signal; ERM fine-tuning does not amplify it"

## Feedback for Phase 5 / Paper

### Suggested Modifications
- Reframe contribution as "pretrained artifact detection" rather than "ERM adaptation effect"
- High epoch-0 AUROC (0.987) is evidence that pretrained backbone is the critical component
- H-E1 results (epoch-1 AUROC ≈ 0.982) remain valid as primary claim

### What NOT To Do
- Do not claim between-centroid signal emerges from ERM fine-tuning on Waterbirds
- Do not treat H-E2 FAIL as a block to Phase 5

### What Showed Promise
- The between-centroid AUROC signal itself is very strong (0.987 epoch-0, 0.982 epoch-1)
- Thin adapter pattern over H-E1 code was efficient and correct

---
*Written at: 2026-08-03T23:50:00Z*
*For cross-phase reference*
