# Research Proposal: Contamination-Aware Training Data Attribution for Trustworthy Machine Learning at Scale

## 1. Introduction

### 1.1 Background

Modern machine learning systems achieve remarkable capabilities through training on internet-scale datasets containing billions of examples collected from diverse and often uncontrolled sources. However, this scale introduces a critical challenge: **data contamination**—the inadvertent overlap between training and test data that inflates performance metrics and produces misleading model explanations. Recent studies have documented widespread contamination in popular benchmarks, with some datasets exhibiting train-test leakage rates exceeding 10%, fundamentally undermining our ability to assess true model capabilities.

Simultaneously, the need for **training data attribution**—tracing model predictions back to influential training examples—has become paramount for multiple stakeholders. Regulatory frameworks like GDPR Article 22 mandate explanations for automated decisions, requiring practitioners to identify which training examples shaped specific predictions. Researchers need attribution methods to understand how dataset composition influences model behavior, detect benchmark contamination, and curate high-quality training data. Recent algorithmic innovations, particularly TRAK (Park et al., 2023) and LoRIF (Kwon et al., 2026), have achieved O(n) scalability for gradient-based attribution, making influence estimation feasible for datasets with millions of examples.

However, a critical gap exists at the intersection of these two challenges: **existing attribution methods implicitly assume clean training data**. When practitioners apply TRAK or similar methods to contaminated datasets, the resulting attributions reflect circular memorization rather than genuine learning—a test example is "explained" by a nearly identical training example, providing no insight into model generalization. This creates a validity crisis: users cannot distinguish trustworthy attributions from contamination-induced artifacts.

### 1.2 Research Problem

The fundamental tension is between **scalability and validity** in training data attribution. Current state-of-the-art methods achieve computational efficiency (O(n) complexity) by focusing exclusively on influence estimation, sacrificing the ability to assess attribution reliability. Conversely, contamination detection methods (e.g., BERT embeddings with cosine similarity) can identify train-test leakage but operate independently from attribution pipelines, requiring manual reconciliation and lacking integration with influence scores.

This research addresses three critical questions:

1. **Can contamination-robustness be achieved without sacrificing scalability?** Specifically, can we jointly compute influence scores and contamination confidence in a single O(n) pass, maintaining production-ready efficiency while adding validity assessment?

2. **How does data contamination distort training data attribution?** What is the quantitative relationship between train-test semantic similarity and attribution reliability, and can we formalize this relationship to provide uncertainty-aware explanations?

3. **What practical benefits emerge from contamination-aware attribution?** Can validity-assessed attributions improve GDPR compliance, benchmark integrity auditing, and data curation workflows compared to baseline methods?

### 1.3 Research Objectives

This research proposes **Contamination-Aware Training Data Attribution (CATA)**, a unified framework that integrates gradient-based influence estimation with semantic similarity-based contamination detection. Our primary objectives are:

**O1. Develop a scalable dual-score computation algorithm** that jointly produces:
- Influence scores $I(z_{\text{train}}, z_{\text{test}})$ quantifying training example impact on test predictions (via TRAK projections)
- Contamination confidence scores $C(z_{\text{train}}, z_{\text{test}})$ quantifying train-test semantic overlap (via pre-computed embeddings)
- Attribution validity scores $V(z_{\text{train}}, z_{\text{test}}) = 1 - C$ indicating explanation trustworthiness

**O2. Establish theoretical foundations** for contamination-attribution validity by formalizing the relationship between data quality and explanation reliability, bridging data provenance principles (W7+1 framework) with ML explainability.

**O3. Empirically validate contamination-robustness** through controlled experiments on synthetic contaminated benchmarks, demonstrating that CATA achieves:
- High contamination detection accuracy (≥0.8 precision/recall)
- Preserved attribution quality on clean data (≥0.95 rank correlation with TRAK)
- Improved attribution accuracy on contaminated data (≥10% relative improvement over TRAK)
- Maintained O(n) scalability (≤2× computational overhead)

**O4. Deliver production-ready tooling** via open-source implementation extending the dattri library, enabling practitioners to generate validity-assessed attributions for internet-scale datasets.

### 1.4 Significance

This research makes four significant contributions to the machine learning community:

**Scientific Impact:** CATA addresses a fundamental gap in training data attribution by introducing validity quantification, enabling researchers to distinguish genuine model learning from contamination artifacts. This advances our understanding of how dataset composition influences model behavior—a core challenge identified in the workshop's call for research on data attribution and selection.

**Regulatory Compliance:** By providing GDPR-compliant explanations that exclude contaminated training examples, CATA enables trustworthy AI deployment in regulated domains (healthcare, finance, legal systems) where explanation validity is legally mandated.

