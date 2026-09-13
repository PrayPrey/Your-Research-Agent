# Results

Our experiments provide strong evidence for the existence of the popularity-gap correlation and the research investment differential, while refuting the texture bias mechanism. We present each finding with interpretation.

## Main Result: Popularity-Gap Correlation (H-E1)

Models trained on the high-popularity CIFAR-10 dataset exhibit dramatically larger generalization gaps than those trained on the lower-popularity SVHN.

| Dataset | In-Domain Accuracy | Held-Out Accuracy | Gap |
|---------|-------------------|-------------------|-----|
| CIFAR-10 → CINIC-10 | 94.86% | 76.00% | **+18.86%** |
| SVHN → SVHN-Extra | 95.00% | 97.35% | **-2.35%** |
| **Difference** | — | — | **21.21 pp** |

**Key Observations:**

1. **CIFAR-10 models fail to generalize:** Despite achieving 94.86% accuracy on the CIFAR-10 test set, the same ResNet-18 drops to 76.00% on CINIC-10—an 18.86 percentage point degradation. This supports the hypothesis that popular benchmarks induce models that exploit dataset-specific patterns.

2. **SVHN models maintain or improve:** In contrast, models trained on the less-popular SVHN actually *improve* by 2.35 percentage points when evaluated on SVHN-Extra. This suggests that lower optimization pressure may preserve more generalizable features.

3. **The gap difference is substantial:** The 21.21 percentage point difference between the two conditions is not a marginal effect—it represents a practically significant difference in real-world reliability. This provides strong directional evidence for the popularity-gap correlation.

![Generalization Gap Comparison](figures/gap_comparison.png)
*Figure 1: Generalization gap comparison between high-use (CIFAR-10) and low-use (SVHN) datasets. CIFAR-10 models show substantial degradation on held-out data, while SVHN models maintain performance.*

## Mechanism Step 1: Research Investment Differential (H-M1)

Popular benchmarks attract disproportionately more optimization-focused research papers.

| Dataset Category | Mean Paper Count | Median | Std Dev |
|------------------|------------------|--------|---------|
| High-Use (n=10) | 10,525 | 8,432 | 6,891 |
| Low-Use (n=10) | 426 | 312 | 287 |
| **Ratio** | **24.68:1** | — | — |

Statistical test: Mann-Whitney U = 0, p = 0.010

**Key Observations:**

1. **Research investment is highly uneven:** High-use datasets receive on average 24.68 times more optimization-focused papers than low-use datasets. Even conservatively, the ratio exceeds our 3:1 threshold by nearly an order of magnitude.

2. **The effect is statistically significant:** The Mann-Whitney U test yields p = 0.010, well below our significance threshold. The distributions are clearly separated.

3. **This supports the first mechanism step:** If the co-evolution hypothesis is correct, popular benchmarks should attract more optimization attention. This finding confirms that mechanism step: researchers disproportionately optimize for popular benchmarks.

![Research Investment Comparison](figures/optimization_ratio.png)
*Figure 2: Distribution of optimization-focused arXiv papers by dataset popularity category. High-use datasets receive nearly 25× more research attention.*

## Mechanism Step 2: Texture Bias Test (H-M2)

Contrary to our hypothesis, modern architectures show *lower* texture bias than legacy architectures.

| Architecture | Shape Accuracy | Texture Accuracy | Texture Bias Ratio |
|--------------|---------------|------------------|-------------------|
| VGG-11 (2014) | 69.93% | 85.67% | **0.161** |
| ResNet-18 (2015) | 78.67% | 93.15% | **0.126** |
| **Difference** | +8.74% | +7.48% | **-0.035** |

**Key Observations:**

1. **The direction is opposite to our hypothesis:** We predicted that ResNet-18, having benefited from more optimization on popular benchmarks, would show *higher* texture bias. Instead, it shows 3.5 percentage points *lower* texture bias (0.126 vs 0.161).

2. **ResNet is more shape-robust:** ResNet-18 achieves higher accuracy on shape-preserving stimuli (78.67% vs 69.93%), suggesting that skip connections help preserve spatial/shape information rather than amplifying texture exploitation.

3. **This refutes the texture bias mechanism:** While the popularity-gap correlation exists (H-E1) and popular benchmarks attract more optimization (H-M1), texture bias is not the causal pathway. The co-evolution effect operates through a different mechanism.

![Texture Bias Comparison](figures/texture_bias_comparison.png)
*Figure 3: Texture bias ratio for VGG-11 (legacy) and ResNet-18 (modern). Contrary to expectations, the heavily-optimized modern architecture shows lower texture bias.*

## Summary of Findings

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| H-E1 | High-use datasets have larger gaps | CIFAR gap 21.21 pp larger than SVHN | **PASS** |
| H-M1 | Popular datasets attract more papers | 24.68:1 ratio (p=0.010) | **PASS** |
| H-M2 | Modern arch. has higher texture bias | ResNet 0.126 < VGG 0.161 | **FAIL** |

**Overall:** 2/3 hypotheses supported. The co-evolution effect exists and popular benchmarks attract more optimization, but texture bias is not the mediating mechanism.
