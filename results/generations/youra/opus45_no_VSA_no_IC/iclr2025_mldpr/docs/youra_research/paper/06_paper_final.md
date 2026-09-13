# Benchmark Fingerprints: Detecting Training Dataset Origin in Fine-Tuned Vision Models

---

## Abstract

Fine-tuned vision models often fail to generalize beyond their training benchmarks, yet no model-internal metric exists to detect benchmark-specific encoding before deployment. We investigate whether benchmark fingerprints — detectable signatures of training dataset origin — exist in model representations and whether they predict cross-dataset performance gaps. Using linear probing on ResNet-50 penultimate layer features, we find that fingerprints are massively detectable: a logistic regression classifier achieves 99.51% accuracy distinguishing models fine-tuned on Flowers102 versus CIFAR-100, with an effect size of Cohen's d = 698. However, the Benchmark Fingerprint Score (classifier confidence for the true benchmark) shows zero correlation with generalization gap (r = 0.022, p = 0.967). All models achieved BFS > 0.999, creating a ceiling effect that eliminates variance for correlation analysis. Our results establish benchmark fingerprints as a measurable phenomenon while demonstrating that fingerprint strength does not predict deployment risk. This paradox — perfect detectability but no predictive power — suggests that the mechanism linking benchmark concentration to generalization failure is more complex than simple spurious feature encoding. We discuss implications for representation learning evaluation and propose calibrated metrics and intervention studies as future directions.

---

## 1. Introduction

A simple linear classifier can identify which benchmark was used to fine-tune a vision model with 99.5% accuracy — yet this powerful fingerprint tells us nothing about how well the model will generalize. This paper investigates this paradox: benchmark-specific signatures are massively detectable in model representations, but their relationship to cross-dataset performance degradation is far more complex than previously assumed.

### The Benchmark Concentration Problem

The machine learning community's reliance on a small set of popular benchmarks has raised concerns about whether strong benchmark performance translates to real-world deployment success. Recht et al. (2019) demonstrated that ImageNet-trained classifiers experience 11-14% accuracy drops on carefully replicated test sets, suggesting systematic gaps between benchmark and deployment performance. D'Amour et al. (2020) attributed such failures to underspecification: models with equivalent benchmark performance can diverge dramatically under distribution shift. Wang et al. (2025) showed that ImageNet classifiers learn frequency shortcuts, encoding texture biases rather than shape information.

These findings share a common thread: fine-tuning on narrow benchmark distributions may cause models to encode spurious, benchmark-specific features rather than task-general visual concepts. However, prior work has measured generalization gaps through external evaluation alone. No model-internal metric exists to detect or quantify benchmark-specific encoding before deployment.

### Benchmark Fingerprints: A Representation-Level Analysis

We hypothesize that fine-tuning creates detectable "benchmark fingerprints" in model representations — systematic patterns that reveal training dataset origin. If such fingerprints exist, they could provide a diagnostic tool for identifying models at risk of benchmark overfitting before deployment failure occurs.

To test this hypothesis, we propose a simple methodology: train a linear classifier on penultimate layer representations to predict which benchmark was used for fine-tuning. If benchmark-specific features are encoded, the classifier should achieve above-chance accuracy. We further propose the Benchmark Fingerprint Score (BFS) — the classifier's confidence for the true benchmark — as a candidate metric for fingerprint strength.

### Contributions and Findings

Our investigation yields both a striking positive finding and an important negative result:

1. **Fingerprints are massively detectable.** A logistic regression classifier achieves 99.51% accuracy distinguishing models fine-tuned on Flowers102 versus CIFAR-100, with an effect size of Cohen's d = 698. This far exceeds our 60% threshold and establishes that benchmark fingerprints are not subtle artifacts but dominant signals in representation space.

2. **BFS does not predict generalization gap.** Despite near-perfect fingerprint detection, the correlation between BFS and cross-dataset performance gap is r = 0.022 (p = 0.967). The proposed mechanism linking fingerprint strength to generalization degradation is not supported.

3. **The paradox opens new questions.** Why are fingerprints so detectable yet so uninformative about generalization? We analyze potential explanations including BFS saturation, domain shift confounding, and the possibility that fingerprints are binary rather than graded phenomena.

---

## 2. Related Work

### Generalization Gap in Deep Learning

The disconnect between benchmark and deployment performance has been extensively documented. Recht et al. (2019) created ImageNetV2 by replicating the original data collection process and found that all tested classifiers experienced 11-14% accuracy drops. These studies measure gaps through evaluation metrics but do not identify model-internal signals that might predict or explain such gaps.

### Underspecification and Shortcut Learning

D'Amour et al. (2020) formalized underspecification as a fundamental challenge: multiple models can achieve equivalent training performance while exhibiting different behaviors under distribution shift. Wang et al. (2025) showed that ImageNet-trained CNNs learn frequency shortcuts. Our benchmark fingerprint framework generalizes this analysis, asking whether fine-tuning creates detectable signatures regardless of the specific spurious mechanism.

### Linear Probing for Representation Analysis

Linear probing has become a standard tool for understanding what information neural network representations encode (Alain & Bengio, 2017; Kornblith et al., 2019). We apply this methodology to detect benchmark identity from fine-tuned representations.

### Our Positioning

Prior work establishes that generalization gaps exist, underspecification causes divergence, and shortcuts can be domain-specific. We contribute a novel representation-level perspective: measuring benchmark fingerprints directly using linear probing. Our negative finding — that BFS does not correlate with gap — opens new research directions.

---

## 3. Methodology

### Problem Formulation

We frame benchmark fingerprint detection as a representation classification problem. Given models fine-tuned on different benchmarks, can we predict which benchmark was used from representations alone?