**Benchmark Integrity:** CATA provides a systematic tool for detecting train-test leakage in ML benchmarks, addressing the reproducibility crisis where inflated performance metrics stem from data contamination rather than algorithmic innovation. This supports the workshop's focus on data leakage/contamination monitoring at internet scale.

**Methodological Innovation:** The dual-score joint computation paradigm demonstrates that validity assessment and scalability are not mutually exclusive—by leveraging pre-computed embeddings and decoupled computation, we achieve contamination-awareness without sacrificing O(n) efficiency. This establishes a template for integrating data quality assessment into other scalable ML methods.

---

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Influence Functions and Attribution

We build upon the influence function framework (Koh & Liang, 2017) for training data attribution. Given a trained model with parameters $\theta^*$ minimizing empirical risk $\mathcal{L}(\theta) = \frac{1}{n}\sum_{i=1}^n \ell(z_i; \theta)$, the influence of removing training example $z_{\text{train}}$ on test loss $\ell(z_{\text{test}}; \theta^*)$ is approximated by:

$$I(z_{\text{train}}, z_{\text{test}}) = -\nabla_\theta \ell(z_{\text{test}}; \theta^*)^\top H^{-1} \nabla_\theta \ell(z_{\text{train}}; \theta^*)$$

where $H = \frac{1}{n}\sum_{i=1}^n \nabla_\theta^2 \ell(z_i; \theta^*)$ is the Hessian. TRAK (Park et al., 2023) achieves O(n) scalability by replacing Hessian inversion with random projection:

$$I_{\text{TRAK}}(z_{\text{train}}, z_{\text{test}}) = \Phi(\nabla_\theta \ell(z_{\text{test}}; \theta^*))^\top \Phi(\nabla_\theta \ell(z_{\text{train}}; \theta^*))$$

where $\Phi: \mathbb{R}^d \rightarrow \mathbb{R}^k$ is a random projection matrix with $k \ll d$.

#### 2.1.2 Contamination Confidence via Semantic Similarity

We define contamination confidence as the semantic similarity between training and test examples in a pre-trained embedding space:

$$C(z_{\text{train}}, z_{\text{test}}) = \text{sim}(\mathbf{e}_{\text{train}}, \mathbf{e}_{\text{test}}) = \frac{\mathbf{e}_{\text{train}} \cdot \mathbf{e}_{\text{test}}}{\|\mathbf{e}_{\text{train}}\| \|\mathbf{e}_{\text{test}}\|}$$

where $\mathbf{e}_{\text{train}} = f_{\text{embed}}(z_{\text{train}})$ and $\mathbf{e}_{\text{test}} = f_{\text{embed}}(z_{\text{test}})$ are embeddings from a pre-trained encoder:
- **Text**: sentence-transformers/all-MiniLM-L6-v2 (384-dim BERT embeddings)
- **Vision**: OpenAI CLIP ViT-B/32 (512-dim image embeddings)

High contamination confidence ($C \approx 1$) indicates potential train-test leakage, as semantically similar examples should ideally reside in separate data partitions.

#### 2.1.3 Attribution Validity

We formalize the relationship between contamination and attribution reliability through **attribution validity**:

$$V(z_{\text{train}}, z_{\text{test}}) = \begin{cases} 
1 - C(z_{\text{train}}, z_{\text{test}}) & \text{if } C(z_{\text{train}}, z_{\text{test}}) > \tau \\
1 & \text{otherwise}
\end{cases}$$

where $\tau$ is an adaptive contamination threshold (99th percentile of the similarity distribution). This formulation captures the intuition that high contamination confidence inversely correlates with explanation trustworthiness—attributions to contaminated examples reflect memorization rather than generalization.

### 2.2 CATA Algorithm

#### 2.2.1 Offline Pre-Computation Phase

**Input:** Training dataset $D_{\text{train}} = \{z_1, \ldots, z_n\}$, test dataset $D_{\text{test}}$, trained model $\theta^*$

**Step 1: Gradient Computation** (O(n) complexity)
```
For each z_train in D_train:
    g_train[i] = ∇_θ ℓ(z_train; θ*)
For each z_test in D_test:
    g_test[j] = ∇_θ ℓ(z_test; θ*)
```

**Step 2: TRAK Projection** (O(n) complexity)
```
Initialize random projection Φ: R^d → R^k (k=1024)
For each gradient g:
    proj[i] = Φ(g[i])
```

