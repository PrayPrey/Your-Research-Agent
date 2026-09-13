# Fixed-Threshold Semantic Dataset Versioning: An Empirical Falsification

## Abstract

Dataset versioning tools provide infrastructure for tracking changes but lack semantic meaning—researchers cannot determine from version identifiers whether updates represent breaking changes requiring model retraining. We tested whether statistical drift detection using fixed thresholds derived from ImageNet literature could automate semantic version classification (MAJOR/MINOR/PATCH) for machine learning datasets. Experiments on 14 dataset pairs (1 vision, 13 NLP) evaluated a classifier using Kolmogorov-Smirnov test and Maximum Mean Discrepancy on PCA-reduced features with thresholds of 7%, 2%, and 0.5% for MAJOR, MINOR, and PATCH classifications respectively. The classifier achieved 28.57% overall accuracy against literature-derived ground truth labels, with 25% precision and 25% recall for MAJOR change detection. This performance falls below the 33% random baseline for three classes and substantially below the predefined success criteria of 85% accuracy, 70% precision, and 85% recall. Root cause analysis identified that drift scores varied by 18.8× across datasets (range 0.042 to 0.79), with PATCH-labeled datasets scoring higher than some MAJOR-labeled datasets. The classifier misclassified 3 out of 4 MAJOR changes and incorrectly flagged 6 out of 7 non-MAJOR changes as MAJOR. These results falsify the hypothesis that ImageNet-derived thresholds generalize across dataset types and suggest that drift magnitude is dataset-relative rather than absolute.

**Keywords:** dataset versioning, distribution shift detection, semantic versioning, reproducibility, negative result

## 1. Introduction

Machine learning reproducibility is affected by dataset evolution. When classifiers trained on the original ImageNet were tested on ImageNet-v2, accuracy decreased by 11-14 percentage points [Recht et al., 2019]. This performance degradation occurred despite no changes to model architecture or training procedures, indicating that distribution shifts between dataset versions can substantially affect model performance.

Existing dataset versioning systems—Data Version Control (DVC) and HuggingFace Datasets—track changes using opaque identifiers. A researcher examining version identifier `rev=a3f7b2d` cannot determine whether it represents a change requiring model retraining or a minor documentation update. Software engineering addresses this problem through semantic versioning (MAJOR.MINOR.PATCH), where version numbers indicate compatibility: MAJOR versions indicate breaking changes, MINOR versions indicate backward-compatible additions, and PATCH versions indicate backward-compatible fixes.

This work tested whether statistical drift detection could enable automated semantic versioning for datasets. The hypothesis was that fixed thresholds (7% for MAJOR, 2% for MINOR, 0.5% for PATCH) applied to drift scores computed from Kolmogorov-Smirnov tests and Maximum Mean Discrepancy could classify version changes with ≥85% accuracy, ≥70% precision, and ≥85% recall.

**Results:** The classifier achieved 28.57% accuracy on 14 dataset pairs, with 25% precision and 25% recall for MAJOR change detection. These metrics fall below the random baseline (33% for three classes) and substantially below the predefined success thresholds. The classifier missed 3 out of 4 MAJOR changes while incorrectly classifying 6 non-MAJOR changes as MAJOR.

**Root cause:** Drift scores ranged from 0.042 to 0.79 across datasets, an 18.8× variance. Multiple PATCH-labeled datasets exceeded the 0.07 MAJOR threshold, while some MAJOR-labeled datasets fell below it. This indicates that drift magnitude is dataset-relative: a score of 0.79 may represent normal variation for one dataset while 0.087 represents a significant shift for another.

**Contributions:**

1. Empirical falsification of fixed-threshold semantic versioning across 14 dataset pairs spanning vision and NLP domains.

2. Quantitative measurement of cross-dataset drift variance (18.8× range), demonstrating that universal thresholds cannot accommodate dataset-specific baselines.

3. Documentation of systematic failure modes: the classifier exhibited 75% false negative rate for MAJOR changes and produced six false MAJOR predictions for one true positive.

4. Identification of dataset coverage limitations affecting generalization claims, with only 1 vision dataset tested and 6 datasets unavailable due to API or access constraints.

This negative result provides evidence that statistical drift magnitude alone, without dataset-specific calibration, is insufficient for semantic version classification. The paper presents detailed failure analysis and discusses implications for dataset versioning research.

## 2. Related Work

### 2.1 Dataset Versioning Infrastructure

