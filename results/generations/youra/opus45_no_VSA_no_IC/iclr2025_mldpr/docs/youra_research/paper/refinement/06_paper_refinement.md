# Benchmark Fingerprints: Detecting Training Dataset Origin in Fine-Tuned Vision Models

---

## Abstract

Fine-tuned vision models often fail to generalize beyond their training benchmarks, yet no model-internal metric exists to detect benchmark-specific encoding before deployment. This work investigates whether benchmark fingerprints—detectable signatures of training dataset origin—exist in model representations and whether they predict cross-dataset performance gaps. Using linear probing on ResNet-50 penultimate layer features, we find that fingerprints are detectable with high accuracy: a logistic regression classifier achieves 99.51% accuracy (95% CI: [99.38%, 99.65%]) distinguishing models fine-tuned on Flowers102 versus CIFAR-100, with an effect size of Cohen's d = 698.08. However, the Benchmark Fingerprint Score (BFS), defined as classifier confidence for the true benchmark, shows no correlation with generalization gap (Pearson r = 0.022, p = 0.967). All six models achieved BFS > 0.999, creating a ceiling effect that eliminates variance for correlation analysis. These results establish benchmark fingerprints as a measurable phenomenon while demonstrating that fingerprint strength, as measured by BFS, does not predict deployment risk under the tested conditions. The observed paradox—high detectability but no predictive power—suggests that the mechanism linking benchmark concentration to generalization failure may be more complex than simple spurious feature encoding, or that the BFS metric saturates before capturing meaningful variation.

---

## 1. Introduction

A linear classifier can identify which benchmark was used to fine-tune a vision model with 99.5% accuracy—yet this fingerprint provides no information about how well the model will generalize. This paper investigates this paradox: benchmark-specific signatures are highly detectable in model representations, but their relationship to cross-dataset performance degradation is not observed under the tested conditions.

### The Benchmark Concentration Problem

The machine learning community's reliance on a small set of popular benchmarks has raised concerns about whether strong benchmark performance translates to deployment success. Recht et al. (2019) demonstrated that ImageNet-trained classifiers experience 11-14% accuracy drops on carefully replicated test sets, suggesting systematic gaps between benchmark and deployment performance. D'Amour et al. (2020) attributed such failures to underspecification: models with equivalent benchmark performance can diverge dramatically under distribution shift. Koch et al. (2021) documented that ML research increasingly concentrates on fewer benchmark datasets. Wang et al. (2025) showed that ImageNet classifiers learn frequency shortcuts, encoding texture biases rather than shape information.

These findings share a common thread: fine-tuning on narrow benchmark distributions may cause models to encode spurious, benchmark-specific features rather than task-general visual concepts. However, prior work has measured generalization gaps through external evaluation alone. No model-internal metric exists to detect or quantify benchmark-specific encoding before deployment.

### Benchmark Fingerprints: A Representation-Level Analysis

We hypothesize that fine-tuning creates detectable "benchmark fingerprints" in model representations—systematic patterns that reveal training dataset origin. If such fingerprints exist, they could provide a diagnostic tool for identifying models at risk of benchmark overfitting before deployment failure occurs.

To test this hypothesis, we propose a simple methodology: train a linear classifier on penultimate layer representations to predict which benchmark was used for fine-tuning. If benchmark-specific features are encoded, the classifier should achieve above-chance accuracy. We further propose the Benchmark Fingerprint Score (BFS)—the classifier's confidence for the true benchmark—as a candidate metric for fingerprint strength.

### Contributions and Findings

This investigation yields both a positive finding and a negative result:

1. **Fingerprints are detectable with high accuracy.** A logistic regression classifier achieves 99.51% accuracy distinguishing models fine-tuned on Flowers102 versus CIFAR-100, with an effect size of Cohen's d = 698.08. This exceeds the 60% threshold and establishes that benchmark fingerprints are detectable signals in representation space.

2. **BFS does not correlate with generalization gap under tested conditions.** Despite high fingerprint detection accuracy, the correlation between BFS and cross-dataset performance gap is r = 0.022 (p = 0.967). The proposed mechanism linking fingerprint strength to generalization degradation is not supported by these data. All models achieved BFS > 0.999, which creates a ceiling effect preventing correlation analysis.

3. **The findings raise questions for future investigation.** Why are fingerprints so detectable yet uninformative about generalization under these conditions? We analyze potential explanations including BFS saturation, domain shift confounding, and the possibility that fingerprints are binary rather than graded phenomena.

---

## 2. Related Work

### Generalization Gap in Deep Learning

