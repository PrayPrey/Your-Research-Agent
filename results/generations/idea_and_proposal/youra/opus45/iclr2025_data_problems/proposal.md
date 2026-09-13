# Research Proposal: Proactive Memorization Risk Screening via Data-Intrinsic Features for Foundation Model Training

## 1. Title

**AC-PMRS: A Data-Centric Framework for Proactive Copyright Risk Mitigation in Foundation Model Training Through Memorization Prediction**

---

## 2. Introduction

### 2.1 Background

Foundation models (FMs) have revolutionized machine learning, demonstrating remarkable capabilities across natural language processing, code generation, and multimodal reasoning. However, their training on massive web-scale corpora introduces significant legal and ethical challenges, particularly concerning the memorization and potential reproduction of copyrighted content. Recent high-profile lawsuits against major AI companies underscore the urgency of addressing these copyright concerns, with plaintiffs demonstrating that large language models can reproduce verbatim passages from copyrighted books, articles, and code repositories.

The current paradigm for addressing memorization-related copyright issues is fundamentally reactive. Existing approaches, such as the DE-COP detection framework, identify memorized content only after model training is complete. This post-hoc detection strategy presents several critical limitations: (1) remediation through model retraining or fine-tuning is computationally expensive, often requiring millions of GPU-hours; (2) machine unlearning techniques remain imperfect and may degrade model performance; and (3) legal liability may already be established by the time memorization is detected. These limitations create an urgent need for proactive approaches that can identify and mitigate copyright risks before they materialize in trained models.

Recent advances in data attribution methods, particularly the LoGra (Low-rank Gradient) framework, have enabled efficient identification of training samples that disproportionately influence model outputs. LoGra achieves a 6,500× throughput improvement over traditional influence function methods, making large-scale attribution computationally feasible. Concurrently, mechanistic studies have established causal links between data characteristics—particularly structural repetition and n-gram uniqueness—and memorization propensity. These developments create an unprecedented opportunity to predict memorization risk from data-intrinsic features before training begins.

### 2.2 Research Objectives

This research proposes the **Attributed-Calibrated Proactive Memorization Risk Screening (AC-PMRS)** framework, which shifts copyright protection from reactive detection to proactive prevention. Our primary objectives are:

1. **Develop a memorization risk predictor** that uses data-intrinsic features (n-gram uniqueness, structural repetition patterns, verbatim overlap scores) to classify training samples by their memorization potential before model training.

2. **Validate the causal mechanism** linking data characteristics to memorization risk through systematic empirical analysis using LoGra attribution scores as ground-truth labels.

3. **Demonstrate practical impact** by showing that proactive filtering of high-risk samples significantly reduces copyright detection rates while preserving training data quality and model performance.

### 2.3 Research Significance

This research addresses a critical gap in the foundation model development pipeline with significant implications across multiple dimensions:

**Scientific Contribution:** We establish the first empirically-validated framework for predicting memorization risk from pre-training data characteristics, advancing our understanding of the data-model interaction dynamics that drive memorization.

**Practical Impact:** AC-PMRS enables scalable, legally-compliant data curation by integrating seamlessly into existing preprocessing pipelines, potentially saving organizations millions of dollars in remediation costs and legal exposure.

**Societal Benefit:** By facilitating proactive copyright protection, this research supports the sustainable development of AI systems that respect intellectual property rights while maintaining the data diversity necessary for capable foundation models.

---

## 3. Methodology

### 3.1 Research Design Overview

Our methodology follows a three-phase approach: (1) feature engineering and extraction, (2) classifier development and validation, and (3) downstream impact evaluation. We formalize the core hypothesis as:

**Hypothesis H-ACPMRS-v1:** Under conditions where training data can be characterized by data-intrinsic features, if we train a classifier on LoGra attribution scores as memorization labels, then we can predict memorization risk before training with precision ≥0.80 and recall ≥0.70, because data-intrinsic features correlate with memorization potential as causally validated by mechanistic studies.

### 3.2 Data Collection and Preparation

#### 3.2.1 Calibration Dataset

We construct a calibration dataset from publicly available training corpora used for Llama-family models, comprising approximately 1 billion tokens of English text. The dataset includes:

- **RedPajama-v2:** A diverse web corpus with known provenance
- **The Pile:** Academic and technical documents with varying copyright status
- **Books3 subset:** Literary content with documented copyright concerns

For each sample $s_i$ in the calibration set $\mathcal{D} = \{s_1, s_2, ..., s_N\}$, we obtain LoGra attribution scores using the LogIX framework with Llama3-8B as the reference model.

#### 3.2.2 Ground-Truth Label Generation

We define memorization risk labels based on LoGra attribution score distribution:

$$y_i = \begin{cases} 1 & \text{if } \text{LoGra}(s_i) \geq \tau_{90} \\ 0 & \text{otherwise} \end{cases}$$

where $\tau_{90}$ represents the 90th percentile of attribution scores, identifying the top 10% highest-influence samples as "high memorization risk."

### 3.3 Feature Engineering

We extract three categories of data-intrinsic features for each sample $s_i$:

#### 3.3.1 N-gram Uniqueness Features

For n-grams of order $k \in \{1, 2, 3, 4, 5\}$, we compute:

$$U_k(s_i) = \frac{|\{g : g \in \text{ngrams}_k(s_i), \text{count}(g, \mathcal{D}) = 1\}|}{|\text{ngrams}_k(s_i)|}$$

This measures the proportion of n-grams in sample $s_i$ that appear exactly once in the corpus, capturing lexical uniqueness that may promote memorization.

#### 3.3.2 Structural Repetition Index

We quantify structural patterns using:

$$R(s_i) = \frac{1}{|\mathcal{P}|} \sum_{p \in \mathcal{P}} \frac{\text{matches}(p, s_i)}{\text{len}(s_i)}$$

where $\mathcal{P}$ is a set of regular expressions capturing common structural patterns (LaTeX equations, XML/HTML tags, code syntax, citation formats). High structural repetition has been causally linked to increased memorization propensity.

#### 3.3.3 Verbatim Overlap Score

We compute Jaccard similarity against a reference database of known copyrighted content $\mathcal{C}$:

$$V(s_i) = \max_{c \in \mathcal{C}} \frac{|\text{shingles}(s_i) \cap \text{shingles}(c)|}{|\text{shingles}(s_i) \cup \text{shingles}(c)|}$$

using character-level 10-shingles. Samples with $V(s_i) \geq 0.8$ are flagged as having high verbatim overlap.

#### 3.3.4 Feature Vector Construction

The complete feature vector for sample $s_i$ is:

$$\mathbf{x}_i = [U_1(s_i), U_2(s_i), U_3(s_i), U_4(s_i), U_5(s_i), R(s_i), V(s_i), \text{len}(s_i), \text{entropy}(s_i)]$$

All features are normalized to $[0, 1]$ using min-max scaling computed on the training partition.

### 3.4 Classifier Development

#### 3.4.1 Model Architecture

We employ a gradient boosted decision tree ensemble (XGBoost) as our primary classifier due to its interpretability and strong performance on tabular features:

$$\hat{y}_i = \sigma\left(\sum_{m=1}^{M} f_m(\mathbf{x}_i)\right)$$

where $f_m$ represents individual decision trees and $\sigma$ is the sigmoid function. We also evaluate neural network baselines (2-layer MLP with 128 hidden units) for comparison.

#### 3.4.2 Training Procedure

The classifier is trained using binary cross-entropy loss with class weighting to address label imbalance:

$$\mathcal{L} = -\frac{1}{N} \sum_{i=1}^{N} \left[ w_1 \cdot y_i \log(\hat{y}_i) + w_0 \cdot (1-y_i) \log(1-\hat{y}_i) \right]$$

where $w_1 = 9$ and $w_0 = 1$ reflect the 10% positive class prevalence.

#### 3.4.3 Hyperparameter Optimization

We perform Bayesian optimization over:
- Number of estimators: $M \in [100, 1000]$
- Maximum depth: $d \in [3, 10]$
- Learning rate: $\eta \in [0.01, 0.3]$
- Minimum child weight: $\gamma \in [1, 10]$

### 3.5 Experimental Design

#### 3.5.1 Experiment 1: Correlation Validation (SH1)

**Objective:** Verify that data-intrinsic features significantly correlate with LoGra attribution scores.

**Method:** Compute Spearman rank correlation $\rho$ between each feature and LoGra scores across the calibration dataset.

**Success Criterion:** At least 3 features achieve $|\rho| > 0.3$ with $p < 0.001$.

**Falsification:** No feature achieves $|\rho| > 0.15$ (p > 0.10), indicating memorization is independent of data characteristics.

#### 3.5.2 Experiment 2: Classifier Performance (H-M2)

**Objective:** Evaluate AC-PMRS classifier against precision and recall targets.

**Method:** 5-fold stratified cross-validation with $n \geq 100$ samples per class in each fold.

**Metrics:**
- Precision: $P = \frac{TP}{TP + FP}$
- Recall: $R = \frac{TP}{TP + FN}$
- F1-Score: $F_1 = \frac{2PR}{P+R}$
- ROC-AUC

**Success Criterion:** Precision ≥ 0.80, Recall ≥ 0.70, ROC-AUC ≥ 0.85.

**Statistical Validation:** Bootstrap confidence intervals (1000 iterations) with 95% CI reported.

