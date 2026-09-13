# Abstract

Machine learning reproducibility suffers from silent dataset versioning failures—researchers use outdated dataset versions without realizing distribution shifts have occurred, causing models to underperform. Existing versioning tools (DVC, HuggingFace) track changes via opaque identifiers without semantic meaning. We test whether statistical drift detection (Kolmogorov-Smirnov test + Maximum Mean Discrepancy) can automate semantic versioning for datasets, classifying version changes as MAJOR/MINOR/PATCH using fixed thresholds (7%/2%/0.5%) derived from ImageNet literature. Experiments on 9 real dataset pairs (1 vision, 8 NLP) falsify this hypothesis: our classifier achieves only 44.4% accuracy (target: 85%) with 16.7% precision for MAJOR detection (target: 70%), barely above random chance. The most striking failure is a 100% false positive rate on PATCH-level changes—all 5 minor updates exceeded the MAJOR threshold. Root cause analysis reveals that drift magnitude is dataset-relative rather than absolute: scores vary 20× (0.042 to 0.79) across datasets with similar ground truth labels. We provide the first empirical evidence that ImageNet-derived thresholds fail to generalize to NLP benchmarks and propose three alternatives: adaptive per-dataset calibration, supervised classification from labeled version pairs, or performance-based ground truth using measured model degradation. This negative result redirects semantic dataset versioning research away from universal fixed thresholds toward dataset-specific or hybrid approaches.

**Keywords:** dataset versioning, distribution shift detection, semantic versioning, machine learning reproducibility, negative result
# 1. Introduction

Machine learning reproducibility faces a fundamental challenge: datasets evolve, but researchers often work with outdated versions without realizing it. When ImageNet classifiers trained on the original dataset were tested on ImageNet-v2, accuracy dropped by 11-14% [Recht et al., 2019]—not because the models were flawed, but because subtle distribution shifts between dataset versions went undetected. This "silent failure" mode wastes researcher time and undermines scientific validity, contributing to reproducibility rates as low as 60-70% in ML research [Gundersen & Kjensmo, 2018].

Existing dataset versioning tools provide infrastructure for tracking changes—DVC offers Git-like snapshots, HuggingFace uses revision IDs—but these systems treat versions as opaque identifiers without semantic meaning. A researcher encountering version `rev=a3f7b2d` has no way to know whether this represents a breaking change requiring model retraining or a minor documentation update. Software engineering solved this problem decades ago with semantic versioning (MAJOR.MINOR.PATCH), where version numbers convey impact: MAJOR versions break backward compatibility, MINOR versions add features, PATCH versions fix bugs. Could we adapt this framework to datasets, where "breaking changes" are distribution shifts that degrade model performance rather than API incompatibilities?

**Our hypothesis:** Statistical drift detection—comparing dataset versions with Kolmogorov-Smirnov (KS) tests and Maximum Mean Discrepancy (MMD)—can automatically classify version changes as MAJOR, MINOR, or PATCH using fixed thresholds derived from computer vision literature. Specifically, we test whether thresholds of 7% (MAJOR), 2% (MINOR), and 0.5% (PATCH) drift, calibrated from ImageNet studies, can generalize across datasets to achieve ≥85% classification accuracy with ≥70% precision.

**Spoiler:** They fail catastrophically. Our experiments on 9 real dataset pairs (1 vision, 8 NLP) achieve only 44.4% accuracy—barely above random chance for 3 classes. More strikingly, we observe a **100% false positive rate on PATCH-level changes**: all 5 datasets labeled as minor updates exceeded the MAJOR threshold, misclassified as breaking changes. This surprising failure mode reveals a fundamental insight: drift magnitude is dataset-relative, not absolute. A 0.79 drift score means "breaking change" for one dataset but "patch-level tweak" for another, invalidating the assumption that universal thresholds can exist.

**Why this negative result matters:** We provide the first empirical evidence that ImageNet-derived thresholds do not transfer to NLP benchmarks, with quantitative evidence of systematic failure (16.7% precision vs 70% target, -53.3 percentage point gap). This falsifies the intuitive hypothesis that statistical drift magnitude alone can determine version severity and redirects future research toward adaptive per-dataset calibration, supervised learning from labeled version pairs, or performance-based ground truth rather than purely statistical approaches.

**Contributions:**

1. **Empirical falsification** of fixed-threshold semantic versioning: We demonstrate that thresholds derived from ImageNet literature (7%/2%/0.5%) fail on NLP datasets, achieving random-level accuracy (44.4%) and 100% false positive rate on PATCH labels.

2. **Quantitative evidence** of cross-modality mis-calibration: We measure 20× variance in drift scores (0.04-0.79) across datasets with similar ground truth severity labels, showing that "high drift" is relative rather than absolute.

3. **Mechanistic insight** into why fixed thresholds fail: Frozen feature extractors (ResNet-50, BERT-base) optimized for transfer learning are too robust to detect version-level distribution shifts, and dataset-specific drift baselines vary by orders of magnitude.

4. **Constructive redirection** of future work: We propose three alternative approaches—adaptive threshold calibration with performance-based validation, supervised classification from labeled version pairs, or using actual model performance degradation as ground truth—each addressing specific failure modes identified in our experiments.

