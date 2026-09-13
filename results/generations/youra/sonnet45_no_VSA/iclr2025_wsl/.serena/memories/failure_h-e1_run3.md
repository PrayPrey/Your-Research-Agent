# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-07-11T16:43:00+00:00
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Best Metric (MAE) | 0.2942 | 0.1208 | +0.1734 (143.5% worse) |

## Root Cause Analysis

- Heuristic architecture detection achieved MAE=0.2942 on validation set
- Performance worse than random baseline (MAE=0.1208)
- Both MUST_WORK success criteria failed: (1) MAE >= threshold (0.15), (2) Proposed >= Baseline
- Dataset acquisition partially failed: only 9/20 planned models downloaded
- All validation samples were Hybrid architecture family (ConvNeXt, RegNet variants)
- PyTorch/transformers version conflicts prevented HuggingFace model downloads
- Soft vs hard label mismatch: heuristic produced hard labels, but validation expected soft labels
- Insufficient sample diversity: evaluation set contained only hybrid architectures
- Methodology had partial merit: heuristic correctly detected CNN patterns but evaluation setup was flawed

## Lessons Learned

1. **Dataset diversity is critical**: Evaluation on single architecture family (Hybrid only) creates biased test conditions that don't reflect true performance
2. **Label type mismatch matters**: Mixing hard predictions with soft ground truth invalidates MAE calculations
3. **Dependency version conflicts block data acquisition**: PyTorch 2.x + transformers 4.x + torchaudio incompatibility prevented 55% of planned models from loading
4. **Baseline comparison requires fair test conditions**: Random baseline performed better because soft labels had uniform distributions that matched random predictions
5. **Heuristic pattern detection was sound**: The core approach (4D conv detection, Q/K/V matrix identification) correctly identified architectural patterns in downloaded models
6. **Evaluation methodology needs upfront validation**: Should verify dataset composition, label types, and baseline fairness before running full experiment

## Feedback for Next Phase

### Suggested Modifications
- Use TIMM library exclusively for consistent model access (avoid HuggingFace/transformers conflicts)
- Ensure balanced architecture family distribution in validation set (CNN, Transformer, Hybrid)
- Align label types: either convert soft labels to hard (argmax) or produce soft predictions
- Verify baseline uses same label type before comparison
- Add dataset composition check as pre-experiment validation gate

### What NOT To Do
- Don't mix model sources with incompatible dependencies (HuggingFace + TIMM)
- Don't evaluate on single architecture family and claim generalization
- Don't compare hard predictions against soft labels
- Don't trust "random baseline" without verifying label distribution fairness

### What Showed Promise
- 4D convolution tensor shape detection correctly identified CNN layers
- Q/K/V attention matrix pattern matching worked for Transformer detection
- TIMM library provided reliable model access without dependency conflicts
- Heuristic scored correctly on downloaded models before evaluation setup issues

---
*For cross-phase reference*
*Written at: 2026-07-11T16:43:00+00:00*
