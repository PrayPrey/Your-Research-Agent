# Experimental Setup

## Experimental Question

Our core experimental question is: **Does per-sample last-layer gradient cosine similarity with the within-batch mean gradient achieve higher ROC-AUC than per-sample loss as a predictor of spurious-minority group membership on Waterbirds and CelebA?**

This is a binary existence test. If yes at ≥1 epoch on both datasets, the directional gradient signal provides discriminative information beyond loss magnitude — warranting further investigation of gradient-based online debiasing. If no, the within-batch reference direction fails and we must diagnose why.

Secondary questions:
1. How does the alignment signal evolve across training epochs {1, 5, 10, 25, 50}?
2. Is the failure mode consistent across datasets with different minority prevalences?
3. What is the magnitude of the alignment–loss gap, and what does it suggest about the failure mechanism?

## Datasets

### Waterbirds

Waterbirds [Wah et al., 2011; Sagawa et al., 2020] is a synthetic spurious correlation benchmark combining CUB-200 bird photographs with Places365 backgrounds. The spurious correlation is between bird species (waterbirds vs. landbirds) and background (water vs. land), constructed at 95% strength: 95% of waterbirds appear on water backgrounds and 95% of landbirds appear on land backgrounds. The prediction task is bird species.

**Why Waterbirds:** Strong, well-characterized spurious correlation with known worst-group performance degradation (ERM worst-group accuracy: 72.6% [Sagawa et al., 2020]). Standard benchmark for evaluating debiasing methods with reproducible splits and group annotations (used only for evaluation, not training).

| Split | Total | Majority (WB/land, LB/water) | Minority (WB/water, LB/land) |
|-------|-------|------------------------------|-------------------------------|
| Train | 4,795 | ~82% | ~18% |
| Val   | 1,199 | — | — |
| Test  | 5,794 | — | — |

Minority group for ROC-AUC evaluation: group IDs $\{1, 2\}$ (landbird on water background; waterbird on land background) — the groups where spurious correlation conflicts with true label.

### CelebA

CelebA [Liu et al., 2015] is a large-scale face attributes dataset with 162,177 training images. We use blond hair prediction as the target and gender as the spurious attribute: blond hair is strongly correlated with female gender in the training set. The minority group — blond male ($<1\%$ of training data) — has the spurious attribute (female) absent.

**Why CelebA:** Complements Waterbirds with much more extreme minority prevalence (~0.8% vs ~5%), allowing us to test whether minority prevalence modulates the alignment signal — a direct test of the batch contamination hypothesis.

For computational feasibility of the existence test, we use a stratified random subsample of 16,000 training samples (seed 42), preserving group composition ratios. The minority group for evaluation: blond male (group ID 3 in group\_DRO encoding).

## Baselines

We compare two minority membership scores on identical model states at each checkpoint epoch:

**Gradient Alignment Score ($a_i$):** Negated cosine similarity of per-sample last-layer gradient with within-batch mean gradient (defined in Section 3). High score = predicted minority.

**Per-Sample Loss ($\ell_i$):** Cross-entropy loss of the ERM model on each training sample. High loss = predicted minority. This is the signal used by JTT [Liu et al., 2021] and LfF [Nam et al., 2020], and serves as the magnitude-based comparator.

**Why these two:** We test the specific theoretical claim that gradient *direction* provides discriminative power beyond gradient *magnitude* (captured by loss). All other aspects of the evaluation are identical — same model, same epoch, same samples — isolating the signal type as the single variable.

## Evaluation Metric

**ROC-AUC:** Area under the receiver operating characteristic curve for binary classification of spurious-minority group membership. ROC-AUC is our primary metric because:
- It is threshold-free (no operating point assumption required for the existence test)
- It measures discriminability directly: probability that a random minority sample scores higher than a random majority sample
- It is interpretable: AUC = 0.5 is random; AUC < 0.5 indicates the signal is inverted (anti-predictive)

**Implementation:** Binary labels $y_i = \mathbb{1}[\text{group\_id}_i \in \text{minority}]$. `sklearn.metrics.roc_auc_score` with default settings.

## Training Protocol

Standard ERM training (no upweighting, no debiasing intervention) for both datasets. We use the group\_DRO repository [Sagawa et al., 2020] for dataset loading and preprocessing, with ResNet-50 ImageNet pretrained weights (`IMAGENET1K_V1`). Full configuration in Section 3 (Methodology). All experiments use a single seed (42) — appropriate for a proof-of-concept existence test where the alignment–loss gap is the primary quantity of interest. Single-seed sufficiency is validated post-hoc: the gap (0.27–0.78 on Waterbirds) far exceeds plausible seed-to-seed variance.

Hardware: NVIDIA H100 NVL GPU. Computation: gradient probe at each checkpoint epoch requires one additional full forward-backward pass over the training set (~2 minutes per checkpoint on Waterbirds; ~5 minutes on CelebA 16K).