### Feature Extraction

We use ResNet-50 pretrained on ImageNet-1K, fine-tuned with SGD (lr=0.01, cosine annealing, 10 epochs). After fine-tuning, we extract 2048-dimensional features from the average pooling layer.

### Fingerprint Detection

We train a logistic regression classifier to predict benchmark origin:

$$\hat{y} = \text{argmax}_b \, P(b \mid \mathbf{r})$$

### Benchmark Fingerprint Score (BFS)

$$\text{BFS}(m_i) = P(b^* \mid \mathbf{r}_i)$$

where $b^*$ is the true training benchmark.

### Statistical Analysis

- **Fingerprint detection:** Classification accuracy, threshold > 60%, Cohen's d
- **BFS-Gap correlation:** Pearson r, threshold r > 0.3, p < 0.05

---

## 4. Experimental Setup

### Research Questions

- **H-E1:** Can a linear classifier predict training benchmark from representations?
- **H-M1:** Does BFS correlate with cross-dataset gap?
- **H-M2:** Do single-benchmark models show larger gaps than multi-benchmark models?

### Datasets

| Dataset | Classes | Domain |
|---------|---------|--------|
| Flowers102 | 102 | Fine-grained flowers |
| CIFAR-100 | 100 | Coarse-grained objects |

### Model Configuration

6 models (2 benchmarks × 3 seeds), ResNet-50, 10 epochs fine-tuning.

---

## 5. Results

### H-E1: Fingerprint Detection

| Metric | Value | 95% CI |
|--------|-------|--------|
| Test Accuracy | **99.51%** | [99.38%, 99.65%] |
| Cohen's d | 698.08 | — |

**Confusion Matrix:**

|  | Pred: Flowers | Pred: CIFAR-100 |
|--|---------------|-----------------|
| **Flowers** | 4,951 | 49 |
| **CIFAR-100** | 0 | 5,000 |

**Verdict: H-E1 PASS.**

### H-M1: BFS-Gap Correlation

| Model | BFS | In-Domain | Transfer | Gap |
|-------|-----|-----------|----------|-----|
| cifar100_s0 | 0.9998 | 83.0% | 38.7% | 44.3 pp |
| cifar100_s1 | 0.9999 | 73.2% | 36.6% | 36.6 pp |
| cifar100_s2 | 1.0000 | 83.6% | 40.9% | 42.7 pp |
| flowers_s0 | 0.9998 | 89.4% | 56.0% | 33.5 pp |
| flowers_s1 | 0.9999 | 89.5% | 53.0% | 36.5 pp |
| flowers_s2 | 0.9998 | 90.2% | 54.6% | 35.7 pp |

**Pearson r = 0.022, p = 0.967**

**Verdict: H-M1 FAIL.**

### H-M2: Training Regime Comparison

**Status: INCONCLUSIVE** — requires real fine-grained datasets.

### Summary

| Hypothesis | Gate | Result |
|------------|------|--------|
| H-E1 | MUST_WORK | **PASS** |
| H-M1 | SHOULD_WORK | **FAIL** |
| H-M2 | SHOULD_WORK | **INCONCLUSIVE** |

---

## 6. Discussion

### Interpreting the Existence Result

The near-perfect fingerprint classification demonstrates that fine-tuning creates highly discriminative representation signatures. The asymmetric confusion matrix suggests different benchmarks create fingerprints of varying strength.

### Why BFS Failed to Predict Gap

1. **Ceiling effect:** All models achieved BFS > 0.999
2. **Binary fingerprints:** May be presence/absence, not graded
3. **Domain shift dominance:** Gap may reflect domain distance, not fingerprints
4. **Sample size:** n=6 limits statistical power

### Limitations

- 2 benchmarks (PoC) vs. planned 5
- BFS metric saturation
- H-M2 not executed with real data
- ResNet-50 only; Transformers may differ

---

## 7. Conclusion

**Fingerprints are massively detectable.** A linear classifier identifies training benchmark origin with 99.51% accuracy (Cohen's d = 698).

**But fingerprint strength does not predict generalization gap.** The BFS-gap correlation (r = 0.022) is effectively zero.

This paradox — perfect detectability but no predictive power — points to deeper questions about what fine-tuning changes in representations. Future work should explore calibrated fingerprint metrics, layer-wise analysis, and intervention studies to establish causal fingerprint-gap relationships.

That 99.5% classification accuracy tells us models encode benchmarks. What it doesn't tell us — yet — is whether and how that encoding harms deployment.

---

## References

- Alain, G. & Bengio, Y. (2017). Understanding Intermediate Layers Using Linear Classifier Probes. *arXiv:1610.01644*
- D'Amour, A. et al. (2020). Underspecification Presents Challenges for Credibility in Modern Machine Learning. *arXiv:2011.03395*
- He, K. et al. (2016). Deep Residual Learning for Image Recognition. *CVPR*
- Koch, B. et al. (2021). Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research. *NeurIPS Datasets Track*
- Kornblith, S. et al. (2019). Do Better ImageNet Models Transfer Better? *CVPR*
- Recht, B. et al. (2019). Do ImageNet Classifiers Generalize to ImageNet? *ICML*
- Wang, H. et al. (2025). Do ImageNet-trained models learn shortcuts? *arXiv:2503.03519*

---

## Figures

**Figure 1:** Confusion matrix for benchmark fingerprint classification (H-E1). Near-perfect separation between Flowers102 and CIFAR-100 representations; CIFAR-100 features never misclassified.

**Figure 2:** BFS vs. cross-dataset gap scatter plot (H-M1). No correlation observed (r = 0.022, p = 0.967); all models cluster at BFS > 0.999.
