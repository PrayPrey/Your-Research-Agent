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