**Step 3: Embedding Computation** (O(n) complexity)
```
Load pre-trained encoder f_embed (BERT/CLIP)
For each z_train in D_train:
    e_train[i] = f_embed(z_train)
For each z_test in D_test:
    e_test[j] = f_embed(z_test)
```

**Step 4: Threshold Calibration** (O(n²) sampling, amortized O(n))
```
Sample 10,000 random train-test pairs
Compute similarity distribution
τ = 99th percentile of similarities
```

**Total Offline Cost:** O(n) for gradients + O(n) for projections + O(n) for embeddings = **O(n)**

#### 2.2.2 Online Attribution Query Phase

**Input:** Test example $z_{\text{test}}$, top-K parameter

**Step 1: Dual-Score Computation** (O(n) per query)
```
For each z_train in D_train:
    I[i] = proj_test · proj_train[i]  // Influence score
    C[i] = cosine_sim(e_test, e_train[i])  // Contamination confidence
    V[i] = 1 - C[i] if C[i] > τ else 1  // Attribution validity
```

**Step 2: Contamination-Aware Ranking**
```
Sort training examples by |I[i]| (descending)
Filter examples where C[i] > τ (contaminated)
Return top-K clean examples with validity scores
```

**Step 3: Explanation Confidence**
```
explanation_confidence = mean(V[top_K_indices])
```

**Output:** 
- Top-K influential training examples (contamination-filtered)
- Influence scores $I_1, \ldots, I_K$
- Validity scores $V_1, \ldots, V_K$
- Overall explanation confidence

**Query Complexity:** O(n) for dual-score computation + O(n log n) for sorting = **O(n log n)** (same as TRAK)

### 2.3 Experimental Design

#### 2.3.1 Datasets and Contamination Injection

**Clean Benchmarks:**
- **Vision:** CIFAR-10 (50k train, 10k test), ImageNet-1K subset (100k train, 10k test)
- **Text:** MNLI (393k train, 10k dev), SQuAD 2.0 (130k train, 12k dev)

**Synthetic Contamination Protocol:**

For each contamination rate $r \in \{1\%, 5\%, 10\%, 20\%\}$ and contamination type:

1. **Exact Duplicates:** Randomly sample $r \times |D_{\text{test}}|$ test examples and insert exact copies into $D_{\text{train}}$

2. **Semantic Paraphrases:**
   - **Text:** Apply back-translation (English → German → English) using MarianMT
   - **Vision:** Apply strong augmentations (random crop + color jitter + Gaussian blur)

3. **Partial Overlaps:**
   - **Text:** Replace 50% of tokens with synonyms from WordNet
   - **Vision:** Insert 50% of test image as random crop into training set

**Contamination Ground Truth:** Maintain mapping $M: D_{\text{train}} \rightarrow D_{\text{test}} \cup \{\text{clean}\}$ for evaluation

#### 2.3.2 Model Training

**Vision Models:**
- Architecture: ResNet-50 (ImageNet pre-trained, fine-tuned on CIFAR-10)
- Optimizer: SGD with momentum (lr=0.01, momentum=0.9, weight decay=5e-4)
- Training: 100 epochs, batch size 128

**Text Models:**
- Architecture: BERT-base-uncased (fine-tuned on MNLI/SQuAD)
- Optimizer: AdamW (lr=2e-5, weight decay=0.01)
- Training: 3 epochs, batch size 32

#### 2.3.3 Evaluation Metrics

**Contamination Detection Performance:**

$$\text{Precision} = \frac{|\{z: C(z, z_{\text{test}}) > \tau\} \cap M^{-1}(z_{\text{test}})|}{|\{z: C(z, z_{\text{test}}) > \tau\}|}$$

$$\text{Recall} = \frac{|\{z: C(z, z_{\text{test}}) > \tau\} \cap M^{-1}(z_{\text{test}})|}{|M^{-1}(z_{\text{test}})|}$$

$$\text{F1} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**Attribution Accuracy:**

1. **Rank Correlation with Leave-One-Out (LOO):**
   - Compute LOO retraining influence (gold standard) for 1,000 sampled examples
   - Measure Spearman's $\rho$ between CATA influence scores and LOO scores

2. **Linear Datamodeling Score (LDS)** (Hammoudeh & Lowd, 2022):
   - Train linear model: $\hat{y}_{\text{test}} = \sum_{i=1}^n \alpha_i I(z_i, z_{\text{test}}) y_i$
   - Measure prediction accuracy on held-out test set

3. **Mislabeled Data Detection:**
   - Inject 10% label noise into training set
   - Measure F1 for detecting mislabeled examples using negative influence scores

**Scalability Metrics:**
- Wall-clock time (seconds) for offline pre-computation and online queries
- Peak memory usage (GB)
- Comparison: CATA vs. TRAK baseline

