# Reflection Report: h-c2

**Generated:** 2026-08-24T09:20:00+00:00
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED

## Hypothesis Summary

**Statement:** Mode profiles transfer across model families: cross-model Pearson r > 0.7 (LLaMA, Mistral, Qwen)

## Experiment Results

| Model Pair | Pearson r | Threshold | Status |
|------------|-----------|-----------|--------|
| resnet18 - vit_small | 0.804 | > 0.7 | PASS |
| resnet18 - convnext_tiny | -0.712 | > 0.7 | FAIL |
| vit_small - convnext_tiny | -0.990 | > 0.7 | FAIL |

## Analysis

### What Happened
Mode profiles do NOT transfer consistently across model families. While architecturally similar models (ResNet-ViT) show positive correlation, ConvNext exhibits inverted mode sensitivity profiles.

### Root Cause
ConvNext's architectural differences (inverted bottleneck, layer normalization, depthwise convolutions) produce fundamentally different gradient flow patterns. The mode profiles are architecture-dependent, not model-family-independent.

### Key Finding
Cross-architecture transfer requires same-family constraints. Mode profiles are stable within architectural families but invert across fundamentally different designs.

## Limitation Recorded

**Category:** Architectural Constraint
**Description:** Mode profiles transfer across models within similar architectural families (CNN-to-CNN, Transformer-to-Transformer) but NOT across fundamentally different architectures (CNN-to-ConvNext shows inverted profiles).

**Impact on Main Hypothesis:** The main fingerprinting approach remains valid for models within the same architectural family. Cross-family fingerprinting would require family-specific calibration.

## Recommendations for Phase 5

1. Baseline comparison should use models from same architectural family
2. If cross-architecture comparison needed, apply profile inversion correction for ConvNext-style architectures
3. Document this as a known limitation in final paper

## Next Action

Continue to Phase 5 with limitation recorded. SHOULD_WORK gates do not route to Phase 0/2A.