The disconnect between benchmark and deployment performance has been documented across multiple studies. Recht et al. (2019) created ImageNetV2 by replicating the original data collection process and found that all tested classifiers experienced 11-14% accuracy drops. These studies measure gaps through evaluation metrics but do not identify model-internal signals that might predict such gaps.

### Underspecification and Shortcut Learning

D'Amour et al. (2020) formalized underspecification as a challenge: multiple models can achieve equivalent training performance while exhibiting different behaviors under distribution shift. Wang et al. (2025) showed that ImageNet-trained CNNs learn frequency shortcuts. Hermann et al. (2020) and Geirhos et al. (2019) documented texture bias in convolutional networks. Our benchmark fingerprint framework generalizes this analysis, asking whether fine-tuning creates detectable signatures regardless of the specific spurious mechanism.

### Linear Probing for Representation Analysis

Linear probing has become a standard tool for understanding what information neural network representations encode (Alain & Bengio, 2017; Kornblith et al., 2019). We apply this methodology to detect benchmark identity from fine-tuned representations.

### Our Positioning

Prior work establishes that generalization gaps exist, underspecification causes divergence, and shortcuts can be domain-specific. We contribute a representation-level perspective: measuring benchmark fingerprints directly using linear probing. Our negative finding—that BFS does not correlate with gap under tested conditions—identifies limitations of the proposed metric and opens directions for alternative approaches.

---

## 3. Method

### Problem Formulation

We frame benchmark fingerprint detection as a representation classification problem. Given models fine-tuned on different benchmarks, can we predict which benchmark was used from representations alone?

### Feature Extraction

We use ResNet-50 (He et al., 2016) pretrained on ImageNet-1K as the base architecture. Models are fine-tuned using SGD with learning rate 0.01, momentum 0.9, and cosine annealing schedule for 10 epochs. After fine-tuning, we extract 2048-dimensional features from the average pooling layer (penultimate layer).

### Fingerprint Detection

We train a logistic regression classifier to predict benchmark origin from extracted features:

$$\hat{y} = \text{argmax}_b \, P(b \mid \mathbf{r})$$

where $\mathbf{r}$ is the feature vector and $b$ indexes the benchmark classes.

### Benchmark Fingerprint Score (BFS)

For each model $m_i$, we define the Benchmark Fingerprint Score as:

$$\text{BFS}(m_i) = P(b^* \mid \mathbf{r}_i)$$

where $b^*$ is the true training benchmark and $\mathbf{r}_i$ represents features extracted using model $m_i$.

### Generalization Gap

For each model, we compute in-domain accuracy (on the training benchmark's test set) and transfer accuracy (on the alternative benchmark's test set with a linear transfer head trained on frozen features). The gap is defined as:

$$\text{Gap} = \text{In-domain accuracy} - \text{Transfer accuracy}$$

### Statistical Analysis

- **Fingerprint detection:** Classification accuracy with 95% bootstrap confidence interval, threshold > 60% for existence claim, Cohen's d for effect size
- **BFS-Gap correlation:** Pearson correlation coefficient r, threshold r > 0.3 and p < 0.05 for mechanism claim

---

## 4. Experimental Setup

### Research Questions

Three hypotheses were tested:

- **H-E1 (Existence):** Can a linear classifier predict training benchmark from penultimate layer representations with accuracy > 60%?
- **H-M1 (Mechanism):** Does BFS correlate with cross-dataset gap (r > 0.3, p < 0.05)?
- **H-M2 (Mechanism):** Do single-benchmark models show larger gaps than multi-benchmark models (> 5 percentage points difference)?

### Datasets

| Dataset | Classes | Domain | Train Size | Test Size |
|---------|---------|--------|------------|-----------|
| Flowers102 | 102 | Fine-grained flowers | 2,040 | 6,149 |
| CIFAR-100 | 100 | Coarse-grained objects | 50,000 | 10,000 |

The original experimental design specified five fine-grained benchmarks (CUB-200, Stanford Dogs, Stanford Cars, FGVC Aircraft, Oxford Flowers) with NABirds as a held-out evaluation set. Due to scope constraints, the proof-of-concept execution used two benchmarks (Flowers102, CIFAR-100), which increases chance level from 20% to 50%.

### Model Configuration

- 6 models total: 2 benchmarks × 3 random seeds
- Architecture: ResNet-50 pretrained on ImageNet-1K
- Fine-tuning: 10 epochs, SGD, lr=0.01, momentum=0.9, cosine annealing
- Feature dimension: 2048 (avgpool layer)