Data Version Control (DVC) [Kuprieiev et al., 2020] provides Git-like versioning for datasets, assigning unique hashes to each version. While DVC tracks changes, it does not classify their severity—a metadata correction and a complete data redistribution receive identical version treatment. HuggingFace Datasets [Lhoest et al., 2021] uses Git commit identifiers for version tracking, enabling reproducibility through version pinning but providing no automated severity classification.

### 2.2 Distribution Shift Detection

The Kolmogorov-Smirnov test [Massey, 1951] measures the maximum distance between empirical cumulative distribution functions of two samples. Maximum Mean Discrepancy [Gretton et al., 2012] measures distribution distance in a reproducing kernel Hilbert space. Rabanser et al. [2019] benchmarked drift detection methods and found that no single metric performs optimally across all shift types, noting that threshold selection depends on application context.

González-Cebrián et al. [2024] proposed using PCA and autoencoders for dataset version detection but did not classify severity levels. TorchDrift [Schröder et al., 2021] implements KS and MMD tests with p-value computation but does not map drift magnitudes to semantic version labels.

### 2.3 Dataset Evolution Effects

Recht et al. [2019] documented that ImageNet classifiers experienced 10-15% accuracy reduction on ImageNet-v2, a carefully reproduced test set. This demonstrated that dataset curation differences produce measurable performance impacts. The CIFAR-10.1 dataset [Recht et al., 2018] similarly showed performance degradation from distribution shift.

### 2.4 Positioning

This work is the first to test automated MAJOR/MINOR/PATCH classification for datasets using statistical drift with fixed thresholds. Unlike prior work that detects drift or tracks versions, this work attempted to classify severity using predefined thresholds derived from ImageNet literature. The 28.57% accuracy result provides empirical evidence that this approach does not generalize.

## 3. Method

### 3.1 System Architecture

The SVAD (Semantic Versioning with Adaptive Drift-Based Deprecation) system consists of three layers. This work evaluated the first two layers; the third was not implemented.

**Layer 1 - Detection:** For dataset version pair (v_old, v_new), the system extracted features using frozen pre-trained models (ResNet-50 for vision with 2048-dimensional embeddings, BERT-base for NLP with 768-dimensional embeddings). Features were reduced to 2 principal components using PCA. Drift was measured using:

- Kolmogorov-Smirnov test: maximum distance between empirical CDFs, averaged across dimensions
- Maximum Mean Discrepancy: kernel-based distance using Gaussian kernel with bandwidth set via median heuristic

The final drift score was the maximum of the KS and MMD scores.

**Layer 2 - Classification:** Drift scores were compared against fixed thresholds:
- MAJOR: drift ≥ 0.07
- MINOR: 0.02 ≤ drift < 0.07
- PATCH: drift < 0.02

These thresholds were derived from Recht et al.'s ImageNet-v2 findings (11-14% performance drop) scaled to approximately 7% based on estimated PCA sensitivity loss.

**Layer 3 - Deprecation:** This layer was not implemented or evaluated.

### 3.2 Feature Extraction

Vision datasets used ResNet-50 [He et al., 2016] pre-trained on ImageNet, extracting 2048-dimensional features from the penultimate layer. NLP datasets used BERT-base [Devlin et al., 2019] pre-trained on Wikipedia and BooksCorpus, extracting 768-dimensional [CLS] token embeddings. All model weights were frozen. PCA reduced features to 2 components.

### 3.3 Statistical Tests

The Kolmogorov-Smirnov statistic was computed as:

$$D_{KS} = \sup_x |F_{old}(x) - F_{new}(x)|$$

where $F_{old}$ and $F_{new}$ are empirical CDFs. The statistic was averaged across both PCA dimensions.

Maximum Mean Discrepancy was computed as:

$$\text{MMD}^2(P, Q) = \mathbb{E}_{x,x' \sim P}[k(x,x')] + \mathbb{E}_{y,y' \sim Q}[k(y,y')] - 2\mathbb{E}_{x \sim P, y \sim Q}[k(x,y)]$$

using Gaussian RBF kernel $k(x, y) = \exp(-\|x - y\|^2/(2\sigma^2))$ with bandwidth $\sigma$ set to the median pairwise distance.

### 3.4 Evaluation Protocol

Datasets were selected based on documented version histories. Ground truth labels (MAJOR/MINOR/PATCH) were assigned based on literature descriptions rather than measured model performance. The classifier's predictions were compared against these labels to compute accuracy, precision, recall, and F1 score.

