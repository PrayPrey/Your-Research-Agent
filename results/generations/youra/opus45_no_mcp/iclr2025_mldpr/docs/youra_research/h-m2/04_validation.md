# Phase 4 Validation Report: H-M2

**Hypothesis:** Dataset-specific optimization creates features that exploit dataset artifacts (texture bias)

**Type:** MECHANISM  
**Date:** 2026-08-19  
**Gate Type:** SHOULD_WORK (was MUST_WORK per plan, but this is a mechanism hypothesis)

---

## Executive Summary

**Gate Result: FAIL**

The experiment tested whether modern architectures (ResNet-18, post-2015, heavily optimized on CIFAR-10) exhibit higher texture bias than legacy architectures (VGG-11, pre-2015). Results show the **opposite** of the hypothesis:

- **VGG-11 texture bias ratio:** 0.161
- **ResNet-18 texture bias ratio:** 0.126  
- **Difference:** -0.035 (ResNet shows LOWER texture bias)

The direction check failed: ResNet-18 demonstrates **more shape-based** rather than texture-based classification.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Models | VGG-11 (9.35M params), ResNet-18 (11.17M params) |
| Training | 30 epochs, SGD + cosine LR (0.1 → 0.001) |
| Dataset | CIFAR-10 (50k train, 10k test) |
| Conflict Stimuli | Stylized-CIFAR-10 (10k samples, AdaIN style transfer) |
| Texture Source | DTD (47 categories, 5,640 images) |

---

## Results

### Model Accuracy

| Model | Final Test Accuracy |
|-------|---------------------|
| VGG-11 | 85.67% |
| ResNet-18 | 93.15% |

### Texture Bias Measurement

| Metric | VGG-11 | ResNet-18 |
|--------|--------|-----------|
| Texture Bias Ratio | 0.161 | 0.126 |
| Shape Accuracy | 54.59% | 71.86% |
| Texture Accuracy | 10.44% | 10.34% |
| Neither | 34.97% | 17.80% |

### Gate Evaluation

| Criterion | Expected | Actual | Pass |
|-----------|----------|--------|------|
| Direction | ResNet > VGG | ResNet < VGG | FAIL |
| Effect Size | diff > 0.05 | diff = -0.035 | FAIL |

---

## Analysis

### Finding: Modern Architectures Show LOWER Texture Bias

Contrary to the hypothesis, ResNet-18 (heavily optimized on CIFAR-10) demonstrates:

1. **Stronger shape recognition** (71.86% vs 54.59% shape accuracy)
2. **Lower texture bias ratio** (0.126 vs 0.161)
3. **Better overall generalization** (93.15% vs 85.67% test accuracy)

### Possible Explanations

1. **Architectural inductive biases**: ResNet's skip connections may preserve spatial/shape information better than VGG's sequential convolutions
2. **Model capacity**: ResNet-18 has more parameters and can learn more nuanced representations
3. **Optimization dynamics**: The cosine LR schedule may benefit ResNet's residual learning differently

### Implications for Main Hypothesis

H-M2 tested whether intensive optimization on popular datasets creates texture-exploiting features. The evidence suggests:

- Architecture improvements (skip connections, batch normalization) lead to MORE generalizable features, not artifact-exploiting ones
- The texture bias mechanism may not be the primary explanation for generalization gaps

---

## Figures

1. **Gate Comparison** (`figures/gate_comparison.png`): Bar chart showing VGG-11 vs ResNet-18 texture bias ratios
2. **Shape-Texture Accuracy** (`figures/shape_texture_accuracy.png`): Breakdown of shape/texture classification
3. **Training Curves** (`figures/training_curves.png`): Test accuracy over epochs

---

## Gate Verdict

**FAIL** - The hypothesis that modern architectures (optimized on popular datasets) show higher texture bias is not supported. The mechanism proposed in H-M2 does not explain the generalization gaps observed in H-E1.

---

## Next Steps

Per gate_types.SHOULD_WORK fail_action: "EXPLORE: Alternative artifact measures"

Potential alternatives:
1. Measure other forms of dataset artifacts (spurious correlations, background features)
2. Test on different dataset pairs (ImageNet vs ObjectNet)
3. Examine frequency-domain biases instead of texture bias

---

## Appendix: Raw Results

```json
{
  "gate": {
    "pass_gate": false,
    "diff": -0.035,
    "resnet_ratio": 0.126,
    "vgg_ratio": 0.161,
    "threshold": 0.05
  },
  "vgg_final_acc": 0.8567,
  "resnet_final_acc": 0.9315
}
```