### Probe Configuration

- Classifier: Logistic regression (sklearn default parameters)
- Training data: 20,000 feature vectors (5,000 per model × 4 models, using CIFAR-100 test images)
- Test data: 10,000 feature vectors (5,000 per model × 2 held-out models)

---

## 5. Results

### H-E1: Fingerprint Detection

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Test Accuracy | 99.51% | > 60% | **PASS** |
| 95% CI | [99.38%, 99.65%] | — | — |
| Cohen's d | 698.08 | — | Massive effect |
| Shuffled Baseline | 50.43% | — | Near chance |

The confusion matrix reveals asymmetric fingerprint strength:

| | Predicted: Flowers | Predicted: CIFAR-100 |
|--|-------------------|----------------------|
| **Actual: Flowers** | 4,951 | 49 |
| **Actual: CIFAR-100** | 0 | 5,000 |

CIFAR-100 features were never misclassified; 49 Flowers102 samples (0.98%) were incorrectly classified as CIFAR-100.

**Verdict: H-E1 PASS.** Benchmark fingerprints are detectable with 99.51% accuracy.

### H-M1: BFS-Gap Correlation

| Model | BFS | In-Domain Acc | Transfer Acc | Gap (pp) |
|-------|-----|---------------|--------------|----------|
| cifar100_seed0 | 0.9998 | 83.0% | 38.7% | 44.3 |
| cifar100_seed1 | 0.9999 | 73.2% | 36.6% | 36.6 |
| cifar100_seed2 | 1.0000 | 83.6% | 40.9% | 42.7 |
| flowers_seed0 | 0.9998 | 89.4% | 56.0% | 33.5 |
| flowers_seed1 | 0.9999 | 89.5% | 53.0% | 36.5 |
| flowers_seed2 | 0.9998 | 90.2% | 54.6% | 35.7 |

**Correlation Statistics:**
- Pearson r = 0.022
- p-value = 0.967
- n = 6 models

**Verdict: H-M1 FAIL.** No correlation between BFS and generalization gap was observed. All models achieved BFS > 0.999, creating a ceiling effect that prevents correlation analysis.

### H-M2: Training Regime Comparison

**Status: INCONCLUSIVE**

The infrastructure for H-M2 was implemented (9 modules covering single-benchmark training, multi-benchmark training with weighted sampling, and k-NN cross-dataset evaluation). However, the experiment was executed with synthetic random images rather than real fine-grained datasets. Near-chance accuracy (< 1%) on synthetic data prevents meaningful statistical conclusions.

### Summary

| Hypothesis | Gate | Threshold | Result | Verdict |
|------------|------|-----------|--------|---------|
| H-E1 | MUST_WORK | > 60% accuracy | 99.51% | **PASS** |
| H-M1 | SHOULD_WORK | r > 0.3, p < 0.05 | r = 0.022, p = 0.967 | **FAIL** |
| H-M2 | SHOULD_WORK | > 5 pp difference | N/A (synthetic data) | **INCONCLUSIVE** |

---

## 6. Discussion

### Interpreting the Existence Result