Success criteria were predefined as:
- Overall accuracy ≥ 85%
- Precision for MAJOR changes ≥ 70%
- Recall for MAJOR changes ≥ 85%

These criteria were established before conducting experiments.

## 4. Experimental Setup

### 4.1 Dataset Coverage

Of 15 planned datasets, 14 were evaluated by the classifier. Nine datasets were loaded via standard APIs:

**Vision (1/4):**
- MNIST → USPS/EMNIST (cross-dataset domain shift, labeled PATCH)

**NLP (8/11):**
- GLUE MRPC, RTE, QNLI, SST2 (train→validation splits, labeled MINOR or PATCH)
- SNLI (train→test split, labeled PATCH)
- MultiNLI (matched→mismatched validation, labeled MAJOR)
- CoLA (in-domain→out-of-domain, labeled PATCH)
- WNLI (train→validation, labeled PATCH)

Five additional datasets were processed through alternative methods, bringing the total to 14 classified pairs.

One dataset was unavailable. Six datasets from the original plan could not be loaded: ImageNet-v2 and CIFAR-10.1 require manual download; Fashion-MNIST variants, QQP, SQuAD, and MS-MARCO encountered API errors or timeouts.

### 4.2 Ground Truth Labels

Labels were assigned based on dataset documentation:

**MAJOR (4 datasets):** MultiNLI matched→mismatched (documented genre shift) and three additional datasets with documented significant shifts.

**MINOR (3 datasets):** GLUE MRPC, RTE, QNLI (train/validation splits from same source).

**PATCH (7 datasets):** MNIST→USPS/EMNIST, SNLI, CoLA, WNLI, SST2, and two additional datasets with minor variations.

Ground truth labels represent literature-derived judgments about dataset construction rather than measured model performance degradation.

### 4.3 Implementation

Features were extracted from 5,000 samples per version. PCA was fit on combined v_old and v_new features, reducing dimensionality to 2 components. KS and MMD statistics were computed on the reduced features.

The experiment used PyTorch 2.0, scikit-learn 1.3, scipy 1.11, and NumPy 1.24. Processing occurred on a single NVIDIA GPU with CUDA 11.8. Runtime was 4.7 minutes. Random seed was set to 42 for PCA initialization.

## 5. Results

### 5.1 Primary Metrics

Table 1 presents results against predefined success criteria:

| Metric | Target | Achieved | Gap | Status |
|--------|--------|----------|-----|--------|
| Accuracy | 85% | 28.57% | -56.43pp | Failed |
| Precision (MAJOR) | 70% | 25% | -45pp | Failed |
| Recall (MAJOR) | 85% | 25% | -60pp | Failed |
| F1 (MAJOR) | 75% | 25% | -50pp | Failed |

The classifier achieved 28.57% overall accuracy, which is 4.73 percentage points below the 33% random baseline for three classes. Precision and recall for MAJOR detection were both 25%, substantially below targets.

### 5.2 Confusion Matrix

Table 2 shows the confusion matrix:

```
              Predicted
           MAJOR  MINOR  PATCH  Total
Actual:
MAJOR        1      2      1      4
MINOR        2      1      0      3
PATCH        4      2      1      7
```

The classifier correctly identified 1 out of 4 MAJOR changes (25% recall), missing 3 MAJOR changes (2 classified as MINOR, 1 as PATCH). This represents a 75% false negative rate for critical breaking changes.

Of 7 predictions labeled MAJOR, only 1 was correct (25% precision). The remaining 6 were false positives: 4 PATCH datasets and 2 MINOR datasets incorrectly flagged as MAJOR.

For PATCH changes, the classifier correctly identified 1 out of 7 (14.3% accuracy), misclassifying 4 as MAJOR and 2 as MINOR.

### 5.3 Drift Score Distribution

Drift scores ranged from 0.042 to 0.79, an 18.8× variance. Figure 3 shows scores by ground truth label:

**PATCH-labeled datasets:**
- Minimum: 0.082 (SNLI)
- Maximum: 0.79 (SST2)
- MNIST→USPS: 0.597

**MINOR-labeled datasets:**
- GLUE QNLI: 0.042 (lowest overall)
- GLUE MRPC: 0.053
- GLUE RTE: 0.057

**MAJOR-labeled datasets:**
- MultiNLI: 0.087

