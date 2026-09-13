# Research Proposal: Gradient-Based Causal Feature Scoring for Domain Generalization via Cross-Domain Variance Analysis

## 1. Introduction

### 1.1 Background

Domain generalization (DG) represents one of the most fundamental challenges in modern machine learning: developing models that can reliably perform on data distributions that differ from those encountered during training. Despite significant research efforts over the past decade, a sobering finding from comprehensive benchmarking studies such as DomainBed (Gulrajani & Lopez-Paz, 2020) reveals that sophisticated DG algorithms often fail to consistently outperform simple Empirical Risk Minimization (ERM) baselines. This observation suggests that standard learning approaches may lack the necessary inductive biases or additional information required to distinguish between features that generalize across domains and those that represent spurious, domain-specific correlations.

The theoretical foundations for understanding this challenge have been explored through multiple lenses. Invariant Risk Minimization (IRM) proposed by Arjovsky et al. (2019) introduced the concept of learning representations that elicit invariant predictors across environments. However, subsequent work by Rosenfeld et al. (2020) demonstrated that IRM can fail dramatically when test domains differ significantly from training domains. More recent approaches like Fishr (Rame et al., 2022) have explored gradient-based invariance penalties, while the unified causal view presented by Wang and Veitch (2022) has established theoretical connections between causal invariance and stable mechanisms across environments.

A critical gap remains in the literature: while gradient-based methods have shown promise for capturing relationship heterogeneity across domains, they typically lack interpretability and fail to provide actionable insights about which specific features contribute to or hinder generalization. This interpretability deficit not only limits practical deployment but also prevents researchers from diagnosing when and why invariance assumptions are violated.

### 1.2 Research Objectives

This research proposes Gradient-based Causal Feature Scoring (GCFS), a novel method that addresses the interpretability gap while leveraging gradient information to distinguish causal from spurious features. Our primary objectives are:

1. **Develop a principled scoring mechanism** that quantifies the causal stability of individual features based on their gradient variance across training domains.

2. **Demonstrate improved out-of-distribution performance** by weighting features according to their causal scores during inference, targeting accuracy improvements of at least 3% over ERM baselines on standard DomainBed benchmarks.

3. **Validate the interpretability claims** by establishing correlations between computed CausalScores and ground-truth causal features on synthetic datasets with known causal structure.

4. **Provide diagnostic capabilities** that allow practitioners to understand when invariance assumptions are likely to hold or fail for specific features.

### 1.3 Significance

This research addresses the workshop's central question—"what do we need for successful domain generalization?"—by proposing that interpretable, per-feature causal scoring provides the additional information necessary for robust out-of-distribution performance. Unlike implicit penalty-based methods, GCFS offers transparency into the feature selection process, enabling both improved performance and actionable insights for model debugging and domain adaptation strategies.

The significance extends beyond benchmark improvements: by providing interpretable causal scores, GCFS enables practitioners to identify which features are reliable across domains, diagnose potential failure modes before deployment, and make informed decisions about when domain generalization methods are appropriate for their specific applications.

## 2. Methodology

### 2.1 Problem Formulation

Consider a multi-domain classification setting with $K$ training domains $\mathcal{D} = \{D_1, D_2, ..., D_K\}$, where each domain $D_k$ contains samples $(x_i^k, y_i^k)$ drawn from domain-specific distribution $P_k(X, Y)$. The goal is to learn a classifier $f: \mathcal{X} \rightarrow \mathcal{Y}$ that generalizes to an unseen test domain $D_{test}$ with distribution $P_{test}(X, Y)$.

We decompose the classifier as $f = g \circ h$, where $h: \mathcal{X} \rightarrow \mathbb{R}^d$ is a feature extractor producing $d$-dimensional representations, and $g: \mathbb{R}^d \rightarrow \mathcal{Y}$ is a classifier head.

### 2.2 Gradient-Based Causal Feature Scoring (GCFS)

#### 2.2.1 Core Intuition

The fundamental insight underlying GCFS is that causal features—those representing stable, domain-invariant relationships between inputs and labels—should exhibit consistent gradient behavior across domains. Specifically, if feature $j$ captures a causal relationship, the gradient of the loss with respect to this feature should have similar magnitude and direction regardless of which domain the data originates from. Conversely, spurious features that exploit domain-specific correlations will show high gradient variance across domains.

#### 2.2.2 Per-Feature Gradient Computation

For each training domain $D_k$ and feature dimension $j \in \{1, ..., d\}$, we compute the average gradient of the loss with respect to feature $j$:

$$\bar{g}_j^k = \frac{1}{|D_k|} \sum_{(x_i, y_i) \in D_k} \frac{\partial \mathcal{L}(f(x_i), y_i)}{\partial h_j(x_i)}$$

where $h_j(x_i)$ denotes the $j$-th dimension of the feature representation for input $x_i$, and $\mathcal{L}$ is the cross-entropy loss.

#### 2.2.3 Cross-Domain Variance Computation

For each feature $j$, we compute the variance of gradients across all $K$ training domains:

$$\text{Var}_j = \frac{1}{K} \sum_{k=1}^{K} \left( \bar{g}_j^k - \bar{g}_j \right)^2$$

where $\bar{g}_j = \frac{1}{K} \sum_{k=1}^{K} \bar{g}_j^k$ is the mean gradient across domains.

To account for scale differences across features, we normalize the variance:

$$\text{NormVar}_j = \frac{\text{Var}_j}{\max_j(\text{Var}_j) + \epsilon}$$

where $\epsilon = 10^{-8}$ prevents division by zero.

#### 2.2.4 CausalScore Computation

The CausalScore for feature $j$ is defined as:

$$\text{CausalScore}_j = \frac{1}{1 + \alpha \cdot \text{NormVar}_j}$$

where $\alpha > 0$ is a temperature hyperparameter controlling the sensitivity to variance differences. Higher $\alpha$ values create sharper distinctions between high-variance and low-variance features.

#### 2.2.5 Feature Weighting During Inference

During inference, feature representations are weighted by their CausalScores:

$$\tilde{h}(x) = \text{CausalScore} \odot h(x)$$

where $\odot$ denotes element-wise multiplication and $\text{CausalScore} \in \mathbb{R}^d$ is the vector of all feature CausalScores.

### 2.3 Training Algorithm

The complete GCFS training procedure is presented in Algorithm 1:

**Algorithm 1: GCFS Training and Inference**

```
Input: Training domains D = {D_1, ..., D_K}, feature extractor h, classifier g
Output: Trained model f, CausalScores

// Phase 1: Standard ERM Training
1. Initialize h and g with pretrained weights (ResNet-50)
2. For epoch = 1 to T_warmup:
3.     For each mini-batch B sampled from ∪_k D_k:
4.         Compute loss L = CrossEntropy(g(h(B)), y_B)
5.         Update h, g via gradient descent

// Phase 2: Gradient Collection
6. For each domain D_k:
7.     For each sample (x_i, y_i) in D_k:
8.         Compute gradients ∂L/∂h_j(x_i) for all j
9.     Compute domain-average gradients ḡ_j^k for all j

// Phase 3: CausalScore Computation
10. For each feature j:
11.     Compute Var_j across domains
12.     Compute CausalScore_j = 1/(1 + α·NormVar_j)

// Phase 4: Fine-tuning with Weighted Features
13. For epoch = 1 to T_finetune:
14.     For each mini-batch B:
15.         Compute weighted features: h̃(B) = CausalScore ⊙ h(B)
16.         Compute loss L = CrossEntropy(g(h̃(B)), y_B)
17.         Update g via gradient descent (h frozen)

// Inference
18. For test input x:
19.     Return g(CausalScore ⊙ h(x))
```

### 2.4 Experimental Design

#### 2.4.1 Datasets

We evaluate GCFS on five standard DomainBed benchmarks:

1. **PACS** (4 domains: Photo, Art, Cartoon, Sketch; 9,991 images, 7 classes)
2. **VLCS** (4 domains: VOC2007, LabelMe, Caltech101, SUN09; 10,729 images, 5 classes)
3. **OfficeHome** (4 domains: Art, Clipart, Product, Real; 15,588 images, 65 classes)
4. **TerraIncognita** (4 domains: L100, L38, L43, L46; 24,788 images, 10 classes)
5. **DomainNet** (6 domains: Clipart, Infograph, Painting, Quickdraw, Real, Sketch; 586,575 images, 345 classes)

Additionally, we construct a **Synthetic Causal Dataset** with known ground-truth causal structure for mechanism validation.

#### 2.4.2 Evaluation Protocol

We follow the standard leave-one-domain-out protocol: for each benchmark with $K$ domains, we train on $K-1$ domains and evaluate on the held-out domain, repeating for all $K$ choices of test domain.

**Hyperparameters:**
- Backbone: ResNet-50 pretrained on ImageNet
- Optimizer: Adam with learning rate $5 \times 10^{-5}$
- Batch size: 32 per domain
- Warmup epochs $T_{warmup}$: 30
- Fine-tuning epochs $T_{finetune}$: 10
- Temperature $\alpha$: searched over $\{0.1, 1.0, 10.0\}$
- Random seeds: 5 independent runs per configuration

