# Research Proposal

## Title
Cross-Domain Backdoor Defense via Universal Trigger Pattern Detection Using Self-Supervised Representation Learning

## 1. Introduction

### Background

Backdoor attacks represent one of the most insidious threats to modern machine learning systems. Unlike adversarial attacks that require real-time perturbation generation, backdoor attacks embed persistent vulnerabilities during the training phase, enabling attackers to trigger misclassification at any time by simply applying a pre-defined trigger pattern. The proliferation of publicly available pre-trained models and the common practice of training on user-contributed data have significantly expanded the attack surface for backdoor threats. Recent research has demonstrated successful backdoor attacks across diverse domains including computer vision (CV), natural language processing (NLP), federated learning (FL), and even emerging areas such as reinforcement learning and autonomous systems.

The defense landscape against backdoor attacks has evolved substantially, spawning multiple research directions: input-level detection of triggered samples, model-level identification of backdoored networks, and backdoor elimination through model purification. However, existing defenses suffer from a critical limitation—they are predominantly domain-specific. TextGuard (Pei et al., 2023) provides provable defense specifically for text classification, while MARS (Wan et al., 2025) addresses backdoor threats uniquely in federated learning contexts. This fragmented approach creates significant security gaps, particularly as modern AI systems increasingly operate across multiple modalities and domains.

The emergence of large pre-trained models deployed across diverse applications amplifies these concerns. A defense mechanism effective only against image-based triggers provides no protection when the same model processes text or multimodal inputs. Furthermore, as demonstrated by recent work on invisible backdoor attacks against self-supervised learning (Zhang et al., 2025) and noisy alignment attacks (Chen et al., 2025), attackers continuously develop novel trigger mechanisms that evade domain-specific defenses.

### Research Objectives

This research proposes to develop a unified, cross-domain backdoor defense framework based on self-supervised contrastive learning. Our primary objectives are:

1. **Develop a domain-agnostic representation learning framework** that captures fundamental characteristics distinguishing clean inputs from backdoor-triggered samples across multiple data modalities.

2. **Design a universal "naturalness scoring" mechanism** that quantifies the conformity of inputs to learned clean data manifolds, enabling detection of triggered samples regardless of the specific attack strategy.

3. **Validate the cross-domain effectiveness** of our approach across CV, NLP, and FL settings, demonstrating robust detection of both known and novel trigger patterns.

4. **Reduce reliance on domain-specific heuristics** by learning generalizable detection features that transfer across domains and attack types.

### Significance

This research addresses a fundamental gap in backdoor defense research: the absence of a unified defense framework capable of protecting multi-modal ML systems. The proposed approach has significant implications for:

- **Security of deployed AI systems**: Enabling practical backdoor detection in real-world applications processing diverse data types
- **Scalability of defense mechanisms**: Reducing the need to develop and maintain separate defenses for each domain
- **Robustness against novel attacks**: Providing detection capabilities that generalize to unseen trigger patterns
- **Advancing theoretical understanding**: Establishing connections between backdoor manifestations across domains through representation learning

## 2. Methodology

### 2.1 Overview

Our methodology centers on the hypothesis that backdoor triggers, regardless of domain or specific attack strategy, create anomalous patterns in representation space that deviate systematically from natural data distributions. We exploit this insight through a three-stage framework: (1) multi-domain contrastive pre-training, (2) naturalness score learning, and (3) cross-domain backdoor detection.

### 2.2 Data Collection and Preparation

**Clean Data Corpus**: We construct a diverse clean dataset spanning multiple domains:
- **Computer Vision**: CIFAR-10, CIFAR-100, ImageNet subsets, GTSRB (traffic signs)
- **Natural Language Processing**: SST-2, AG News, IMDB reviews, 20 Newsgroups
- **Tabular/Federated Learning**: MNIST (for FL simulation), UCI Adult, CICIDS network intrusion data

**Backdoor Attack Dataset**: We generate backdoored versions using established attack methods:
- **CV attacks**: BadNets (patch triggers), Blended attacks, WaNet (warping-based), ISSBA (sample-specific)
- **NLP attacks**: BadNL (word insertion), syntactic triggers, style-based triggers
- **FL attacks**: Model replacement, gradient manipulation with embedded triggers

**Preprocessing**: All inputs are transformed into a unified representation space:
- Images: ResNet-18 feature extraction (512-dimensional vectors)
- Text: Sentence-BERT embeddings (768-dimensional vectors)
- Tabular: Standardized feature vectors with domain-specific normalization