#### 2.3.4 Ablation Studies

**A1. Threshold Sensitivity:**
- Vary $\tau$ from 90th to 99.9th percentile
- Measure contamination detection F1 and attribution accuracy
- Identify optimal threshold balancing false positives/negatives

**A2. Embedding Model Comparison:**
- **Text:** Compare BERT-base, Sentence-BERT (all-MiniLM-L6-v2), RoBERTa-base
- **Vision:** Compare CLIP ViT-B/32, ResNet-50 features, DINOv2
- Measure contamination detection accuracy for each embedding

**A3. Contamination Type Analysis:**
- Separate evaluation on exact duplicates, paraphrases, partial overlaps
- Characterize detection scope and failure modes

**A4. Filtering Strategy:**
- Compare hard filtering (remove C > τ) vs. soft filtering (weight by validity)
- Measure impact on attribution accuracy and explanation diversity

#### 2.3.5 Statistical Testing

**Hypothesis Testing Framework:**

- **Null Hypothesis (H0):** CATA attribution accuracy = TRAK attribution accuracy on contaminated data
- **Alternative Hypothesis (H1):** CATA attribution accuracy > TRAK attribution accuracy

**Test Procedure:**
1. For each contamination rate $r \in \{1\%, 5\%, 10\%, 20\%\}$:
   - Measure LDS for CATA and TRAK on 5 independent contaminated datasets
   - Compute paired differences: $\Delta_i = \text{LDS}_{\text{CATA}}^{(i)} - \text{LDS}_{\text{TRAK}}^{(i)}$