#### 2.4.3 Baseline Methods

We compare against:
- **ERM**: Standard empirical risk minimization
- **IRM** (Arjovsky et al., 2019): Invariant risk minimization
- **CORAL** (Sun & Saenko, 2016): Correlation alignment
- **DANN** (Ganin et al., 2016): Domain adversarial neural networks
- **Fishr** (Rame et al., 2022): Gradient matching across domains

#### 2.4.4 Evaluation Metrics

**Primary Metric:**
- Out-of-distribution test accuracy (averaged across all domain splits)

**Secondary Metrics:**
- CausalScore-variance correlation: Spearman correlation between CausalScores and inverse gradient variance
- Interpretability validation: Spearman correlation $\rho$ between CausalScores and ground-truth causal features on synthetic data
- Computational overhead: Training time relative to ERM

#### 2.4.5 Statistical Analysis

All experiments are repeated with 5 random seeds. We report:
- Mean accuracy ± standard deviation
- Paired t-test comparing GCFS vs. ERM (one-tailed, $\alpha = 0.05$)
- Cohen's d effect size
- 95% confidence intervals for accuracy differences

### 2.5 Synthetic Dataset for Mechanism Validation

To validate that CausalScores correctly identify causal features, we construct a synthetic dataset with known causal structure:

**Data Generation Process:**
1. Define $d_{causal} = 10$ causal features and $d_{spurious} = 10$ spurious features
2. Generate causal features $X_{causal} \sim \mathcal{N}(0, I)$
3. Generate labels $Y = \text{sign}(w_{causal}^T X_{causal} + \epsilon)$ where $\epsilon \sim \mathcal{N}(0, 0.1)$
4. For each domain $k$, generate spurious features with domain-specific correlation:
   $$X_{spurious}^k = \rho_k \cdot Y + \sqrt{1-\rho_k^2} \cdot \mathcal{N}(0, I)$$
   where $\rho_k$ varies across domains (e.g., $\rho \in \{0.9, 0.5, 0.1, -0.3\}$)

This construction ensures causal features have stable gradient relationships while spurious features exhibit high gradient variance.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** We expect GCFS to achieve average OOD accuracy exceeding 72% across DomainBed benchmarks, representing a statistically significant improvement over the ERM baseline (~69%). Based on our hypothesis confidence level of 0.82, we anticipate:
- PACS: 87% → 90% accuracy
- VLCS: 77% → 80% accuracy
- OfficeHome: 67% → 70% accuracy
- TerraIncognita: 47% → 51% accuracy
- DomainNet: 41% → 44% accuracy

**Mechanism Validation (P2):** Features in the top 20% by CausalScore will exhibit at least 2× lower gradient variance than features in the bottom 20%, confirming the theoretical relationship between gradient stability and causal relevance.

**Interpretability Validation (P3):** On synthetic datasets, CausalScores will correlate with ground-truth causal features with Spearman $\rho > 0.6$, demonstrating that the scoring mechanism correctly identifies causal structure.

### 3.2 Potential Limitations and Mitigation

1. **Domain Label Quality:** GCFS requires meaningful domain labels. If domains do not represent genuine distribution shifts, gradient variance may not capture spurious correlations. *Mitigation:* We include TerraIncognita, which has naturally occurring domain shifts, to test robustness.

2. **Number of Domains:** With fewer than 3 training domains, variance estimates may be unreliable. *Mitigation:* We report performance stratified by number of training domains and recommend minimum domain requirements.

3. **Computational Overhead:** Gradient collection adds computational cost. *Mitigation:* We estimate 5-10% overhead and report exact measurements.

### 3.3 Broader Impact

This research contributes to the workshop's goal of identifying what additional information enables successful domain generalization. By demonstrating that interpretable, per-feature causal scoring provides actionable insights beyond implicit penalty methods, we advance both the theoretical understanding and practical applicability of DG methods.

The interpretability benefits extend to high-stakes applications in healthcare, autonomous systems, and scientific discovery, where understanding *why* a model generalizes (or fails to generalize) is as important as the generalization itself. GCFS provides practitioners with diagnostic tools to assess model reliability before deployment, potentially preventing costly failures in safety-critical applications.

Furthermore, the gradient-variance framework opens new research directions: extending GCFS to other modalities (text, time-series), combining with causal discovery methods, and developing adaptive weighting schemes that adjust CausalScores based on detected distribution shift at test time.