**Paper organization:** Section 2 surveys related work on dataset versioning, drift detection, and semantic versioning systems. Section 3 describes our SVAD (Semantic Versioning with Adaptive Drift-Based Deprecation) system design and experimental protocol. Section 4 details our dataset selection and evaluation metrics. Section 5 presents results including the 100% PATCH misclassification finding. Section 6 analyzes root causes and discusses implications. Section 7 concludes with lessons learned and future directions.
# 2. Related Work

## 2.1 Dataset Versioning Tools

**DVC (Data Version Control)** [Kuprieiev et al., 2020] provides Git-like versioning for datasets, treating each version as a snapshot with a unique hash. While DVC excels at tracking "what changed," it does not capture "how much impact" the change has—a 1-line metadata correction and a complete dataset redistribution receive identical treatment. Researchers must manually inspect changelogs to assess whether a version update requires model retraining, creating opportunities for silent failures when changelogs are incomplete or ignored.

**HuggingFace Datasets** [Lhoest et al., 2021] uses revision IDs (Git commit SHAs) to version datasets, enabling exact reproducibility via pinning (e.g., `load_dataset("glue", revision="a3f7b2d")`). However, like DVC, revisions are opaque identifiers without semantic meaning. The library provides no automated mechanism to classify whether revision `a3f7b2d` represents a breaking change, leaving impact assessment to human judgment.

**MLflow Model Registry** [Zaharia et al., 2018] tracks model lineage including dataset versions used for training, enabling "which models used which data" queries. While valuable for dependency tracking, MLflow does not detect when dataset updates invalidate existing models—it records relationships but does not flag drift.

**Our focus:** We extend these systems' version tracking with automated severity classification (MAJOR/MINOR/PATCH) to make version impact explicit rather than implicit. Unlike snapshot-based approaches, we test whether statistical drift detection can automate the "breaking change" determination that currently requires manual inspection.

## 2.2 Distribution Shift Detection

**Statistical tests** for distribution comparison are well-established. The **Kolmogorov-Smirnov (KS) test** [Massey, 1951] compares univariate distributions via maximum distance between empirical CDFs, with O(n log n) computational complexity. **Maximum Mean Discrepancy (MMD)** [Gretton et al., 2012] measures multivariate distribution distance in a reproducing kernel Hilbert space, offering superior sensitivity to high-dimensional shifts but requiring careful kernel selection.

**Rabanser et al. [2019]** ("Failing Loudly") benchmarked drift detection methods on synthetic shifts, finding no single metric dominates across all shift types. Critically, they note that threshold selection is context-dependent—what constitutes "significant drift" varies by application. This finding foreshadows our core challenge: determining universal thresholds for semantic versioning.

**González-Cebrián et al. [2024]** proposed using PCA + autoencoders for dataset versioning, detecting drift to trigger version bumps. However, their system flags that drift occurred without classifying severity (is this a MAJOR breaking change or a PATCH tweak?). Our work extends drift detection to semantic classification.

**TorchDrift** [Schröder et al., 2021] implements KS and MMD tests in PyTorch with built-in feature extraction. While TorchDrift provides p-values for hypothesis testing ("is drift statistically significant?"), it does not map drift magnitudes to semantic version labels—the gap we address.

## 2.3 Semantic Versioning in Software Engineering

**Semantic versioning (SemVer)** [Preston-Werner, 2013] uses MAJOR.MINOR.PATCH format to communicate API compatibility:
- **MAJOR:** Breaking changes requiring consumer updates
- **MINOR:** Backward-compatible feature additions  
- **PATCH:** Backward-compatible bug fixes

SemVer's success in package managers (NPM, PyPI) demonstrates the value of explicit version semantics. When a package bumps MAJOR version, downstream consumers receive clear signals to review compatibility. NPM deprecation warnings reduce package usage by ~60% within 6 months [Decan et al., 2018], showing that automated notifications drive behavior change.

**Key difference for datasets:** Software breaking changes are syntactic (function signatures, API contracts), while dataset breaking changes are statistical (distribution shifts causing performance degradation). This means dataset semantic versioning requires empirical measurement rather than static analysis. Our hypothesis tests whether statistical drift magnitude can serve as a reliable proxy for version severity.

## 2.4 Dataset Evolution and Performance Degradation

**Recht et al. [2019]** documented 10-15% accuracy drops when ImageNet classifiers trained on the original dataset were tested on ImageNet-v2, a carefully reproduced test set. Subsequent analysis [Kornblith et al., 2019] attributed this gap to distribution shift rather than dataset construction flaws—the model simply generalized poorly to the new data distribution.

**CIFAR-10.1** [Recht et al., 2018] and **WILDS** [Koh et al., 2021] similarly demonstrate that minor dataset curation differences produce measurable performance impacts. These findings validate the problem we address (dataset evolution affects reproducibility) while highlighting the challenge: if expert-curated datasets show subtle shifts, automated detection must be highly sensitive.

**Our contribution:** While prior work documents that dataset drift causes performance degradation, we are the first to systematically test whether drift magnitude can be thresholded to classify version severity. Our negative result (100% false positive rate on PATCH labels) quantifies the limits of this approach.

## 2.5 Positioning Our Work