#### 3.5.3 Experiment 3: Mechanism Validation (H-M1)

**Objective:** Confirm that high structural repetition causally promotes memorization.

**Method:** Stratify samples by structural repetition quartiles and compare mean LoGra attribution scores using Welch's t-test.

**Success Criterion:** Top quartile samples have ≥2× higher mean attribution than bottom quartile ($p < 0.01$).

#### 3.5.4 Experiment 4: Downstream Impact (H-M3)

**Objective:** Demonstrate that AC-PMRS filtering reduces copyright detection rates.

**Method:** 
1. Train two Llama3-8B models: one on full data, one on data filtered by AC-PMRS (removing top 5% risk samples)
2. Evaluate both models using DE-COP copyright detection benchmark
3. Compare detection rates and model performance (perplexity, downstream task accuracy)

**Success Criterion:** ≥30% reduction in DE-COP detection rate with <5% perplexity increase.

#### 3.5.5 Experiment 5: Baseline Comparison (SH3)

**Objective:** Demonstrate AC-PMRS superiority over simple baselines.

**Baselines:**
- Random filtering (5% random removal)
- N-gram matching only (threshold-based filtering on $U_3$)
- Verbatim overlap only (threshold-based filtering on $V$)

**Method:** Compare precision, recall, and downstream impact across all methods.

### 3.6 Evaluation Metrics Summary

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Precision | ≥ 0.80 | 5-fold CV with bootstrap CI |
| Recall | ≥ 0.70 | 5-fold CV with bootstrap CI |
| ROC-AUC | ≥ 0.85 | 5-fold CV |
| DE-COP Reduction | ≥ 30% | Pre/post filtering comparison |
| Perplexity Degradation | < 5% | Held-out validation set |
| Feature Correlation | ρ > 0.30 | Spearman correlation |

### 3.7 Implementation Details

**Computational Resources:** Feature extraction requires approximately 1 GPU-day on A100; classifier training requires 2 CPU-hours; model retraining for downstream evaluation requires 8 GPU-days.

**Software Stack:** PyTorch for model training, LogIX for LoGra computation, XGBoost for classification, HuggingFace Transformers for Llama3-8B.

**Reproducibility:** All code, features, and trained classifiers will be released under Apache 2.0 license with W3C PROV-compliant metadata.

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome:** We expect the AC-PMRS classifier to achieve precision of 0.82 ± 0.04 and recall of 0.73 ± 0.05 (95% CI), successfully identifying high-memorization-risk samples before training. Feature importance analysis will reveal that structural repetition index ($R$) and trigram uniqueness ($U_3$) are the strongest predictors, contributing approximately 60% of predictive power.

**Secondary Outcomes:**
1. Filtering the top 5% highest-risk samples will reduce DE-COP copyright detection rates by 35-40% while maintaining model perplexity within 3% of the unfiltered baseline.
2. The correlation analysis will establish $\rho > 0.35$ between structural repetition and LoGra attribution, providing empirical validation of the causal mechanism.
3. AC-PMRS will outperform simple n-gram matching baselines by 15-20% in precision while maintaining comparable recall.

### 4.2 Scientific Impact

This research establishes the first empirically-validated framework for predicting memorization risk from data characteristics, contributing to our fundamental understanding of how foundation models interact with training data. The validated causal mechanism—linking structural repetition to memorization propensity—provides actionable insights for future data curation research and informs theoretical models of neural network memorization.

### 4.3 Practical Impact

**For AI Practitioners:** AC-PMRS provides a drop-in solution for existing data curation pipelines, enabling proactive copyright risk management without requiring model architecture changes or post-hoc remediation.

**For Organizations:** By preventing copyright violations before they occur, AC-PMRS potentially saves millions of dollars in legal costs and retraining expenses while enabling continued use of diverse training data.

**For the Research Community:** The released classifier, features, and evaluation framework establish a benchmark for future work on proactive memorization mitigation.

### 4.4 Societal Impact

This research supports the sustainable development of AI systems that respect intellectual property rights. By enabling proactive copyright protection, AC-PMRS helps balance the competing interests of AI advancement and content creator rights, contributing to a more equitable AI ecosystem. The framework also provides a template for addressing other data-related concerns (privacy, fairness) through proactive screening approaches.

### 4.5 Limitations and Future Work

We acknowledge several limitations: (1) the current framework focuses on English text and may require adaptation for multilingual or multimodal settings; (2) paraphrased copyrighted content may evade detection; (3) model-specific calibration may be needed for non-Llama architectures. Future work will extend AC-PMRS to multimodal foundation models, develop paraphrase-aware features, and investigate transfer learning approaches for cross-architecture generalization.

---

**Word Count:** ~2,100 words