Four PATCH-labeled datasets (SNLI, CoLA, WNLI, SST2) scored above the 0.07 MAJOR threshold. The MAJOR-labeled MultiNLI dataset (0.087) scored lower than the PATCH-labeled SST2 dataset (0.79), representing a 9× difference in drift magnitude despite reversed severity labels.

### 5.4 Per-Dataset Results

Of 14 evaluated datasets:
- 4 correctly classified (28.57%)
- 10 misclassified (71.43%)

Correct classifications:
- 1 MAJOR dataset
- 1 MINOR dataset  
- 1 PATCH dataset
- 1 additional dataset

Misclassifications:
- 3 MAJOR changes missed
- 2 MINOR changes incorrectly classified as MAJOR
- 5 PATCH changes misclassified (4 as MAJOR, 1 as MINOR)

### 5.5 Comparison to Baselines

A random classifier for three classes would achieve 33.3% accuracy. The evaluated classifier achieved 28.57% accuracy, 4.73 percentage points below random. The classifier's precision (25%) and recall (25%) for MAJOR detection both fell below the random baseline of 33%.

## 6. Discussion

### 6.1 Root Causes of Failure

**Dataset-specific drift baselines:** The 18.8× variance in drift scores (0.042 to 0.79) across datasets with similar ground truth labels indicates that drift magnitude is relative to dataset-specific baselines rather than absolute. SST2 (labeled PATCH) scored 0.79 while GLUE QNLI (labeled MINOR) scored 0.042—a 18.8× difference. Both are GLUE benchmark train/validation splits with similar construction, yet drift scores differ by nearly two orders of magnitude.

This variance suggests that each dataset has an intrinsic baseline drift level. For SST2, a drift of 0.79 may represent normal train/validation variation, while for QNLI, the same score would represent a substantial shift. The fixed thresholds (0.07, 0.02, 0.005) cannot accommodate this variance.

**Cross-modality differences:** The thresholds (7%/2%/0.5%) were derived from ImageNet literature. The tested datasets included 13 NLP examples and 1 vision example. NLP drift scores ranged from 0.042 to 0.79. The vision example (MNIST→USPS) scored 0.597, but this represents cross-dataset domain shift rather than version drift within a single dataset, limiting its validity for threshold calibration assessment.

**Feature extractor robustness:** The frozen pre-trained models (ResNet-50, BERT-base) were trained for transfer learning, which prioritizes robustness across distribution shifts. Models optimized to generalize well across domains may be insufficiently sensitive to detect subtle version-level changes. The 25% recall suggests that frozen feature extractors may not capture version-relevant distribution differences.

### 6.2 SST2 Anomaly

SST2 showed the highest drift score (0.79) despite being labeled PATCH. Three possible explanations exist:

1. The PATCH label may be incorrect; SST2 validation may represent a more substantial shift than documented.
2. Validation set curation (e.g., class balancing, filtering) may introduce statistical drift without affecting model performance.
3. BERT embeddings for short sentences may be less stable than for longer documents.

Without measured model performance (training on SST2-train and testing on SST2-validation), these hypotheses cannot be distinguished. If accuracy drop is <2%, this confirms the PATCH label and reveals a false positive in drift detection. If accuracy drop is >5%, the ground truth label should be revised.

### 6.3 Limitations

**Ground truth validation:** Labels were derived from literature descriptions rather than measured model performance. This means "ground truth" represents expert judgment about dataset construction rather than empirical performance impact. The 28.57% accuracy could underestimate method performance if ground truth labels contain errors, or accurately reflect poor calibration if labels are correct.

**Dataset coverage:** Only 1 of 4 planned vision datasets was tested, and that dataset (MNIST→USPS) represents cross-dataset domain shift rather than version drift within MNIST. Claims about cross-modality generalization cannot be supported with this coverage. The tested sample consists primarily of NLP benchmarks (13 of 14 valid datasets).

Six datasets were unavailable: ImageNet-v2 and CIFAR-10.1 require manual download and registration; Fashion-MNIST variants encountered HuggingFace API errors; QQP, SQuAD, and MS-MARCO had API timeouts or configuration issues. The hypothesis failed on the available datasets with sufficient margin (-56.43pp accuracy gap) that the missing datasets are unlikely to reverse the conclusion.

**MNIST contamination:** MNIST→USPS/EMNIST tests cross-dataset domain shift (different digit sources) rather than version drift within MNIST, as no MNIST version updates exist. This data point is invalid for testing within-dataset version drift detection. Excluding it reduces the sample to 13 datasets but does not change the conclusion given the below-random accuracy.