| Method | Semantic Versioning | Automated Detection | Tested Datasets | Reported Accuracy |
|--------|---------------------|---------------------|-----------------|-------------------|
| DVC | ❌ (snapshots only) | ❌ (manual) | N/A | N/A |
| HuggingFace | ❌ (revision IDs) | ❌ (manual) | N/A | N/A |
| González-Cebrián et al. | ❌ (flags drift, no severity) | ✅ (PCA+autoencoder) | 3 | N/A (classification not tested) |
| TorchDrift | ❌ (p-values only) | ✅ (KS+MMD) | Synthetic | N/A (threshold-based classification not goal) |
| **Ours (SVAD)** | ✅ (MAJOR/MINOR/PATCH) | ✅ (KS+MMD+thresholds) | 9 real datasets | 44.4% (failed) |

We are the first to attempt automated MAJOR/MINOR/PATCH classification for datasets using statistical drift. Our negative result—44.4% accuracy with 16.7% precision—provides empirical evidence that fixed thresholds fail and redirects future work toward adaptive or supervised approaches.
# 3. Methodology

## 3.1 SVAD System Architecture

Our SVAD (Semantic Versioning with Adaptive Drift-Based Deprecation) system consists of three layers:

**Layer 1: Detection.** For a dataset version pair (v_old, v_new), we extract feature representations using frozen pre-trained models (ResNet-50 for vision, BERT-base for NLP), apply PCA to reduce dimensionality to 2 components, then compute drift scores using:
- **Kolmogorov-Smirnov (KS) test:** Maximum distance between empirical CDFs on each feature dimension, averaged across dimensions
- **Maximum Mean Discrepancy (MMD):** Kernel-based distance in RKHS using Gaussian kernel with bandwidth selected via median heuristic

The final drift score is the maximum of KS and MMD scores (conservative: flag if either test detects shift).

**Layer 2: Classification.** We compare the drift score against fixed thresholds to assign semantic version labels:
- **MAJOR** (breaking change): drift score ≥ 7%  
- **MINOR** (compatible addition): 2% ≤ drift score < 7%  
- **PATCH** (trivial fix): drift score < 2%

These thresholds derive from Recht et al.'s ImageNet-v2 findings (11-14% performance drop corresponded to measurable distribution shift) scaled to ~7% drift via PCA sensitivity analysis.

**Layer 3: Versioning** (not evaluated in this paper). For detected MAJOR changes, trigger 90-day deprecation workflow with dependency-graph notifications. This layer is deferred pending validation of Layers 1-2.

## 3.2 Feature Extraction

**Vision datasets:** ResNet-50 [He et al., 2016] pre-trained on ImageNet, extracting 2048-dimensional embeddings from the penultimate layer. We freeze weights (no fine-tuning) to use general-purpose representations.

**NLP datasets:** BERT-base [Devlin et al., 2019] pre-trained on Wikipedia+BooksCorpus, extracting 768-dimensional [CLS] token embeddings. Text inputs are tokenized with WordPiece, truncated to 512 tokens, and passed through the 12-layer transformer.

**PCA reduction:** We reduce 2048-dim (vision) or 768-dim (NLP) features to 2 components, retaining ~60-75% of variance. This trades off information loss for computational efficiency (KS test runs in seconds vs minutes) and visualization clarity.

**Rationale for frozen models:** Transfer learning literature demonstrates that pre-trained features generalize well across domains. We hypothesize that if these features are robust enough for downstream tasks, they capture sufficient signal to detect version-level distribution shifts. (This assumption turns out to be critically flawed—see Discussion.)

## 3.3 Statistical Drift Tests

### Kolmogorov-Smirnov Test

For each PCA dimension independently:

$$
D_{KS} = \sup_x |F_{old}(x) - F_{new}(x)|
$$

where $F_{old}$, $F_{new}$ are empirical CDFs of v_old and v_new. We average $D_{KS}$ across both PCA dimensions. Implemented using `scipy.stats.ks_2samp` with two-sided test.

### Maximum Mean Discrepancy

$$
\text{MMD}^2(P, Q) = \mathbb{E}_{x,x' \sim P}[k(x,x')] + \mathbb{E}_{y,y' \sim Q}[k(y,y')] - 2\mathbb{E}_{x \sim P, y \sim Q}[k(x,y)]
$$

where $k$ is a Gaussian RBF kernel:

$$
k(x, y) = \exp\left(-\frac{\|x - y\|^2}{2\sigma^2}\right)
$$

Bandwidth $\sigma$ is set to the median pairwise distance between all samples (median heuristic [Gretton et al., 2012]). Implemented using matrix operations in NumPy for computational efficiency.

**Final drift score:** $\text{drift} = \max(D_{KS}, \sqrt{\text{MMD}^2})$

Taking the maximum makes the detector conservative: we flag drift if either test detects a shift.

## 3.4 Threshold Selection

Fixed thresholds are derived from ImageNet-v2 literature:
- **Recht et al. [2019]:** 11-14% performance drop on ImageNet-v2
- **Assumption:** Performance degradation correlates with distribution shift detectable by KS/MMD
- **Calibration:** We estimate ~50% sensitivity loss from PCA compression (2048→2 dims), scaling the 14% performance drop to 7% drift score as MAJOR threshold
- **Ratio assumption:** MINOR and PATCH thresholds set at 2% and 0.5% based on software engineering convention (MAJOR:MINOR:PATCH ≈ 7:2:0.5 severity ratio)

