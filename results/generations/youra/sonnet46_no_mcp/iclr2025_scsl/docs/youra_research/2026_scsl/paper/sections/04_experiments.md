# 4. Experimental Setup

## 4.1 Research Questions

Our experimental design is organized around five research questions (RQs) that correspond to the sequential causal chain described in Section 3.4:

**RQ1 (H-E1 — Existence):** Does a statistically significant contiguous window of δ(t) > 0 exist during standard ERM training on Waterbirds, replicated across multiple random seeds?

**RQ2 (H-M1 — Gradient Mechanism):** Do spurious features receive measurably higher gradient signal than core features in early training, consistent with the Gradient Dominance Ratio (GDR) > 1.0?

**RQ3 (H-M2 — Feature Complexity):** Are spurious features (background texture) measurably simpler than core features (bird morphology) on at least 2 of 3 complexity metrics, each with p < 0.05?

**RQ4 (H-M3 — Transition Epoch Reproducibility):** Is the transition epoch t* identifiable with low variance across random seeds (std < 10 epochs), confirming it as a structural SGD property?

**RQ5 (H-M4 — DFR Mechanism):** Does DFR worst-group accuracy improvement correlate positively with epochs trained past t* (Pearson r > 0.7, p < 0.05)?

Each RQ maps directly to a claim in the Introduction. RQ1–RQ4 test the core causal chain; RQ5 tests the secondary mechanistic claim linking t* to practical utility.

## 4.2 Dataset

**Waterbirds** [Sagawa et al., 2020]: A spurious correlation benchmark constructed by combining CUB-200-2011 bird images with backgrounds from the Places dataset. The spurious correlation is between bird species (landbird/waterbird — the core label) and background type (land/water — the spurious label). In the training split, 95% of waterbirds appear on water backgrounds and 95% of landbirds appear on land backgrounds, creating a strong spurious correlation. The validation and test splits contain all four group combinations (spurious × core label combinations) with sufficient representation for WGA evaluation.

We use the standard Waterbirds split (4,795 training, 1,199 validation, 5,794 test images). The held-out validation split serves triple duty: (a) probe training for δ(t) measurement, (b) complexity metric evaluation on extracted patches, and (c) DFR last-layer reweighting.

**Why Waterbirds:** It is the canonical benchmark for spurious correlation methods, enabling direct comparison with JTT [Liu et al., 2021], DFR [Kirichenko et al., 2022], and GroupDRO [Sagawa et al., 2020]. Its group structure is sufficiently interpretable that we can extract spurious (background) and core (bird) image patches for complexity analysis, and we have access to both spurious and core labels for separate probe training. CelebA was planned for replication but was unavailable due to network access restrictions in the experimental environment (see Section 6.2).

## 4.3 Model

**ResNet-50** pretrained on ImageNet (torchvision standard weights). ImageNet pretraining is standard in the DFR literature and provides a rich feature initialization. The final fully-connected layer is replaced for binary classification (waterbird vs. landbird). Feature dimensionality at the penultimate layer: 2,048.

## 4.4 Training Protocol

| Hyperparameter | Value |
|---|---|
| Optimizer | SGD |
| Learning rate | 1e-3 |
| Momentum | 0.9 |
| Weight decay | 1e-4 |
| Batch size | 64 |
| Training epochs | 30 (PoC) |
| Checkpoint interval | 2 epochs |
| Random seeds | 3 (seeds 1, 2, 3) |
| Loss function | Cross-entropy (standard ERM) |

Training follows standard ERM without any group annotations, reweighting, or data augmentation beyond standard normalization. This is the baseline condition for all spurious correlation methods.

## 4.5 Baselines and Comparisons

**ERM (standard training):** The natural baseline representing the training procedure that produces spurious correlations. We report ERM WGA and average accuracy across all checkpoints.

**DFR [Kirichenko et al., 2022]:** Applied to ResNet-50 backbones trained to 5 checkpoint conditions (epochs 1, 2, 10, 20, 30). DFR protocol: refit the last linear layer using 50 balanced samples per class from the validation split (following the original DFR implementation). This tests the relationship between training depth and DFR efficacy (RQ5).

**GroupDRO [Sagawa et al., 2020]:** Reported as the group-label-supervised oracle upper bound on WGA, for context. Not directly compared against our measurement framework (different objective).

## 4.6 Evaluation Metrics

**Primary metrics for temporal gap:**
- δ(t) contiguous window fraction: proportion of training epochs where δ(t) > 0 in the longest contiguous window (threshold: ≥ 10%)
- One-sided paired t-test p-value across seeds for δ(t) > 0 in the early window (threshold: p < 0.05)
- Gap area A: sum of δ(t) × 2 over the positive window (measures cumulative spurious advantage)

**Gradient mechanism metrics:**
- GDR = mean(||∇_spurious L||) / mean(||∇_core L||) in early epochs (threshold: GDR > 1.0)
- Wilcoxon signed-rank test across early checkpoints for GDR > 1.0 (threshold: p < 0.05; acknowledged as underpowered at n=3)

**Complexity metrics:**
- FFT mean spatial frequency: spurious < core (one-sided t-test p < 0.05)
- Intra-class variance: spurious < core (one-sided t-test p < 0.05)
- Linear separability AUC: spurious > core (one-sided t-test p < 0.05)
- Success criterion: ≥ 2/3 metrics pass (SHOULD_WORK gate)

**Transition epoch metrics:**
- t* per seed (primary threshold: δ < 0.02 for 3 consecutive checkpoints)
- std(t*) across seeds (threshold: < 10 epochs)
- 95% bootstrap confidence interval for std(t*)

**DFR metrics:**
- DFR WGA (absolute) at each training checkpoint
- DFR improvement = DFR WGA − ERM WGA at each checkpoint
- Pearson r between improvement and epochs-past-t* (threshold: r > 0.7, p < 0.05)

**Worst-group accuracy** (WGA): accuracy on the minority group (landbirds on water background + waterbirds on land background), the standard evaluation metric for spurious correlation robustness.

## 4.7 Implementation

All experiments implemented in PyTorch. Linear probes implemented using scikit-learn LogisticRegression (L2 penalty, C=1.0, max_iter=1000). Gradient instrumentation hooks registered on ResNet-50 layer4 parameters. Complexity analysis conducted with numpy (FFT), scipy.stats (t-tests, Wilcoxon), and scikit-learn (logistic regression). Statistical tests: one-sided paired t-tests for directional hypotheses; bootstrap with 1000 resamples for confidence intervals. All experiments run on a single GPU (CUDA_VISIBLE_DEVICES set to single device). Code and checkpoints will be made available upon acceptance.
