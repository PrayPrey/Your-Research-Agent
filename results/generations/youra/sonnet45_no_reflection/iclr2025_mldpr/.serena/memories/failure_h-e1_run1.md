# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-05-12T08:35:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAILED
**Failure Type:** FUNDAMENTAL_HYPOTHESIS_FAILURE

## Performance Gap

| Metric | Ours | Target | Gap |
|--------|------|--------|-----|
| Precision (MAJOR) | 0.25 | 0.70 | -0.45 (-64.3%) |
| Recall (MAJOR) | 0.25 | 0.85 | -0.60 (-70.6%) |
| Overall Accuracy | 0.2857 | 0.85 | -0.5643 (-66.4%) |

## Root Cause Analysis

- **Fixed cold-start thresholds do not generalize across dataset types**: 10/14 misclassifications (71% error rate). The thresholds 7%/2%/0.5% are insufficient for reliable classification across diverse datasets.

- **Frozen feature extractors insensitive to distribution shifts**: ImageNet-V2 drift score (0.023) far below MAJOR threshold (0.07) despite 10-15% accuracy drop reported in literature. Pre-trained models are too robust to natural distribution shifts to serve as effective drift indicators.

- **Dataset-agnostic approach fails across modalities**: NLP drift scores range 0.014-0.129 (9x range), Vision drift scores range 0.012-0.118 (10x range). No domain-specific calibration leads to systematic misclassification.

- **Ground truth label quality issues**: 6/14 datasets were simulated rather than real version pairs, contaminating validation results.

## Lessons Learned

1. **Cold-start thresholds are fundamentally insufficient**: Fixed thresholds (7%/2%/0.5%) cannot reliably classify dataset version changes across diverse types. Adaptive or learned thresholds are necessary.

2. **Frozen models poor drift detectors**: Pre-trained frozen feature extractors (ResNet-50, BERT) are too robust to distribution shifts. Fine-tuned drift detectors or learned representations are needed.

3. **Modality-specific calibration required**: Vision and NLP datasets exhibit vastly different drift score distributions. A single threshold set cannot handle both modalities.

4. **Real data essential for validation**: Simulated dataset version pairs (train/test splits) create artificial drift that contaminations validation. Real documented version pairs are necessary.

5. **Performance-based validation needed**: Statistical drift measures (KS, MMD) alone are insufficient. Need to correlate with actual performance degradation.

## Feedback for Next Phase

### Suggested Modifications
- Replace fixed cold-start thresholds with dataset-specific adaptive calibration
- Add supervised threshold learning from labeled version pairs
- Implement per-modality threshold adjustment (vision vs NLP)
- Replace frozen models with fine-tuned drift detectors or learned drift representations
- Acquire real dataset version pairs (ImageNet-V2, CIFAR-10.1) instead of simulated data

### What NOT To Do
- Do not use fixed universal thresholds across all dataset types
- Do not rely on frozen pre-trained models as feature extractors for drift detection
- Do not simulate dataset version pairs using train/test splits
- Do not assume statistical drift scores alone are sufficient for semantic versioning

### What Showed Promise
- The overall SVAD architecture (PCA → statistical tests → classification) is sound
- KS test and MMD both detected drift signals, though thresholds were wrong
- The multi-dataset evaluation framework (14 pairs) is comprehensive
- Visualization suite successfully identified failure modes

## Context

**Gate Type:** MUST_WORK  
**Routing Decision:** ROUTED_TO_PHASE_0  
**Hypothesis Status:** FAILED - verification chain blocked  

This failure indicates the foundational assumption is invalid:
> "Statistical drift tests (KS + MMD) with cold-start thresholds can reliably classify dataset version changes"

The hypothesis requires fundamental redesign. Recommend exploring:
1. Supervised classification approaches that learn thresholds from data
2. Adaptive two-phase calibration (cold-start → dataset-specific refinement)
3. Multi-signal fusion combining drift scores with performance degradation metrics

---
*For cross-phase reference*
*Written at: 2026-05-12T08:35:00Z*