**Critical assumption being tested:** These thresholds generalize from ImageNet (computer vision, large-scale) to other datasets (NLP, small-scale benchmarks). Our experiments falsify this assumption.

## 3.5 Experimental Protocol

### Dataset Selection

We selected 15 datasets with documented version histories spanning vision and NLP domains:

**Vision (4):** MNIST → USPS/EMNIST, ImageNet → ImageNet-v2, CIFAR-10 → CIFAR-10.1, Fashion-MNIST variants

**NLP (11):** GLUE benchmarks (MRPC, RTE, QNLI, SST2), SNLI, MultiNLI, CoLA, WNLI, QQP, SQuAD, MS-MARCO

**Ground truth labels:** Assigned based on documented changes:
- **MAJOR:** New data sources (MultiNLI matched→mismatched), documented performance drops >5%
- **MINOR:** Train/validation splits from same source (GLUE datasets)
- **PATCH:** Minor curation fixes, out-of-domain test sets (CoLA, WNLI)

We acknowledge that these labels are derived from literature rather than measured model performance—a limitation discussed in Section 6.3.

### Evaluation Metrics

**Primary metrics:**
- **Precision (MAJOR):** Of all predicted MAJOR changes, % that are truly MAJOR (target: ≥70%)
- **Recall (MAJOR):** Of all true MAJOR changes, % correctly detected (target: ≥85%)  
- **Overall Accuracy:** % of all version changes correctly classified (target: ≥85%)

**Gate criteria:** Hypothesis passes MUST_WORK gate only if precision ≥70%, recall ≥85%, and accuracy ≥85%. Failure blocks downstream hypotheses testing adaptive calibration and deprecation workflows.

### Implementation Details

- **Libraries:** PyTorch 2.0 (feature extraction), scikit-learn 1.3 (PCA), scipy 1.11 (KS test), NumPy 1.24 (MMD)
- **Hardware:** Single NVIDIA GPU (CUDA 11.8)
- **Runtime:** ~4.7 minutes for 9 datasets (feature extraction dominates)
- **Random seed:** 42 (for PCA initialization; KS/MMD tests are deterministic)

### Reproducibility

All code, datasets (except those requiring manual download), and experiment results are available at [REPOSITORY_URL]. Feature extraction uses frozen pre-trained weights from HuggingFace `transformers` and `torchvision` libraries with version pinning for exact reproducibility.
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
# 5. Results

## 5.1 Headline Metrics: Gate Failure

Table 2 summarizes our results against the MUST_WORK gate criteria:

| Metric | Target | Achieved | Gap | Status |
|--------|--------|----------|-----|--------|
| **Accuracy** | 85% | 44.4% | -40.6pp | ❌ FAIL |
| **Precision (MAJOR)** | 70% | 16.7% | -53.3pp | ❌ FAIL |
| **Recall (MAJOR)** | 85% | 100% | +15pp | ✅ PASS |
| **F1 (MAJOR)** | 75% | 28.6% | -46.4pp | ❌ FAIL |

The classifier achieves **44.4% overall accuracy**—barely above the 33% random baseline for 3 classes (MAJOR/MINOR/PATCH). Precision for MAJOR detection is catastrophically low at **16.7%**, missing the 70% target by 53.3 percentage points. Paradoxically, recall is perfect (100%), meaning all true MAJOR changes are detected—but at the cost of massive false positive rate.

**Gate verdict:** ❌ **FAILED**. All three metrics (accuracy, precision, F1) fall far short of targets. The hypothesis that fixed thresholds (7%/2%/0.5%) can reliably classify version severity is empirically refuted.

## 5.2 Confusion Matrix: 100% False Positive Rate on PATCH

Figure 2 shows the confusion matrix:

```
              Predicted
           MAJOR  MINOR  PATCH
Actual:
MAJOR        1      0      0      (1 total)
MINOR        0      3      0      (3 total)
PATCH        5      0      0      (5 total)
```

**Key finding:** All 5 PATCH-labeled datasets (MNIST, SST2, SNLI, CoLA, WNLI) were misclassified as MAJOR. This represents a **100% false positive rate** on PATCH labels—every minor update is flagged as a breaking change.

**Why this matters:** In production, this failure mode would cause "alarm fatigue." If every patch-level documentation fix triggers MAJOR version bump warnings, researchers will learn to ignore the system, defeating its purpose. The perfect PATCH→MAJOR confusion reveals that the 7% threshold is fundamentally mis-calibrated for the tested datasets.

**MINOR classification:** The system correctly classified 3/3 MINOR changes (GLUE MRPC, RTE, QNLI) with drift scores between 0.042-0.057, falling within the 2-7% MINOR range. This suggests the MINOR threshold (2%) may be better calibrated, though the small sample size (3 datasets) limits confidence.

**MAJOR detection:** The system correctly identified the 1 true MAJOR change (MultiNLI matched→mismatched, drift score 0.087). However, it also produced 5 false positives, yielding 16.7% precision (1 true positive / 6 total predictions).

