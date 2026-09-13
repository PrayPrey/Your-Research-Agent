---
paper_id: "2311.09620"
title: "GAIA: Delving into Gradient-based Attribution Abnormality for Out-of-distribution Detection"
authors: "Chen, Li, Qu, Wang, Wan, Xiao"
year: 2023
arxiv_id: "2311.09620"
venue: "NeurIPS 2023"
citations: 16
---

# Paper Summary: GAIA - Gradient-based Attribution Abnormality for OOD Detection

## Key Contributions

**Core Innovation:** Instead of using gradient attribution to EXPLAIN predictions (Grad-CAM's original purpose), GAIA detects **abnormality in attribution gradients** as a signal for OOD detection. This addresses Adebayo 2022's limitation — don't use attribution results directly, use the abnormality of the attribution process itself.

**Two Abnormality Measures:**
1. **Channel-wise Average Abnormality (GAIA-A):** OOD samples produce noisy, abnormal outliers in channel-wise gradient weights compared to ID samples
2. **Zero-deflation Abnormality (GAIA-Z):** OOD samples have fewer zero partial derivatives (denser gradient matrices) than ID samples, especially in deeper layers

**Performance Gains:**
- CIFAR10: Reduces FPR95 by **23.10%** vs advanced post-hoc methods
- CIFAR100: Reduces FPR95 by **45.41%** vs advanced post-hoc methods
- ImageNet-1K: Reduces FPR95 by **17.28%** vs GradNorm (gradient-based baseline)

## Methodology

**Core Observation:** When pre-trained models attempt to explain OOD predictions using gradient-based attribution (Grad-CAM), they produce **meaningless attribution results** because the OOD label doesn't belong to training distribution. This confusion manifests as abnormal gradient patterns.

**Theoretical Foundation (Taylor Expansion):**
Attribution algorithms explained as Taylor expansion of network output Sc(z) around zero baseline:
```
Sc(0) = Sc(z) + Σ (1/p!) * (∂^p Sc(z) / ∂zi^p) * zi^p + ε
```
For OOD samples, error term ε diverges, causing attribution gradient abnormality.

**GAIA-A (Channel-wise Average):**
- Computes channel-wise weight wk = (1/WH) Σ (∂Sc(A) / ∂Ak_ij) for GradCAM
- ID samples: weights form smooth distribution
- OOD samples: weights show noisy outliers (Fig 2 shows clear separation)
- Abnormality metric: Expected value E[ε|Akl] based on gradient magnitude

**GAIA-Z (Zero-deflation):**
- Counts sparsity of attribution gradient matrix (∂Sc(A) / ∂Ak_ij)
- ID samples: Many zero derivatives (sparse gradients)
- OOD samples: Fewer zeros (dense gradients) — "zero-deflation"
- Abnormality metric: Sparsity ratio deviation from expected ID distribution

**Algorithm (Plug-and-Play):**
1. Forward pass: Compute class scores {Sc(x)}
2. Backpropagate attribution gradients ∂Sc(Akl) / ∂Akl_ij for each layer l
3. Calculate E[ε|Akl] via GAIA-A or GAIA-Z formula
4. Aggregate across layers: Global abnormality ||Λ||_F (Frobenius norm)
5. Return ||Λ||_F as OOD score (higher = more OOD)

**Key Properties:**
- Hyperparameter-free
- Training-free
- No ID data or outliers required
- Works with any pre-trained classifier

## Experiments & Results

**Benchmarks:**
- **CIFAR-10/100** (ID) vs SVHN, TinyImageNet, LSUN, Places, Textures (OOD)
- **ImageNet-1K** (ID) vs iNaturalist, SUN, Places, Textures (OOD)
- Architectures: ResNet34, WRN40, ResNet50

**Main Results (Table 3 - CIFAR10 with ResNet34):**
| Method | SVHN (FPR95↓) | TinyImageNet (FPR95↓) | Average AUROC |
|--------|--------------|----------------------|---------------|
| MSP (baseline) | 42.84 | 68.75 | 0.907 |
| ODIN | 38.77 | 64.82 | 0.915 |
| Energy | 34.27 | 59.17 | 0.925 |
| GradNorm | 33.81 | 55.34 | 0.931 |
| **GAIA-Z** | **26.01** | **42.60** | **0.954** |

**Improvement Breakdown:**
- vs MSP: FPR95 reduced from 42.84% → 26.01% on SVHN (39% relative improvement)
- vs GradNorm (gradient baseline): FPR95 reduced from 33.81% → 26.01% (23% relative improvement)

**CIFAR100 Results (even stronger):**
- Average FPR95 reduction: **45.41%** vs advanced post-hoc methods
- GAIA-Z consistently outperforms all baselines

**ImageNet-1K Results:**
- GAIA-A reduces FPR95 by 17.28% vs GradNorm
- GAIA-A better for large-scale benchmarks (GAIA-Z better for CIFAR)

**Ablation Studies:**
1. **Layer Selection:** Deeper layers (Block 3-4) show stronger abnormality signals
2. **GAIA-A vs GAIA-Z:** Complementary — GAIA-Z excels on smaller datasets, GAIA-A on large-scale
3. **Sensitivity Analysis:** Method robust to hyperparameter choices (none required)

## Theoretical Framework

**Why Attribution Abnormality Detects OOD:**

**Proposition 1 (Channel-wise Average):** For OOD input xout where label ∉ Yin, channel-wise gradient weights wk exhibit higher variance due to unpredictable Taylor expansion error term ε.

**Proposition 2 (Zero-deflation):** ID samples have sparse attribution gradients (many near-zero partials) because model learned efficient feature representations. OOD samples force model to use all features (dense gradients) due to uncertainty.

**Connection to Adebayo 2022:**
- Adebayo showed attribution RESULTS fail for unknown spurious
- GAIA uses attribution PROCESS abnormality as detection signal
- Key insight: Don't interpret the attribution map — measure how abnormal the attribution computation itself is

## Related Work & Baselines

**Post-hoc OOD Detection Methods Compared:**
- **Output-based:** MSP (Max Softmax Probability), ODIN (temperature scaling), Energy-based
- **Feature-based:** Mahalanobis distance, ReAct (activation clipping), KNN
- **Gradient-based:** GradNorm (parameter gradients) ← GAIA uses attribution gradients instead

**Key Distinction:**
- GradNorm uses ∂Loss/∂θ (parameter gradients)
- GAIA uses ∂Sc/∂A (attribution gradients w.r.t. activations)

**Attribution Algorithms Used as Foundation:**
- GradCAM (primary focus)
- Can extend to Integrated Gradients, SmoothGrad (similar gradient-based methods)

## Implications for Research

**Direct Solution to Adebayo 2022 Limitation:**
- Adebayo: Direct attribution fails for unknown spurious
- GAIA: Use gradient **abnormality** instead of attribution **results**
- Paradigm shift: Uncertainty in explanation process ≠ explanation content

**For Spurious Correlation Detection:**
- If spurious features cause models to rely on unexpected regions, attribution gradients will show abnormality
- GAIA detects this abnormality WITHOUT knowing what spurious feature to look for
- Potential application: Spurious reliance → abnormal gradient patterns → GAIA detects deviation

**Feasibility Advantages:**
- No training required (post-hoc)
- No prior knowledge of spurious signal needed
- Works with any pre-trained model
- Computationally cheap (single backward pass)

**Limitations:**
- Tested on OOD detection (distribution shift), not explicitly on spurious correlation within-distribution
- Requires defining "normal" gradient distribution for ID data (unsupervised setting)
- May need adaptation for spurious correlation scenario (ID_spurious vs ID_normal instead of ID vs OOD)

## Relevance to Selected Research Gap

**Gap 3 (P0): Attribution effectiveness for unknown spurious features**

This is the **SOLUTION** paper that addresses Adebayo 2022's limitation. Key takeaways:

1. **Gradient abnormality > direct attribution:** Don't use Grad-CAM to see what model uses (fails). Use abnormality in gradient computation to detect when model confused (succeeds).

2. **Two complementary signals:**
   - Channel-wise noise (GAIA-A): Outliers in gradient weights
   - Zero-deflation (GAIA-Z): Dense gradients instead of sparse

3. **Unsupervised detection:** No need to know spurious signal ahead of time — abnormality emerges automatically when model encounters unexpected inputs

**Adaptation to Spurious Correlation:**
- GAIA detects ID vs OOD (distribution shift)
- Spurious correlation: ID_spurious_group vs ID_core_group (subpopulation shift)
- Hypothesis: Models relying on spurious features show **abnormal gradient patterns** on minority groups (where spurious correlation breaks)
- Proposed method: Compute GAIA scores for different subpopulations, high abnormality indicates spurious reliance

**Action Items for Hypothesis Design:**
- ✅ Adopt gradient abnormality approach (GAIA-style) instead of direct attribution (Adebayo failure mode)
- ✅ Compute abnormality metrics (zero-deflation, channel-wise variance) on worst-group samples
- ✅ No prior knowledge of spurious feature required — abnormality signal emerges organically
- ✅ Post-hoc, training-free detection (aligns with feasibility constraints)
- ⚠️ Need to validate: Does spurious reliance cause similar abnormality to OOD shift?