The 99.51% fingerprint classification accuracy demonstrates that fine-tuning creates highly discriminative representation signatures. The effect size (Cohen's d = 698.08) indicates near-complete separation between benchmark-specific representation spaces. The asymmetric confusion matrix—CIFAR-100 features never misclassified while 49 Flowers102 samples were—suggests different benchmarks create fingerprints of varying strength or distinctiveness.

This finding is consistent with the hypothesis that fine-tuning encodes benchmark-specific statistical regularities. Flowers102 contains fine-grained petal textures and natural backgrounds; CIFAR-100 contains diverse object categories at low resolution. These systematic differences produce linearly separable representations.

### Why BFS Failed to Predict Gap

Several factors may explain the null correlation:

1. **Ceiling effect:** All models achieved BFS > 0.999. With effectively zero variance in BFS, correlation is mathematically impossible. This is a metric saturation problem, not necessarily evidence against an underlying relationship.

2. **Binary fingerprints:** The fingerprint phenomenon may be presence/absence rather than graded. Once representations encode benchmark-specific patterns, additional "fingerprint intensity" may not exist.

3. **Domain shift dominance:** CIFAR-100 (coarse-grained objects) and Flowers102 (fine-grained plants) represent fundamentally different visual domains. The observed gap (33-44 percentage points) may primarily reflect domain distance rather than benchmark-specific overfitting.

4. **Sample size limitation:** With n = 6 models, statistical power for detecting moderate correlations is low. A true effect could exist but remain undetected.

### Limitations

1. **Reduced benchmark count:** The proof-of-concept used 2 benchmarks instead of the planned 5, increasing chance level from 20% to 50% and reducing the stringency of the existence test.

2. **BFS metric saturation:** The proposed BFS metric saturates at high values, preventing correlation analysis. Alternative metrics (entropy, margin, calibrated probabilities) may provide more variance.

3. **H-M2 not executed with real data:** The single vs. multi-benchmark comparison remains untested with real datasets.

4. **Single architecture:** Only ResNet-50 was tested. Vision Transformers and other architectures may exhibit different fingerprint characteristics.

5. **Domain heterogeneity confound:** Using CIFAR-100 and Flowers102—domains with substantial differences—conflates domain shift with benchmark-specific effects. Testing within a single domain (e.g., multiple fine-grained datasets) would isolate benchmark effects.

---

## 7. Conclusion

This work establishes two findings regarding benchmark fingerprints in fine-tuned vision models:

**Fingerprints are detectable with high accuracy.** A linear classifier identifies training benchmark origin from ResNet-50 penultimate layer features with 99.51% accuracy (Cohen's d = 698.08). This demonstrates that fine-tuning encodes benchmark-specific information that is linearly separable in representation space.

**The BFS metric does not predict generalization gap under tested conditions.** The correlation between Benchmark Fingerprint Score and cross-dataset performance gap is r = 0.022 (p = 0.967). The proposed mechanism linking fingerprint strength to generalization degradation is not supported by these data, though ceiling effects in BFS (all models > 0.999) prevent conclusive interpretation.

The observed paradox—high detectability but no predictive power—points to questions about what fine-tuning changes in representations and how those changes relate to deployment performance. Future work should explore calibrated fingerprint metrics that provide variance across models, layer-wise analysis to identify where fingerprints emerge, and intervention studies (e.g., representation regularization) to establish causal relationships between fingerprint strength and generalization.

The 99.51% classification accuracy demonstrates that models encode their training benchmarks. What remains to be established is whether and how that encoding relates to deployment performance.

---

## References

- Alain, G. & Bengio, Y. (2017). Understanding Intermediate Layers Using Linear Classifier Probes. arXiv:1610.01644.
- D'Amour, A. et al. (2020). Underspecification Presents Challenges for Credibility in Modern Machine Learning. arXiv:2011.03395.
- Geirhos, R. et al. (2019). ImageNet-trained CNNs are biased towards textures; increasing shape bias improves accuracy and robustness. ICLR.
- He, K. et al. (2016). Deep Residual Learning for Image Recognition. CVPR, 770-778.
- Hermann, K. et al. (2020). The Origins and Prevalence of Texture Bias in Convolutional Neural Networks. NeurIPS, 33, 19000-19015.
- Koch, B. et al. (2021). Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research. NeurIPS Datasets and Benchmarks Track.
- Kornblith, S. et al. (2019). Do Better ImageNet Models Transfer Better? CVPR, 2661-2671.
- Krizhevsky, A. (2009). Learning Multiple Layers of Features from Tiny Images. Technical Report, University of Toronto.
- Nilsback, M.-E. & Zisserman, A. (2008). Automated Flower Classification over a Large Number of Classes. ICVGIP.
- Recht, B. et al. (2019). Do ImageNet Classifiers Generalize to ImageNet? ICML, 5389-5400.
- Wang, H. et al. (2025). Do ImageNet-trained models learn shortcuts? arXiv:2503.03519.

---

## Figures

![Confusion matrix for benchmark fingerprint classification](/home/PrayPrey/YOURA_no_VSA_no_IC/opus45/TEST_mldpr/docs/youra_research/paper/figures/confusion_matrix.png)

**Figure 1:** Confusion matrix for benchmark fingerprint classification (H-E1). The classifier achieves 99.51% accuracy with asymmetric errors: CIFAR-100 representations are never misclassified, while 49/5000 (0.98%) Flowers102 samples are incorrectly classified as CIFAR-100.

![BFS vs. cross-dataset gap scatter plot](/home/PrayPrey/YOURA_no_VSA_no_IC/opus45/TEST_mldpr/docs/youra_research/paper/figures/bfs_gap_scatter.png)

**Figure 2:** BFS vs. cross-dataset gap scatter plot (H-M1). No correlation is observed (r = 0.022, p = 0.967). All models cluster at BFS > 0.999, demonstrating the ceiling effect that prevents correlation analysis. Gap values range from 33.5 to 44.3 percentage points.
