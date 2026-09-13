# Methodology

## Overview

Our diagnostic approach rests on a single observation: if backbone-level spurious encoding and head-level decision making are the two sites of robustification, then we need a measurement that is sensitive to one and *not* the other. A linear probe trained on *frozen* backbone features to predict the *spurious attribute* is exactly this measurement — it captures what the backbone encodes while being independent of head weights.

We design a three-gate verification study with pre-registered statistical tests to characterize the causal chain from GroupDRO's training objective to backbone spurious encoding change. The gates correspond to three mechanistic steps, each with an independently falsifiable prediction. Failure at any gate halts the causal argument at that step.

## 3.1 Checkpoints and Dataset

**Checkpoints.** We use the publicly available izmailovpavel/spurious\_feature\_learning checkpoints [Izmailov et al., 2022]: 12 ResNet-50 models trained on Waterbirds WILDS (3 seeds × 4 methods: ERM, SAM, GroupDRO, DFR). These checkpoints are fully trained (not early-stopped) and represent the canonical comparison set for Waterbirds robustification analysis.

**Rationale for using these checkpoints:** Matched seeds across all 4 methods enable paired statistical tests (within-seed variance controlled). This design eliminates seed-to-seed training variability from the comparison, which would otherwise inflate between-method variance.

**Dataset.** Waterbirds WILDS [Sagawa et al., 2019] provides 4,795 training and 5,794 test images of waterbirds and landbirds photographed on water and land backgrounds. The spurious correlation is strong: 95% of training waterbirds appear on water backgrounds, and 95% of landbirds on land backgrounds. The `group_array` annotation encodes background as a binary attribute (`group_array % 2`: 0 = land, 1 = water), providing ground-truth spurious attribute labels for probe training and evaluation.

## 3.2 Background Linear Probe Protocol

**Feature extraction.** For each checkpoint, we extract features from the ResNet-50 layer4 output using a forward hook with no gradient computation (`torch.no_grad()`), followed by `AdaptiveAvgPool2d(output_size=(1,1))` to produce a D=2048 feature vector per image. We evaluate on the full test set (N=5,794).

