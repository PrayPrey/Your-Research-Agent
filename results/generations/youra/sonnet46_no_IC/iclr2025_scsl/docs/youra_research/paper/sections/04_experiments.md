# Experimental Setup

## Research Questions

Our experimental design answers four research questions, each corresponding to one step of the verified causal chain described in Section 3.7:

**RQ1:** Does GroupDRO training create a group-reweighted gradient signal that differentially affects backbone weights compared to ERM? (Mechanism existence, H-M1/H-M2)

**RQ2:** Does DFR backbone encoding differ from ERM backbone encoding at matching seeds? (Structural typology, H-P0)

**RQ3:** Does GroupDRO layer4 background probe accuracy significantly lower than ERM (one-sided paired t-test, p < 0.05, n = 3 seeds)? (Primary claim, H-M3)

**RQ4:** Does background probe accuracy correlate negatively with WGA across robustification methods? (Exploratory, H-P2)

These questions map to Introduction claims 1–4 respectively. RQ3 is the primary claim; RQ1 and RQ2 provide mechanistic context; RQ4 connects backbone encoding to downstream performance.

## Dataset

**Waterbirds WILDS** [Sagawa et al., 2019; Koh et al., 2021]. The dataset contains 4,795 training images and 5,794 test images of waterbirds and landbirds photographed on water and land backgrounds. The spurious correlation is strong: 95% of waterbird images appear on water backgrounds and 95% of landbird images on land backgrounds.

| Split | Size | Spurious Groups |
|-------|------|-----------------|
| Train | 4,795 | 4 groups (landbird-land, landbird-water, waterbird-land, waterbird-water) |
| Test | 5,794 | Same 4 groups |
| Minority fraction | 5.01% | (landbird-water + waterbird-land) |

We use the full test set (N=5,794) for all probe accuracy evaluations. The `group_array` annotation provides binary background labels (`group_array % 2`: 0 = land background, 1 = water background).

**Why Waterbirds:** It is the canonical spurious correlation benchmark with strong background-label covariance, established evaluation conventions [Sagawa et al., 2019], and publicly available checkpoints covering all methods under study [Izmailov et al., 2022].

## Methods Studied

**ERM (Empirical Risk Minimization, baseline).** Standard cross-entropy minimization with no group information. Trains on all Waterbirds training data, exploiting background-label correlations. We treat ERM as the reference for backbone spurious encoding.

**GroupDRO** [Sagawa et al., 2019]. **Primary backbone-modification method.** Minimizes worst-group loss via exponentiated gradient ascent on group weights. Group membership is required at training time. WGA = 0.88 (Izmailov et al. [2022] values).

**DFR (Deep Feature Reweighting)** [Kirichenko et al., 2022]. **Head-recalibration reference.** Retrains only the final linear classifier on a small group-balanced held-out set, freezing all backbone weights. WGA = 0.91. DFR serves as the structural contrast: highest WGA, zero backbone modification.

**SAM (Sharpness-Aware Minimization)** [Foret et al., 2021]. **Exploratory comparison.** Minimizes loss in a neighborhood of parameter space for improved generalization. WGA = 0.74. SAM is not pre-registered for backbone modification analysis; its probe accuracy is reported as an exploratory finding.

All checkpoints from izmailovpavel/spurious\_feature\_learning [Izmailov et al., 2022]: 3 seeds × 4 methods = 12 ResNet-50 checkpoints, fully trained on Waterbirds WILDS.

## Probe Implementation

**Feature extraction.** PyTorch forward hook on ResNet-50 `layer4`, `torch.no_grad()`, `AdaptiveAvgPool2d(output_size=(1,1))`, resulting in D=2048 feature vectors per image.

**Linear probe.** `sklearn.linear_model.LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)` trained to classify background attribute from frozen layer4 features.

**Evaluation.** Probe accuracy on full test set (N=5,794). For H-M3, probe is fit on a held-out training subset and evaluated on the test set. The same protocol is applied uniformly across all methods and seeds.

## Statistical Tests

| Hypothesis | Test | n | Pre-registered Threshold |
|------------|------|---|--------------------------|
| H-P0 (DFR backbone identity) | Mean cosine similarity | 3 seed pairs, 50 images each | ≥ 0.9999 (PASS gate) |
| H-M2 (gradient propagation) | L2 weight difference ratio | 3 seeds | Backbone/head ratio > 1 |
| H-M3 (probe accuracy) | One-sided paired t-test, GroupDRO < ERM | n = 3 seed pairs | p < 0.05, d > 0 (CONFIRMED) |
| H-P2 (WGA correlation) | Pearson r, bootstrap CI | n = 9 checkpoints | r < −0.5 (SHOULD_WORK gate) |

All thresholds were pre-registered before experiments were conducted. We report CONFIRMED (p < 0.05, d > 0), SUGGESTIVE (0.05 ≤ p < 0.10, d > 0.5), or REJECTED (otherwise) for each hypothesis.

## Compute Resources

All experiments run on a single GPU (CUDA-enabled). Feature extraction requires one forward pass per checkpoint per test image — approximately 10 minutes per checkpoint on standard hardware. No new model training is conducted; we use pre-trained checkpoints exclusively.

## Reproducibility

All probe code uses scikit-learn standard implementations. Checkpoint source: izmailovpavel/spurious\_feature\_learning (GitHub). Dataset: Waterbirds WILDS v1.0 accessed via the WILDS benchmark library [Koh et al., 2021]. Cache path: standard WILDS cache structure.
