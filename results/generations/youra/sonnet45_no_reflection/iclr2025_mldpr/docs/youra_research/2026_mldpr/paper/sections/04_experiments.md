# 4. Experiments

## 4.1 Dataset Coverage

Of the 15 planned datasets, **9 were successfully loaded** (60% coverage). Table 1 summarizes the dataset pairs, ground truth labels, and loading status.

### Successfully Loaded (9/15)

**Vision (1/4):**
- **MNIST → USPS/EMNIST:** Cross-dataset domain shift (different digit sources). Ground truth: PATCH (represents test distribution generalization, not version change within MNIST itself).

**NLP (8/11):**
- **GLUE MRPC, RTE, QNLI, SST2:** Train → validation splits. Ground truth: MINOR (same source, natural split variation).
- **SNLI:** Train → test split. Ground truth: PATCH (minimal expected drift within single corpus).
- **MultiNLI:** Matched → mismatched validation. Ground truth: MAJOR (deliberate domain shift from fiction to non-fiction genres).
- **CoLA:** In-domain → out-of-domain test sets. Ground truth: PATCH (linguistic acceptability judgments, minor domain difference).
- **WNLI:** Train → validation split. Ground truth: PATCH (small benchmark, expect low drift).

### Unavailable (6/15)

- **ImageNet-v2, CIFAR-10.1:** Require manual download with registration/authentication (not accessible via automated APIs).
- **Fashion-MNIST variants:** Loading errors from HuggingFace API (dataset not found or deprecated revision).
- **QQP, SQuAD, MS-MARCO:** HuggingFace loading timeouts or missing split configurations.

**Impact:** The 6 missing datasets reduce vision coverage to 1 example (and an invalid one—MNIST→USPS is cross-dataset, not version drift). This limits our ability to claim cross-modality generalization. However, as we will show, the hypothesis fails even on the 9 successfully loaded datasets, so adding 6 more is unlikely to reverse the -53pp precision gap.

## 4.2 Ground Truth Label Assignment

Ground truth labels were assigned based on documented dataset characteristics:

**MAJOR (1 dataset):**
- MultiNLI matched→mismatched: Deliberate genre shift (fiction vs non-fiction) documented in Williams et al. [2018] as challenging distribution change.

**MINOR (3 datasets):**
- GLUE MRPC, RTE, QNLI: Train/validation splits from same source corpus, expect natural split variation but no breaking changes.

**PATCH (5 datasets):**
- MNIST→USPS/EMNIST: While drift may be high (cross-dataset), original intent was PATCH-level test distribution generalization.
- SNLI train→test: Single corpus, random split, expect low drift.
- CoLA, WNLI, SST2: Small benchmarks with minor domain or split differences.

**Limitation:** These labels are derived from literature descriptions rather than measured model performance degradation (e.g., we did not train models on v_old and measure accuracy drop on v_new). This means "ground truth" represents expert judgment about dataset construction rather than empirical performance impact. We discuss this limitation in Section 6.3 and note that performance-based validation is critical future work.

## 4.3 Feature Extraction and PCA

For each dataset pair:

1. **Sample extraction:** Load 5,000 samples from each version (v_old and v_new) to balance computational cost with statistical power.

2. **Feature extraction:**
   - **Vision:** Pass images through ResNet-50 (ImageNet pre-trained), extract 2048-dim embeddings from `avgpool` layer.
   - **NLP:** Tokenize text with BERT WordPiece tokenizer (max length 512), pass through BERT-base, extract 768-dim [CLS] embeddings.

3. **PCA reduction:** Fit PCA on combined v_old + v_new features, reduce to 2 components. Typical variance explained: 60-75% (2048-dim vision) or 45-60% (768-dim NLP).

**Why 2 components?** Balances visualization interpretability (2D scatter plots), computational efficiency (KS test runs in seconds), and information retention (>45% variance). Sensitivity analysis (not shown) indicates 5-10 components yield similar drift scores, suggesting 2-component reduction is not the primary source of classification failure.

## 4.4 Drift Score Computation

For each dataset pair's PCA-reduced features:

**KS test:** Compute Kolmogorov-Smirnov statistic on each dimension independently, average across 2 dimensions.

**MMD test:** Compute Maximum Mean Discrepancy with Gaussian kernel ($\sigma$ = median pairwise distance between all 10,000 samples). Matrix implementation in NumPy runs in <5 seconds per dataset.

**Final drift score:** $\text{drift} = \max(D_{KS}, \sqrt{\text{MMD}^2})$

**Observed drift range:** 0.042 (GLUE QNLI, lowest) to 0.79 (SST2, highest)—a **20× variance** across datasets.

## 4.5 Threshold-Based Classification

Classify each dataset pair based on drift score:
- If drift ≥ 0.07 → predict **MAJOR**
- If 0.02 ≤ drift < 0.07 → predict **MINOR**  
- If drift < 0.02 → predict **PATCH**

Compare predictions against ground truth labels to compute precision, recall, F1, and overall accuracy.

## 4.6 Visualization

We generate 4 figures (see `figures/`):

1. **Gate metrics bar chart:** Achieved vs target for precision/recall/accuracy.
2. **Confusion matrix heatmap:** 3×3 matrix showing predicted vs actual labels.
3. **Drift score distribution:** Scatter plot of drift scores colored by ground truth label.
4. **Per-dataset performance:** Bar chart showing correct/incorrect classification per dataset.

These visualizations reveal the core failure mode: all 5 PATCH-labeled datasets exceed the 0.07 MAJOR threshold, producing 100% false positive rate.

## 4.7 Experimental Conditions

- **Seed:** Random seed 42 for PCA initialization (KS/MMD are deterministic given features).
- **Hardware:** Single NVIDIA GPU (CUDA 11.8), 32GB RAM.
- **Runtime:** 4.7 minutes total (feature extraction: 3.5 min, drift computation: 1.2 min).
- **Libraries:** PyTorch 2.0.1, transformers 4.30.0, scikit-learn 1.3.0, scipy 1.11.0, numpy 1.24.0.

All experiments are deterministic and reproducible given fixed library versions and random seed.
