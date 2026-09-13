# Results

We present results for both experiments: H-E1 (existence of spurious dominance) and H-M1 (gradient competition mechanism). H-E1 passes, confirming spurious features dominate early. H-M1 fails, falsifying the gradient competition hypothesis.

## H-E1: Spurious Feature Dominance Exists

**Finding:** Spurious features dominate from epoch 0, with attribution ratio 1.35—spurious regions receive 35% more GradCAM activation than core regions from the first epoch.

| Epoch | Attribution Ratio ($R$) | Status |
|-------|------------------------|--------|
| 0 | 1.348 | > 1.0 ✓ |
| 5 | 1.273 | > 1.0 ✓ |
| 10 | 1.431 | > 1.0 ✓ |
| 13 (peak) | 1.590 | > 1.0 ✓ |
| 25 | 1.255 | > 1.0 ✓ |
| 50 | 1.255 | > 1.0 ✓ |

**Gate evaluation:** Dominance epoch < 10 required. Observed: dominance from epoch 0. **PASS.**

Figure 1 shows the attribution ratio trajectory across all 50 epochs. Spurious dominance is immediate (from initialization) and persistent (ratio never drops below 1.0). The ratio peaks at epoch 13 (1.59), suggesting maximum spurious reliance occurs early-to-mid training before stabilizing.

**Interpretation:** This confirms the simplicity bias phenomenon [Shah et al., 2020] on Waterbirds. ERM-trained ResNet-50 exhibits spurious feature preference from the very first forward pass, likely due to pretrained ImageNet features that respond more strongly to background textures than bird morphology. The monotonicity of dominance (never reversing) indicates that standard training provides no natural correction mechanism.

## H-M1: Gradient Competition Hypothesis Falsified

**Finding:** Contrary to the gradient competition hypothesis, spurious-aligned samples produce *lower* gradient norms than minority samples. The gradient ratio is 0.18, not >1.5 as predicted—an inversion by a factor of 8.

| Seed | Early Epoch Ratio (1-10) | Direction |
|------|-------------------------|-----------|
| 42 | 0.175 | Minority > Spurious |
| 123 | 0.173 | Minority > Spurious |
| 456 | 0.181 | Minority > Spurious |
| **Mean** | **0.176 ± 0.004** | **Inverted** |

**Gate evaluation:** Ratio > 1.5 required. Observed: 0.18. **FAIL.**

Figure 2 shows the gradient norm ratio trajectory across 50 epochs for all three seeds. The ratio starts around 0.45 at epoch 1 and decreases to 0.13-0.16 by epoch 50. Critically, the ratio is *never* above 1.0—minority samples produce stronger gradients at every epoch.

Figure 3 compares absolute gradient norms between groups. Minority samples consistently produce 5-7× higher gradient norms than spurious-aligned samples, with the gap widening over training.

**Interpretation:** The gradient competition hypothesis is empirically falsified. Spurious features dominate (H-E1) but *not* because they receive stronger gradient signals. Instead, we observe the opposite pattern:

1. **Spurious-aligned samples achieve low loss quickly** (background is easy to classify)
2. **Low loss produces low gradients** (already solved, little learning signal)
3. **Minority samples remain high-loss** (background misleads, bird features needed)
4. **High loss produces high gradients** (still learning)

This reveals that "gradient competition" is the wrong frame. Spurious dominance arises from *convergence speed*, not gradient magnitude—spurious patterns occupy simpler loss landscape regions that converge first.

## Ablation: Trend Consistency

The decreasing gradient ratio trend (0.45 → 0.15 over training) is consistent across all seeds and aligns with our interpretation. As spurious-aligned samples become "more solved," their gradients decrease further. Minority samples continue generating high gradients because they remain difficult.

| Epoch Range | Mean Ratio | Trend |
|-------------|-----------|-------|
| 1-10 | 0.176 | High (early training) |
| 11-25 | 0.142 | Decreasing |
| 26-50 | 0.138 | Stable low |

This pattern supports the convergence speed interpretation: gradient contribution inversely correlates with solution quality, not feature preference.

## Summary

| Hypothesis | Prediction | Observed | Gate |
|------------|------------|----------|------|
| H-E1 (Existence) | $R > 1.0$ before epoch 10 | $R = 1.35$ at epoch 0 | **PASS** |
| H-M1 (Mechanism) | $\rho > 1.5$ in epochs 1-10 | $\rho = 0.18$ | **FAIL** |

Spurious dominance exists but the hypothesized mechanism is incorrect. The gradient competition hypothesis is falsified with high confidence (8× inversion, consistent across 3 seeds).