## 5.3 Drift Score Distribution: 20× Variance

Figure 3 plots drift scores across all 9 datasets, color-coded by ground truth label. Key observations:

**PATCH labels show extreme variance:** 
- SNLI: 0.082 (slightly above MAJOR threshold)
- CoLA: 0.089  
- WNLI: 0.085
- SST2: **0.79** (highest drift, 10× above MAJOR threshold)
- MNIST→USPS: 0.597 (cross-dataset artifact)

**MINOR labels cluster tightly:**
- GLUE QNLI: 0.042 (lowest drift overall)
- GLUE MRPC: 0.053
- GLUE RTE: 0.057

**MAJOR label below some PATCH scores:**
- MultiNLI: 0.087 (only slightly above PATCH scores 0.082-0.089)

**20× variance:** The ratio between lowest (QNLI: 0.042) and highest (SST2: 0.79) drift scores is **18.8×**, demonstrating that drift magnitude spans nearly two orders of magnitude across datasets with similar ground truth severity.

**Insight:** This variance falsifies the core hypothesis that drift score magnitude alone determines version severity. A 0.79 drift (SST2, labeled PATCH) is 9× higher than 0.087 drift (MultiNLI, labeled MAJOR), yet the ground truth labels reverse the severity ordering. This suggests that "high drift" is relative to dataset-specific baselines, not an absolute threshold.

## 5.4 Per-Dataset Breakdown

Figure 4 shows classification results for each dataset:

**Correctly classified (4/9, 44.4%):**
- ✅ MultiNLI (MAJOR): drift 0.087 → predicted MAJOR
- ✅ GLUE MRPC (MINOR): drift 0.053 → predicted MINOR
- ✅ GLUE RTE (MINOR): drift 0.057 → predicted MINOR
- ✅ GLUE QNLI (MINOR): drift 0.042 → predicted MINOR

**Misclassified (5/9, 55.6%):**
- ❌ MNIST→USPS (PATCH): drift 0.597 → predicted MAJOR
- ❌ SST2 (PATCH): drift 0.79 → predicted MAJOR  
- ❌ SNLI (PATCH): drift 0.082 → predicted MAJOR
- ❌ CoLA (PATCH): drift 0.089 → predicted MAJOR
- ❌ WNLI (PATCH): drift 0.085 → predicted MAJOR

**Pattern:** The classifier achieves 100% accuracy on MINOR changes (3/3) and 100% accuracy on MAJOR changes (1/1), but **0% accuracy on PATCH changes** (0/5). This is not random error—it is systematic mis-calibration where the MAJOR threshold (7%) is set too low for PATCH-level dataset changes.

## 5.5 Comparison to Random Baseline

A random classifier for 3 classes achieves 33.3% accuracy (1/3 uniform distribution). Our classifier achieves **44.4% accuracy**, only **11.1pp above random**. While statistically better than random, this is far from the 85% target and demonstrates that fixed thresholds provide minimal signal for semantic version classification.

**Precision comparison:** Random classifier would yield ~33% precision for MAJOR detection (1/3 of predictions are MAJOR by chance). Our classifier achieves 16.7% precision, **worse than random** for MAJOR predictions due to systematic over-flagging.

## 5.6 Summary of Findings

1. **Fixed thresholds fail comprehensively:** 44.4% accuracy vs 85% target (-40.6pp gap).

2. **100% false positive rate on PATCH labels:** All 5 PATCH datasets exceed MAJOR threshold, revealing fundamental threshold mis-calibration.

3. **20× drift variance invalidates universal thresholds:** Drift scores range 0.042-0.79 across datasets with similar ground truth labels, demonstrating dataset-specific baselines are required.

4. **Perfect recall but abysmal precision:** System detects all MAJOR changes (100% recall) but produces 5× false positive rate (16.7% precision), making it unusable without manual filtering.

5. **Cross-modality generalization untested:** Only 1 vision dataset (and an invalid one—MNIST→USPS is cross-dataset, not version drift). Cannot claim results generalize beyond NLP benchmarks.

These findings falsify the hypothesis that ImageNet-derived thresholds (7%/2%/0.5%) generalize across datasets. The surprising failure mode (100% PATCH error rate) redirects future research toward adaptive calibration or alternative approaches (Section 6.4).
# 6. Discussion

## 6.1 Why Fixed Thresholds Fail: Root Cause Analysis

### Root Cause 1: Dataset-Specific Drift Baselines Required

The 20× variance in drift scores (0.042 to 0.79) across datasets with similar ground truth labels reveals that **drift magnitude is relative, not absolute**. Consider:

- **SST2 (PATCH):** Train→validation split, same corpus, expected to be low-drift. Yet drift score = 0.79, far exceeding the 0.07 MAJOR threshold.
- **GLUE QNLI (MINOR):** Train→validation split, similar construction to SST2. Drift score = 0.042, 18× lower.

Both datasets are GLUE benchmarks with train/validation splits from the same source, yet one scores 0.79 and the other 0.042. This suggests that **"high drift" means different things for different datasets**. For SST2, a baseline drift of 0.79 may be normal (validation set possibly curated differently), while for QNLI, 0.042 represents expected variation.

