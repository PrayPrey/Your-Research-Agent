# Failure Mode Analysis

## Overall Statistics

Total misclassified: 2

## Per-Family Patterns

### NormFree

**Pattern:** All 1 models misclassified as Hybrid

### SENet

**Pattern:** No failures

### RegNet

**Pattern:** No failures

### ViT-Extreme

**Pattern:** No failures

### Unknown

**Pattern:** All 1 models misclassified as Transformer

**Misclassified models:**

- vit_large_patch32_224: predicted as Transformer

## Proposed Extensions

Based on failure patterns, consider:

- Add weight standardization detection for NormFree models
- Add GroupNorm count feature
- Add activation function type detection
- Retrain classifier with balanced edge case representation