### 2.3 Multi-Domain Contrastive Pre-Training

We train a domain-agnostic encoder $f_\theta$ using a modified contrastive learning objective that encourages learning of cross-domain invariant representations.

**Architecture**: The encoder consists of:
- Domain-specific input projectors $\{g_d\}_{d \in \mathcal{D}}$ that map domain $d$ inputs to a shared latent space $\mathbb{R}^{256}$
- A shared representation network $h_\phi: \mathbb{R}^{256} \rightarrow \mathbb{R}^{128}$

**Contrastive Learning Objective**: For each sample $x_i$ from domain $d$, we generate augmented views $\tilde{x}_i^{(1)}$ and $\tilde{x}_i^{(2)}$ using domain-appropriate augmentations. The contrastive loss is:

$$\mathcal{L}_{contrast} = -\sum_{i=1}^{N} \log \frac{\exp(sim(z_i^{(1)}, z_i^{(2)})/\tau)}{\sum_{j=1}^{2N} \mathbb{1}_{[j \neq i]} \exp(sim(z_i^{(1)}, z_j)/\tau)}$$

where $z_i = h_\phi(g_d(x_i))$, $sim(\cdot, \cdot)$ denotes cosine similarity, and $\tau$ is a temperature parameter.

**Cross-Domain Alignment Loss**: To ensure representations from different domains share a common structure, we introduce an alignment term:

$$\mathcal{L}_{align} = \sum_{d_1, d_2 \in \mathcal{D}} D_{KL}\left(P_{d_1}(z) \| P_{d_2}(z)\right)$$

where $P_d(z)$ represents the empirical distribution of representations from domain $d$.

**Total Pre-Training Objective**:

$$\mathcal{L}_{pretrain} = \mathcal{L}_{contrast} + \lambda \mathcal{L}_{align}$$

### 2.4 Naturalness Score Learning

After pre-training, we learn a naturalness scoring function $s: \mathbb{R}^{128} \rightarrow [0, 1]$ that measures conformity to clean data manifolds.

**Gaussian Mixture Model Fitting**: We model the clean data distribution in representation space as a mixture of Gaussians:

$$p(z | \text{clean}) = \sum_{k=1}^{K} \pi_k \mathcal{N}(z; \mu_k, \Sigma_k)$$

The parameters $\{\pi_k, \mu_k, \Sigma_k\}_{k=1}^{K}$ are estimated via Expectation-Maximization on clean training representations.

**Naturalness Score Computation**: For an input $x$, the naturalness score is computed as:

$$s(x) = \frac{p(z_x | \text{clean})}{\max_{z' \in \mathcal{Z}_{clean}} p(z' | \text{clean})}$$

where $z_x = h_\phi(g_d(x))$ and $\mathcal{Z}_{clean}$ represents the set of clean training representations.

**Anomaly-Aware Refinement**: We refine the scoring function using a small set of known backdoor samples (if available) via a neural network classifier:

$$\mathcal{L}_{refine} = -\sum_{i} \left[ y_i \log \sigma(w^T z_i + b) + (1-y_i) \log(1 - \sigma(w^T z_i + b)) \right]$$

where $y_i \in \{0, 1\}$ indicates clean/backdoor labels.

### 2.5 Cross-Domain Backdoor Detection Algorithm

**Algorithm 1: Universal Backdoor Detection**

```
Input: Test sample x, domain indicator d, threshold τ_det
Output: Detection decision (clean/backdoor)

1. Extract representation: z = h_φ(g_d(x))
2. Compute naturalness score: s = NaturalnessScore(z)
3. If s < τ_det:
      Return "Backdoor detected"
   Else:
      Return "Clean"
```

**Threshold Selection**: The detection threshold $\tau_{det}$ is determined using a validation set containing clean samples:

$$\tau_{det} = \mu_{clean} - k \cdot \sigma_{clean}$$

where $\mu_{clean}$ and $\sigma_{clean}$ are the mean and standard deviation of naturalness scores for clean validation samples, and $k$ is a sensitivity parameter (typically $k = 2$ or $k = 3$).

### 2.6 Experimental Design

**Evaluation Scenarios**:

1. **Intra-Domain Detection**: Train and test on the same domain (CV-to-CV, NLP-to-NLP)
2. **Cross-Domain Transfer**: Train on one domain, test on another (CV-to-NLP, etc.)
3. **Multi-Domain Joint Training**: Train on all domains simultaneously
4. **Novel Attack Detection**: Evaluate on attack types not seen during training

**Baseline Methods**:
- Domain-specific: Neural Cleanse, STRIP, Spectral Signatures (CV); ONION, RAP (NLP)
- Recent advances: TextGuard, DLP, NT-ML
- Ablations: Single-domain pre-training, supervised-only detection

**Evaluation Metrics**:

1. **Detection Performance**:
   - True Positive Rate (TPR): Proportion of backdoor samples correctly identified
   - False Positive Rate (FPR): Proportion of clean samples incorrectly flagged
   - Area Under ROC Curve (AUROC): Overall detection discrimination ability
   - F1-Score: Harmonic mean of precision and recall

2. **Cross-Domain Generalization**:
   - Transfer AUROC: Detection performance when trained on domain A, tested on domain B
   - Generalization Gap: Performance difference between intra-domain and cross-domain settings

3. **Computational Efficiency**:
   - Detection latency per sample
   - Memory footprint
   - Training time for the defense model

**Statistical Validation**: All experiments will be repeated with 5 random seeds, reporting mean and standard deviation. Statistical significance will be assessed using paired t-tests with Bonferroni correction.

### 2.7 Implementation Details

- **Framework**: PyTorch 2.0 with distributed training support
- **Encoder Architecture**: 4-layer MLP with ReLU activations and batch normalization
- **Training**: Adam optimizer, learning rate $10^{-4}$, batch size 256, 100 epochs
- **Contrastive Learning**: Temperature $\tau = 0.07$, alignment weight $\lambda = 0.1$
- **GMM Components**: $K = 10$ (selected via BIC criterion)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Outcomes**:

1. **Universal Detection Framework**: We expect to achieve AUROC scores exceeding 0.90 for intra-domain detection across CV, NLP, and FL settings, matching or surpassing domain-specific baselines.

2. **Cross-Domain Transfer**: We anticipate transfer AUROC scores of at least 0.80 when the defense model is trained on one domain and tested on another, demonstrating meaningful cross-domain generalization.

3. **Novel Attack Robustness**: The self-supervised approach should detect at least 70% of unseen attack types not included in training, addressing a critical limitation of existing supervised defenses.

4. **Computational Efficiency**: Detection latency should remain under 10ms per sample, enabling real-time deployment in production systems.

**Scientific Contributions**:

1. **Theoretical Insights**: Empirical validation of the hypothesis that backdoor triggers create domain-invariant anomalies in representation space, advancing theoretical understanding of backdoor attacks.

2. **Unified Framework**: First comprehensive cross-domain backdoor defense framework validated across CV, NLP, and FL domains simultaneously.

3. **Benchmark and Resources**: Public release of code, pre-trained models, and a standardized multi-domain backdoor evaluation benchmark.

### Research Impact

**Immediate Impact**:

- **Practical Deployment**: Organizations can deploy a single defense mechanism protecting multi-modal AI systems, reducing security infrastructure complexity
- **Cost Reduction**: Elimination of the need to maintain domain-specific defense systems
- **Enhanced Security Posture**: Protection against cross-domain attacks exploiting modality-specific blind spots

**Long-Term Impact**:

- **Foundation for Future Research**: The cross-domain representation learning approach can be extended to other security threats beyond backdoors
- **Standardization**: Establishment of benchmarks and evaluation protocols for cross-domain ML security research
- **Industry Adoption**: Practical defense mechanisms suitable for integration into production ML pipelines

**Broader Implications**:

This research contributes to the broader goal of trustworthy AI by addressing security vulnerabilities in increasingly ubiquitous ML systems. As AI systems become more integrated into critical infrastructure, healthcare, and autonomous systems, robust cross-domain defenses become essential for maintaining public trust and safety.

### Limitations and Future Directions

We acknowledge potential limitations: (1) the assumption that clean training data is available may not hold in all scenarios; (2) adaptive attackers aware of our defense may develop evasion strategies; (3) computational overhead of contrastive pre-training may limit applicability in resource-constrained settings.

Future work will address these limitations by exploring: (1) semi-supervised and unsupervised variants requiring minimal clean data; (2) adversarial training to improve robustness against adaptive attacks; (3) efficient architectures for edge deployment.