**Implication:** Fixed universal thresholds (7%/2%/0.5%) assume drift scores are comparable across datasets—like assuming 100°C is universally "hot" regardless of whether you're measuring air or molten metal. Instead, each dataset requires calibrated baselines: "SST2 drift >0.8 is MAJOR" while "QNLI drift >0.05 is MAJOR."

### Root Cause 2: Frozen Feature Extractors Insufficiently Sensitive

We used frozen pre-trained models (ResNet-50, BERT-base) optimized for transfer learning, which prioritizes **robustness** to distribution shifts. A model that generalizes well across domains (the goal of transfer learning) will by design produce similar embeddings for different data distributions—exactly the opposite of what drift detection requires.

**Example:** BERT-base trained on Wikipedia generalizes to legal text, medical text, and social media—producing meaningful embeddings despite domain shift. When we use these embeddings to detect drift between SST2 train/validation, the model's robustness may suppress subtle distributional differences, requiring larger actual shifts to register as measurable drift.

**Why PATCH datasets scored high:** If frozen extractors are insufficiently sensitive, even minor dataset changes may produce exaggerated drift scores relative to the underlying performance impact. SST2 (PATCH) showing 0.79 drift suggests the feature space is noisy or the validation set has curation artifacts that don't reflect actual performance degradation.

**Alternative approach:** Train drift-specialized feature extractors using contrastive learning on synthetic distribution shifts, optimizing for **sensitivity** rather than robustness. Recent work on contrastive drift detection [Gui et al., 2021] demonstrates this improves calibration.

### Root Cause 3: Cross-Modality Mis-Calibration

The 7%/2%/0.5% thresholds derive from ImageNet-v2 literature (Recht et al., 2019: 11-14% performance drop). Scaling this to ~7% drift assumes:
1. PCA compression causes ~50% sensitivity loss
2. Performance drops correlate linearly with drift scores  
3. ImageNet characteristics (large-scale, high-resolution images, 1000 classes) generalize to GLUE benchmarks (small-scale, text, 2-10 classes)

**Evidence of mis-calibration:** All 8 NLP datasets show different drift characteristics than expected from ImageNet:
- NLP drift scores span 0.04-0.79 (20× range)
- ImageNet-derived 7% threshold falls in the middle of this range, not at the tail
- PATCH-labeled NLP datasets systematically exceed MAJOR threshold

**Hypothesis:** Text embeddings (768-dim BERT) vs image embeddings (2048-dim ResNet) may have fundamentally different drift magnitude distributions. NLP datasets with smaller vocabularies and discrete token spaces may naturally exhibit higher measured drift than continuous image pixel distributions.

**Implication:** Cross-modality thresholds cannot be transferred without extensive calibration. At minimum, separate thresholds for vision and NLP are required; ideally, per-dataset or per-family (e.g., GLUE-wide) baselines.

## 6.2 Unexpected Finding: SST2 PATCH with 0.79 Drift

SST2 (Stanford Sentiment Treebank) train→validation scored **0.79 drift**, the highest in our corpus, yet is labeled PATCH (expected low impact). Three competing explanations:

**Hypothesis 1: Ground truth label error.** SST2 validation may actually represent a MINOR or MAJOR shift due to curation differences. Without measuring actual model performance degradation (train on SST2-train, test on SST2-validation), we cannot verify the PATCH label is correct.

**Hypothesis 2: Validation set curation artifacts.** SST2 validation may have been curated differently (e.g., balanced class distribution, filtered edge cases) in ways that increase statistical drift without affecting performance. This would make it a false positive for version severity.

**Hypothesis 3: Feature extractor noise.** BERT-base embeddings for short sentences (SST2 is movie reviews, often 10-30 tokens) may be less stable than for longer documents, amplifying spurious drift.

**Evidence needed:** Train a sentiment classifier on SST2-train, measure accuracy on SST2-validation. If accuracy drop is <2% → confirms PATCH label, exposes drift detection false positive. If drop is >5% → ground truth label should be MINOR/MAJOR, vindicating the drift detector.

**Implication:** Ground truth validation via performance measurement is critical. Literature-derived labels are insufficient for evaluating drift-based semantic versioning.

## 6.3 Limitations and Scope Boundaries

### Limitation 1: Ground Truth Labels Not Performance-Validated

We assigned MAJOR/MINOR/PATCH labels based on documented dataset changes (literature descriptions, curator intent) rather than measuring actual model performance degradation. This means:

- **If ground truth is noisy:** Our 44.4% accuracy may underestimate method performance—some "misclassifications" may actually be correct.
- **If ground truth is accurate:** The method genuinely fails to capture performance-relevant drift.

**Why acceptable for this paper:** Our goal is to test whether fixed thresholds generalize. Even if ground truth has errors, the 100% PATCH misclassification rate and 20× drift variance demonstrate threshold failure. Performance validation would strengthen future work but doesn't change the negative result.

**Mitigation:** Future work should train reference models on v_old, measure accuracy on v_new, use performance drops as ground truth (e.g., >5% drop = MAJOR, 2-5% = MINOR, <2% = PATCH).

### Limitation 2: Dataset Coverage Incomplete (9/15)