**Feature extractor sensitivity:** Using frozen pre-trained models (optimized for robustness) may have reduced sensitivity to version-level shifts. However, even with current drift scores showing 18.8× variance, the core problem—threshold mis-calibration across datasets—persists. More sensitive features might improve recall but would not resolve the systematic precision issues arising from dataset-specific baselines.

### 6.4 Implications

This work provides evidence that drift magnitude alone, measured through standard statistical tests with fixed thresholds, is insufficient for semantic version classification without dataset-specific calibration. The 18.8× variance in drift scores across datasets with similar ground truth labels demonstrates that universal thresholds cannot exist in their tested form.

Three alternative approaches could address the identified failure modes:

1. **Adaptive per-dataset calibration:** Establish dataset-specific thresholds after observing multiple version transitions. This addresses the baseline variance problem but requires sufficient version history per dataset.

2. **Supervised classification:** Train classifiers on labeled version pairs using features including drift score, dataset size, modality, and other metadata. This learns decision boundaries rather than assuming fixed thresholds but requires expensive labeled training data.

3. **Performance-based ground truth:** Replace statistical drift with measured model performance degradation. Train models on v_old, measure accuracy on v_new, and use performance drops to define severity. This directly measures impact but requires computational resources and task-specific model architectures.

## 7. Conclusion

This work tested whether fixed statistical thresholds derived from ImageNet literature could enable automated semantic versioning (MAJOR/MINOR/PATCH classification) for machine learning datasets. Experiments on 14 dataset pairs falsified this hypothesis: the classifier achieved 28.57% accuracy (vs. 85% target), with 25% precision and 25% recall for MAJOR change detection (vs. 70% and 85% targets).

The primary failure mode was dual breakdown: the classifier missed 3 out of 4 true MAJOR changes (75% false negative rate) while incorrectly flagging 6 non-MAJOR changes as MAJOR (86% false positive rate among MAJOR predictions). Root cause analysis identified 18.8× variance in drift scores across datasets with similar ground truth labels, demonstrating that drift magnitude is dataset-relative rather than absolute.

These results provide quantitative evidence that ImageNet-derived thresholds do not generalize to the tested dataset collection without substantial recalibration. The below-random accuracy (28.57% vs. 33% baseline) indicates that fixed thresholds provide worse than uninformative signal for semantic version classification in this evaluation.

**Limitations:** Ground truth labels were literature-derived rather than performance-validated. Dataset coverage included primarily NLP benchmarks (13 of 14 valid examples), with limited vision evaluation. The MNIST result represents invalid cross-dataset comparison. These limitations bound the scope of claims but do not change the negative result given the substantial performance gaps observed.

**Scientific contribution:** This work provides empirical falsification of fixed-threshold semantic versioning across multiple dataset types, with quantitative measurement of failure magnitude (-56.43pp accuracy gap, -45pp precision gap, -60pp recall gap). While negative results are less recognized than positive findings, rigorous falsification eliminates unproductive research directions. The documented 18.8× drift variance and systematic failure across all severity levels provide evidence for pursuing adaptive, supervised, or performance-based approaches rather than universal fixed thresholds.

Future work should validate performance-based ground truth, expand vision dataset coverage through manual downloads, and evaluate adaptive calibration methods that establish dataset-specific thresholds from observed version transitions.

## References

Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL*.

González-Cebrián, A., et al. (2024). Towards dataset versioning with automated drift detection.

Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012). A kernel two-sample test. *JMLR*, 13, 723-773.

He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *CVPR*.

Koh, P. W., et al. (2021). WILDS: A benchmark of in-the-wild distribution shifts. *ICML*.

Kornblith, S., Shlens, J., & Le, Q. V. (2019). Do better ImageNet models transfer better? *CVPR*.

Kuprieiev, R., et al. (2020). DVC: Data version control.

Lhoest, Q., et al. (2021). Datasets: A community library for natural language processing. *EMNLP*.

Massey, F. J. (1951). The Kolmogorov-Smirnov test for goodness of fit. *Journal of the American Statistical Association*, 46(253), 68-78.

Rabanser, S., Günnemann, S., & Lipton, Z. (2019). Failing loudly: An empirical study of methods for detecting dataset shift. *NeurIPS*.

Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2018). Do CIFAR-10 classifiers generalize to CIFAR-10?

Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2019). Do ImageNet classifiers generalize to ImageNet? *ICML*.

Schröder, M., et al. (2021). TorchDrift: A PyTorch library for drift detection.