2. Perform one-tailed paired t-test with $\alpha = 0.05$
3. Compute effect size (Cohen's d): $d = \frac{\bar{\Delta}}{s_\Delta}$
4. **Reject H0 if:** $p < 0.05$ AND $d > 0.3$ (medium practical significance)

**Confidence Intervals:**
- Bootstrap 95% CI for contamination detection metrics (1,000 resamples)
- Report mean ± CI for all performance metrics

### 2.4 Implementation Details

**Software Stack:**
- Framework: PyTorch 2.0, Hugging Face Transformers 4.30
- Attribution: dattri library (extended with CATA module)
- Embeddings: sentence-transformers, OpenAI CLIP
- Compute: 4× NVIDIA A100 GPUs (40GB), 256GB RAM

**Code Availability:**
- Open-source repository: github.com/[anonymous]/contamination-aware-attribution
- Integration with dattri: Pull request to github.com/trais-lab/dattri
- Reproducibility: Docker container with frozen dependencies, random seeds

**Computational Budget:**
- Offline pre-computation: ~8 GPU-hours per dataset (CIFAR-10/MNLI)
- Online queries: ~0.1 seconds per test example (amortized over batch processing)
- Total experimental cost: ~200 GPU-hours (all datasets, contamination rates, ablations)

---

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Outcome 1: Validated Contamination Detection**

We expect CATA to achieve **≥0.8 precision and ≥0.8 recall** for detecting exact duplicates and semantic paraphrases across all contamination rates (1%-20%). This will demonstrate that pre-trained embeddings (BERT/CLIP) combined with cosine similarity provide reliable contamination detection without task-specific fine-tuning. We anticipate lower recall (~0.6-0.7) for partial overlaps, as these represent more subtle contamination that may fall below the 99th percentile threshold.

**Outcome 2: Preserved Attribution Quality on Clean Data**

On clean benchmarks (no contamination), we expect CATA influence scores to achieve **≥0.95 Spearman rank correlation** with baseline TRAK scores. This will validate that adding contamination confidence scoring does not degrade attribution accuracy when contamination is absent, confirming the decoupled dual-score computation preserves TRAK's attribution fidelity.

**Outcome 3: Improved Robustness on Contaminated Data**

On contaminated benchmarks, we expect CATA (with contamination filtering) to achieve **10-30% relative improvement** in linear datamodeling score compared to TRAK, with larger improvements at higher contamination rates (20% vs. 1%). Statistical testing will confirm significance (p < 0.05, Cohen's d > 0.3), demonstrating that contamination-aware filtering produces more reliable attributions by excluding memorization artifacts.

**Outcome 4: Maintained Scalability**

We expect CATA's total computation time to be **≤2× TRAK baseline**, with the overhead primarily from embedding computation (one-time O(n) cost). For CIFAR-10 (50k training examples), we anticipate:
- TRAK baseline: ~30 minutes offline + 0.05 seconds per query
- CATA: ~50 minutes offline + 0.08 seconds per query

This will validate the O(n) scalability claim and demonstrate production-readiness.

### 3.2 Scientific Impact

**Advancing Model Behavior Attribution Theory:**

CATA establishes a theoretical framework connecting data quality assessment with explainability by formalizing attribution validity $V = 1 - C$. This bridges two previously disconnected research areas:
- **Data provenance** (W7+1 framework's "How certain?" dimension)
- **Training data attribution** (influence functions, gradient-based methods)

This cross-domain synthesis provides a principled foundation for uncertainty-aware explanations, addressing a fundamental gap in current attribution methods that provide point estimates without confidence quantification.

**Characterizing Contamination's Impact on Attribution:**

Through controlled experiments with synthetic contamination, CATA will provide the first systematic characterization of how train-test leakage distorts influence scores. We expect to discover:
- **Contamination amplification:** Contaminated examples receive disproportionately high influence scores (top-10 attributions dominated by leaks)
- **Threshold sensitivity:** Optimal contamination threshold varies by domain (text vs. vision) and contamination type
- **Failure modes:** Adversarial paraphrasing (e.g., synonym substitution) may evade semantic similarity detection

These findings will inform future research on contamination-robust attribution and benchmark design.

### 3.3 Practical Impact

**GDPR Compliance and Trustworthy AI:**

CATA enables regulatory compliance by providing **validity-assessed explanations** that exclude contaminated training examples. For GDPR Article 22 ("right to explanation"), practitioners can now report:
- Top-K influential training examples (contamination-filtered)
- Explanation confidence score (mean attribution validity)
- Flagged contaminated examples for manual review

This addresses a critical gap in current explainability tools, which provide attributions without reliability assessment, potentially violating regulatory requirements for trustworthy explanations.

**Benchmark Integrity Auditing:**

CATA provides a systematic tool for detecting train-test leakage in ML benchmarks. We will apply CATA to popular datasets (CIFAR-10, ImageNet, MNLI, SQuAD) and publicly report:
- Estimated contamination rates (percentage of test examples with high-similarity training matches)
- Identified contaminated example pairs for community review
- Recommendations for benchmark curation (e.g., deduplication protocols)

This supports the ML community's efforts to address the reproducibility crisis, where inflated performance metrics stem from data contamination rather than algorithmic innovation.

**Data Curation and Quality Improvement:**

CATA's contamination confidence scores enable **automated data cleaning pipelines**:
1. Flag training examples with high contamination confidence (C > τ) for manual review
2. Remove exact duplicates and near-duplicates from training sets
3. Monitor contamination rates in continually updated datasets (e.g., web scraping pipelines)

For internet-scale datasets (Common Crawl, LAION-5B), this provides a scalable quality control mechanism, improving dataset integrity without manual inspection of billions of examples.

### 3.4 Broader Impact

**Open-Source Tooling:**

By extending the dattri library with CATA, we will provide production-ready tooling for the ML community. Expected adoption pathways:
- **Researchers:** Use CATA for dataset analysis, contamination auditing, and attribution studies
- **Practitioners:** Integrate CATA into ML pipelines for GDPR-compliant explanations
- **Benchmark curators:** Apply CATA for train-test leakage detection before dataset release

**Methodological Template:**

CATA demonstrates that **validity assessment and scalability are not mutually exclusive**. The dual-score joint computation paradigm (decoupled influence + contamination scoring) can be extended to other scalable ML methods:
- **Uncertainty quantification:** Add calibration confidence to predictions
- **Fairness auditing:** Detect demographic leakage in training data
- **Privacy analysis:** Identify membership inference vulnerabilities

This establishes a template for integrating data quality assessment into efficient ML algorithms.

**Limitations and Future Work:**

We acknowledge several limitations that motivate future research:

1. **Adversarial Contamination:** CATA detects semantic-level contamination but may fail against adversarial obfuscation (e.g., steganographic encoding). Future work: adversarial robustness for contamination detection.

2. **Cross-Lingual Leakage:** Current embeddings (English BERT) cannot detect translation-based contamination. Future work: multilingual embeddings (mBERT, XLM-R).

3. **Feature-Level Leakage:** Examples with identical features but different labels (e.g., label noise) are not detected by semantic similarity. Future work: feature space contamination detection.

4. **Dynamic Datasets:** Pre-computed embeddings assume static datasets. Future work: incremental embedding updates for continual learning.

Despite these limitations, CATA represents a significant step toward trustworthy, validity-assessed training data attribution at scale, addressing critical needs for regulatory compliance, benchmark integrity, and data quality in modern ML systems.

---

**Word Count:** 4,987 words (extended for comprehensive coverage)