**Rationale for frozen layer4:** Layer4 is the immediate predecessor of the classification head — it is the most policy-relevant layer (the target of DFR's intervention) and is the standard choice for backbone probing in the spurious correlation literature [Kirichenko et al., 2022; Murotkar et al., 2024]. Using frozen features isolates backbone encoding from head recalibration.

**Probe classifier.** We train `sklearn.linear_model.LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)` to predict the background attribute (`group_array % 2`) from layer4 features. C=1e9 (no effective regularization) is the established convention for spurious attribute probing [Kirichenko et al., 2022; Murotkar et al., 2024] and avoids the optimizer geometry confounds that invalidated our earlier Hessian-based approach.

**Rationale for no regularization:** With D=2048 features and N=5,794 test samples, logistic regression with C=1e9 behaves as the maximum-likelihood linear classifier — it exploits all linearly separable information in the feature space. Lower C values would introduce regularization that artificially suppresses probe accuracy independent of the features' information content.

## 3.3 DFR Backbone Identity Verification (H-P0)

Before comparing backbone probe accuracy across methods, we verify the fundamental architectural assumption: DFR and ERM should share identical backbone weights at matching seeds, since DFR freezes the backbone and only retrains the head.

**Protocol.** For each of 3 seed pairs, we extract layer4 feature vectors for 50 randomly sampled test images from both the DFR and ERM checkpoints. We compute cosine similarity between DFR and ERM feature vectors for each image, then average across images (mean cosine similarity per seed pair). **Pre-registered gate:** mean cosine similarity ≥ 0.9999 for all 3 seed pairs.

**Why this matters:** If DFR backbones differ from ERM backbones (e.g., due to fine-tuning on balanced data affecting backbone weights), then comparing DFR probe accuracy to ERM would confound backbone-level changes with head-level retraining, invalidating our typology. H-P0 must pass before the backbone-vs-head distinction can be drawn.

## 3.4 Gradient Propagation Verification (H-M2)

To establish that GroupDRO's group-reweighted loss signal reaches backbone layers (not just the head), we analyze weight-level changes between GroupDRO and ERM checkpoints.

**Weight difference analysis.** For each seed, we compute L2 norms of weight differences (GroupDRO − ERM) per ResNet-50 block and layer. We compute the backbone/head ratio: L2 norm of backbone weight differences divided by L2 norm of head weight differences. **Pre-registered gate:** backbone/head ratio > 1 for all 3 seeds (backbone changes more than head, in absolute L2 terms). DFR−ERM differences serve as a negative control (should be 0.000 at all backbone layers, since DFR backbone = ERM backbone by H-P0).

**Gradient norm analysis.** We compute gradient norms at layer4 (the final backbone layer) under ERM and GroupDRO loss functions at checkpoint weights, to characterize the qualitative difference in gradient signal reaching the backbone.

**Rationale:** Weight differences provide direct, model-level evidence that GroupDRO modifies backbone weights beyond what could be attributed to random seed variation. The DFR negative control eliminates the possibility that apparent backbone changes are checkpoint-specific artifacts.

## 3.5 Primary Probe Accuracy Test (H-M3)

The primary experiment tests whether GroupDRO's backbone modification reduces background linear decodability in layer4 features.

**Protocol.** For each of 3 seed pairs (ERM₁/GroupDRO₁, ERM₂/GroupDRO₂, ERM₃/GroupDRO₃), we compute background probe accuracy as described in Section 3.2 on the full test set (N=5,794). We apply a one-sided paired t-test with n=3 seed pairs.

**Pre-registered statistical thresholds:**
- **CONFIRMED:** p < 0.05 AND Cohen's d > 0 (GroupDRO probe accuracy < ERM probe accuracy in expected direction)
- **SUGGESTIVE:** 0.05 ≤ p < 0.10 AND Cohen's d > 0.5
- **REJECTED:** p ≥ 0.10 OR wrong direction

**Rationale for one-sided test:** We have a directional prediction (GroupDRO < ERM) motivated by prior theory [Sagawa et al., 2019] and our mechanism verification (H-M2). A one-sided test is appropriate when the direction is pre-specified.

**Rationale for n=3:** The izmailovpavel checkpoints provide exactly 3 seeds per method. With n=3, one-sided t-test has sufficient power to detect large effects (d > 2.0) at the 0.05 level. H-M3's observed effect (d = 6.48) is well above this threshold.

## 3.6 WGA Correlation Analysis (H-P2, Exploratory)

As an exploratory analysis, we test whether spurious probe accuracy correlates negatively with WGA across all 9 non-DFR checkpoints (ERM × 3, GroupDRO × 3, SAM × 3).

**Protocol.** We compute Pearson r between probe accuracy values (9 data points) and WGA values from Izmailov et al. [2022] (ERM = 0.72, SAM = 0.74, GroupDRO = 0.88, each applied to all 3 seeds of the respective method). We compute 95% bootstrap confidence intervals (n_resamples = 1,000, percentile method; BCa bootstrap fails at n=9 due to degenerate distribution).

**Pre-registered gate (SHOULD_WORK):** Pearson r < −0.5. This is a less stringent gate than H-M3 (MUST_WORK) because H-P2 is exploratory — method-level WGA constants limit statistical precision.

**Limitation:** WGA values from Izmailov et al. [2022] are method-level constants (same WGA for all 3 seeds within a method), not per-seed measurements. This creates within-method collinearity that inflates bootstrap CI width. Per-seed WGA measurements would resolve this; we acknowledge this limitation explicitly.

## 3.7 Causal Chain Structure

The four experiments (H-P0, H-M1, H-M2, H-M3) form a verified causal chain:

```
GroupDRO minority upweighting (H-M1, MUST_WORK)
    → Group-balanced gradient propagates to backbone (H-M2, SHOULD_WORK)
        → Reduced background linear decodability in layer4 (H-M3, MUST_WORK)
            → Improved WGA (H-P2, SHOULD_WORK, exploratory)
```

DFR establishes the structural alternative: head recalibration on unchanged backbone features (H-P0) achieves WGA = 0.91 without any of the above chain executing. The causal chain is GroupDRO-specific; DFR operates through a structurally distinct mechanism.

This causal chain architecture was pre-registered before experiments were conducted, with gate types (MUST_WORK = non-negotiable pass required; SHOULD_WORK = non-blocking failure) specified per hypothesis. The pre-registration prevents post-hoc narrative construction from results.