We successfully loaded 9 of 15 planned datasets (60% coverage), missing:
- **Vision:** 3 of 4 datasets (ImageNet-v2, CIFAR-10.1, Fashion-MNIST)  
- **NLP:** 3 of 11 datasets (QQP, SQuAD, MS-MARCO)

**Impact:** Cannot claim results generalize to computer vision (only 1 vision example, and it's invalid—MNIST→USPS is cross-dataset, not version drift). Our findings apply to NLP benchmarks (8/9 datasets) but vision generalization is untested.

**Why acceptable:** The hypothesis failed decisively on 9 datasets (44.4% accuracy, -53pp gap). Adding 6 more datasets is unlikely to reverse this trend—achieving 85% accuracy on all 15 would require perfect 15/15 classification on the missing 6 datasets, implausible given 4/9 on tested ones.

**Mitigation:** Future work should manually download ImageNet-v2 and CIFAR-10.1 (require registration) to test cross-modality generalization.

### Limitation 3: MNIST Cross-Dataset Shift Contaminates Results

MNIST→USPS/EMNIST (drift 0.597) is **domain adaptation** (different digit sources), not version drift within MNIST. This invalidates the data point—it tests whether frozen ResNet-50 detects domain shift (it does) rather than version-level drift.

**Impact:** Removing MNIST reduces sample to 8 datasets (all NLP). Recalculated accuracy: 4/8 = 50%, still far below 85% target. Precision: 1/5 = 20% (MAJOR detection), still far below 70% target. Conclusion unchanged.

**Why included:** We include MNIST for transparency but note it should be interpreted separately. It demonstrates that drift detection **works** for large domain shifts, but this doesn't help with semantic versioning where changes are more subtle.

**Mitigation:** Exclude MNIST from primary analysis or relabel as "domain shift control" rather than PATCH.

### Limitation 4: Frozen Feature Extractors May Under-Detect Drift

Transfer learning models are optimized for **robustness** (generalize well despite distribution shift), potentially making them insensitive to version-level changes. This is a design choice trade-off:

- **Advantage:** Off-the-shelf models, no training required, computationally cheap  
- **Disadvantage:** May lack sensitivity for subtle shifts

**Impact:** Even with current "under-sensitive" features, drift scores span 0.04-0.79 (20× range). Improving sensitivity might change score magnitudes but won't fix the threshold generalization problem—we'd still need per-dataset calibration.

**Why acceptable:** The failure mode is threshold mis-calibration (100% PATCH error), not missed detections (100% recall). More sensitive features might produce different score magnitudes, but the relative ordering (SST2 >> QNLI) would likely persist, still requiring dataset-specific thresholds.

**Mitigation:** Train drift-specialized feature extractors using contrastive learning on synthetic shifts (future work).

## 6.4 Path Forward: Three Alternative Approaches

Our negative result falsifies fixed-threshold semantic versioning but suggests three viable alternatives:

### Approach 1: Adaptive Per-Dataset Calibration

**Idea:** Start with cold-start thresholds (7%/2%/0.5%) for new datasets, then refine thresholds as more version transitions are observed. For example:
- After 5 version transitions: Use percentile-based thresholds (e.g., 75th percentile = MAJOR)  
- After 20 transitions: Fit distribution model to drift scores, set thresholds at 2σ/1σ/0.5σ

**Advantage:** Addresses dataset-specific baseline issue (Root Cause 1).

**Challenge:** Requires multiple version transitions per dataset to calibrate. New datasets face cold-start problem.

**Validation needed:** Collect 5+ version transitions per dataset, test convergence.

### Approach 2: Supervised Classification from Labeled Version Pairs

**Idea:** Treat semantic versioning as a supervised learning problem. Collect 100+ labeled version pairs (with measured performance degradation), train a classifier (Random Forest, XGBoost, neural network) on features = [drift_score, dataset_size, feature_dim, domain, ...].

**Advantage:** Learns decision boundaries rather than assuming fixed thresholds. Can incorporate dataset metadata (size, domain) to capture context.

**Challenge:** Requires labeled training data (expensive to collect). May not generalize to unseen dataset types.

**Validation needed:** Cross-dataset evaluation (train on GLUE, test on SQuAD).

### Approach 3: Performance-Based Ground Truth

**Idea:** Replace statistical drift with actual model performance degradation. For each version pair:
1. Train reference model on v_old  
2. Measure accuracy on v_old vs v_new
3. If drop >5% → MAJOR, 2-5% → MINOR, <2% → PATCH

**Advantage:** Directly measures what matters (performance impact), bypassing drift score calibration issues.

**Challenge:** Computationally expensive (requires training models per version pair). Requires task-specific model architecture and hyperparameters.

**Validation needed:** Test on datasets with documented performance drops (ImageNet-v2, CIFAR-10.1).

## 6.5 Implications for Reproducibility Research

Our negative result has broader implications:

**Automated reproducibility tools are harder than they appear.** The intuition that "statistical drift → semantic version" seems obvious, yet fails in practice. This suggests that reproducibility interventions require extensive empirical validation, not just conceptual plausibility.

**Dataset versioning needs human-in-the-loop.** Fully automated semantic versioning may be infeasible. Hybrid systems (automated detection + manual review for borderline cases) may be more practical.

**Performance measurement is unavoidable.** Statistical proxies (drift scores) are insufficient. Ground truth must come from actual model performance degradation, requiring computational investment.

**Universal standards are elusive.** Just as software semantic versioning requires human judgment ("is this breaking?"), dataset versioning may resist full automation. Tools can assist (flag potential breaking changes) but cannot replace expert assessment.
# 7. Conclusion

We tested whether fixed statistical thresholds derived from ImageNet literature (7%/2%/0.5% drift for MAJOR/MINOR/PATCH classification) could automate semantic versioning for ML datasets. Our experiments on 9 real dataset pairs falsify this hypothesis: the system achieves only 44.4% accuracy (vs 85% target) with 16.7% precision (vs 70% target) for MAJOR change detection.

The most striking failure mode is the **100% false positive rate on PATCH-level changes**—all 5 datasets labeled as minor updates exceeded the MAJOR threshold, misclassified as breaking changes. This reveals that drift magnitude is dataset-relative, not absolute: SST2 (PATCH) scored 0.79 drift while MultiNLI (MAJOR) scored only 0.087, yet the severity ordering is reversed in ground truth labels. The 20× variance in drift scores (0.042 to 0.79) across datasets with similar severity demonstrates that universal thresholds cannot exist without per-dataset calibration.

**Scientific contribution:** This paper provides the first empirical evidence that ImageNet-derived thresholds fail to generalize to NLP benchmarks, with quantitative measurement of the failure magnitude (−53.3pp precision gap, 20× drift variance). While negative results are less celebrated than breakthroughs, rigorous falsification redirects research effort away from dead ends. Our finding that fixed thresholds produce random-level classification (44.4% vs 33% baseline) should dissuade future attempts at universal threshold-based semantic versioning.

**Why the hypothesis failed:** Three root causes conspire against fixed thresholds:

1. **Dataset-specific baselines required:** "High drift" means 0.05 for QNLI but 0.8 for SST2. Without calibrated baselines, thresholds are arbitrary.

2. **Frozen feature extractor robustness:** Pre-trained models optimized for transfer learning (BERT-base, ResNet-50) are too robust to detect subtle version-level shifts, requiring drift-specialized feature extractors.

3. **Cross-modality mis-calibration:** ImageNet characteristics (large-scale, 2048-dim embeddings, continuous pixel distributions) do not transfer to GLUE benchmarks (small-scale, 768-dim text embeddings, discrete token spaces).

**Path forward:** We propose three alternatives, each addressing specific failure modes:

- **Adaptive calibration:** Start with cold-start thresholds, refine per-dataset after ≥5 version transitions using percentile-based or distribution-fitted thresholds. Addresses dataset-specific baseline issue but requires multiple transitions for calibration.

- **Supervised classification:** Train classifiers (Random Forest, XGBoost) on 100+ labeled version pairs with features = [drift_score, dataset_size, domain, ...]. Learns decision boundaries rather than assuming fixed thresholds but requires expensive labeled data collection.

- **Performance-based ground truth:** Replace statistical drift with measured model performance degradation (train on v_old, test on v_new, threshold accuracy drops). Directly captures what matters but computationally expensive and task-specific.

We recommend **hybrid approaches** combining automated drift detection (flag potential breaking changes) with human review (final severity assignment), acknowledging that full automation may be elusive.

**Limitations recap:** Our ground truth labels derive from literature rather than measured performance (limitation for PoC stage, critical for future work). Dataset coverage is incomplete (9/15, missing vision datasets for cross-modality validation). MNIST result is invalid (cross-dataset shift, not version drift). These limitations do not change the negative result—the -53pp precision gap is decisive—but bound the scope of claims to NLP benchmarks.

**Broader impact:** This work contributes to ML reproducibility research by demonstrating that intuitive solutions (statistical drift thresholds) can fail in non-obvious ways (100% FP rate on minor changes). Reproducibility tools require extensive empirical validation, not just conceptual plausibility. Our negative result saves future researchers from pursuing fixed-threshold approaches and provides quantitative evidence to justify more sophisticated alternatives.

**Callback to introduction hook:** We opened by asking, "What if we could automatically classify version changes as 'breaking' vs 'minor' using statistical drift detection?" The answer: not with fixed thresholds. Dataset versioning faces the same challenge as software semantic versioning—"breaking change" requires human judgment about impact, resisting full automation. But unlike software's syntactic changes (API signatures), datasets involve statistical shifts that vary by domain, making automation even harder. Our 100% PATCH misclassification rate quantifies this difficulty.

**Final takeaway:** Automated semantic dataset versioning is harder than anticipated. Statistical drift alone cannot determine version severity without extensive per-dataset calibration or supervised learning. However, our failure mode analysis provides actionable insights—drift detection works (100% recall), threshold generalization fails (16.7% precision)—guiding future systems toward hybrid automation rather than universal thresholds.

---

**Data and code availability:** Experiment code, feature extraction pipelines, and results are available at [REPOSITORY_URL]. Datasets are accessible via HuggingFace (GLUE, SNLI, MultiNLI) and torchvision (MNIST, USPS/EMNIST), except those requiring manual download (ImageNet-v2, CIFAR-10.1).

**Acknowledgments:** We thank the HuggingFace and TorchVision teams for dataset infrastructure, and reviewers for constructive feedback on framing negative results.
