# Research Proposal: HUA-LoRA: Hierarchical Unlearning via Domain-Partitioned Adapters for Scalable GDPR Compliance in Large Language Models

## 1. Introduction

### 1.1 Background

The proliferation of large language models (LLMs) across critical applications—from healthcare diagnostics to financial services—has precipitated unprecedented regulatory scrutiny. The European Union's General Data Protection Regulation (GDPR), particularly Article 17 establishing the "right to be forgotten," mandates that individuals can request the erasure of their personal data from automated systems. This regulatory requirement creates a fundamental tension with modern machine learning practices: LLMs trained on billions of parameters encode information from training data in distributed, entangled representations that resist selective removal.

Current approaches to machine unlearning fall into two categories, neither satisfying regulatory requirements at scale. **Exact unlearning** through full model retraining guarantees complete data removal but incurs prohibitive computational costs—retraining a 7-billion parameter model can require thousands of GPU-hours and millions of dollars. **Approximate unlearning** methods, including gradient ascent, influence function-based approaches, and knowledge distillation, offer computational efficiency but provide weak or unverifiable forgetting guarantees. Recent empirical studies demonstrate that approximate methods often fail membership inference attack (MIA) verification, leaving residual data influence detectable by adversaries and regulators alike.

This gap between regulatory mandates and technical capabilities represents a critical barrier to compliant LLM deployment. Organizations face an impossible choice: either maintain expensive retraining infrastructure for every deletion request or deploy systems that may violate data protection laws. The situation is further complicated by the lack of standardized verification protocols—even when unlearning is attempted, demonstrating compliance to regulators remains challenging.

### 1.2 Research Objectives

This research proposes **HUA-LoRA (Hierarchical Unlearning via Domain-Partitioned Adapters)**, a novel framework that achieves scalable, verifiable machine unlearning for LLMs through architectural compartmentalization and targeted weight decay. Our specific objectives are:

1. **Design a domain-partitioned adapter architecture** that localizes data influence to specific low-rank adapter modules during fine-tuning, enabling targeted unlearning without affecting unrelated knowledge.

2. **Develop a multiplicative weight decay mechanism** inspired by neuroscience principles of synaptic forgetting that progressively erases learned representations in targeted adapters.

3. **Establish rigorous verification protocols** using membership inference attacks and statistical tests to demonstrate forgetting efficacy that satisfies regulatory requirements.

4. **Validate the framework** on billion-parameter LLMs, demonstrating >90% MIA evasion, >95% utility retention, and <1% of retraining computational cost.

### 1.3 Significance

This research directly addresses the workshop's focus on bridging gaps between ML research and regulatory principles. By providing a practical, verifiable unlearning mechanism for production LLMs, HUA-LoRA enables organizations to operationalize GDPR's right to be forgotten without prohibitive costs. The framework contributes to multiple workshop themes: (1) novel algorithmic frameworks for the right to be forgotten, (2) evaluation and auditing frameworks for regulatory compliance, and (3) addressing new regulation challenges posed by large generative models. Beyond immediate regulatory compliance, this work establishes foundations for trustworthy AI systems where users maintain meaningful control over their data contributions.

## 2. Methodology

### 2.1 Framework Overview

HUA-LoRA operates through two complementary mechanisms: **domain-partitioned training** that compartmentalizes knowledge acquisition, and **targeted multiplicative decay** that enables selective forgetting. The framework assumes access to training data with domain labels (natural or assigned) and operates during the fine-tuning phase of LLM development.

### 2.2 Domain-Partitioned LoRA Architecture

#### 2.2.1 Low-Rank Adapter Formulation

We build upon Low-Rank Adaptation (LoRA), which augments frozen pre-trained weights $W_0 \in \mathbb{R}^{d \times k}$ with trainable low-rank decomposition:

$$h = W_0 x + \Delta W x = W_0 x + BA x$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$, and rank $r \ll \min(d, k)$. This formulation reduces trainable parameters while maintaining expressiveness.

#### 2.2.2 Domain Partitioning Strategy

Let $\mathcal{D} = \{D_1, D_2, ..., D_K\}$ represent $K$ domain partitions of the training data. We instantiate $K$ independent LoRA adapter pairs $\{(A_i, B_i)\}_{i=1}^{K}$, each dedicated to a specific domain. During training, data from domain $D_i$ exclusively updates adapter $(A_i, B_i)$:

$$\mathcal{L}_i = \mathbb{E}_{(x,y) \sim D_i} \left[ \ell(f_{W_0 + B_i A_i}(x), y) \right]$$

where $\ell$ is the task-specific loss function. This isolation ensures that knowledge from domain $D_i$ is localized to adapter $i$, minimizing cross-domain interference.

#### 2.2.3 Routing Mechanism

For inference, we employ a lightweight routing function $\phi: \mathcal{X} \rightarrow [K]$ that maps inputs to their corresponding domain adapter:

$$h = W_0 x + B_{\phi(x)} A_{\phi(x)} x$$

The router can be implemented as a simple classifier trained on domain labels or derived from metadata (e.g., user ID, data source). For unlearning requests, the router identifies which adapter(s) contain the target data's influence.

### 2.3 Multiplicative Weight Decay for Unlearning

#### 2.3.1 Neuroscience-Inspired Decay Mechanism

Drawing from synaptic decay principles in neuroscience and the Focused Neural Network (FNN) framework, we implement multiplicative weight decay that progressively weakens learned representations. For adapter $(A_i, B_i)$ targeted for unlearning, we apply:

$$A_i^{(t+1)} = \lambda_A \cdot A_i^{(t)} + \eta \cdot \nabla_{A_i} \mathcal{L}_{retain}$$
$$B_i^{(t+1)} = \lambda_B \cdot B_i^{(t)} + \eta \cdot \nabla_{B_i} \mathcal{L}_{retain}$$

where $\lambda_A, \lambda_B \in (0, 1)$ are decay factors, $\eta$ is the learning rate, and $\mathcal{L}_{retain}$ is computed on retained data to preserve utility. The decay factors follow a schedule:

$$\lambda^{(t)} = \lambda_{init} \cdot \gamma^t$$

where $\gamma \in (0, 1)$ controls decay acceleration. This exponential schedule initially preserves structure while progressively eliminating learned patterns.

#### 2.3.2 Selective Forgetting Algorithm

**Algorithm 1: HUA-LoRA Unlearning Procedure**

```
Input: Target domain index i, decay schedule {λ^(t)}, epochs T, retain set D_retain
Output: Updated adapter (A_i', B_i') with forgotten knowledge

1. Initialize: A_i' ← A_i, B_i' ← B_i
2. For t = 1 to T:
   a. Sample batch (x, y) from D_retain
   b. Compute retain loss: L_retain = ℓ(f_{W_0 + B_i' A_i'}(x), y)
   c. Apply multiplicative decay:
      A_i' ← λ^(t) · A_i' + η · ∇_{A_i'} L_retain
      B_i' ← λ^(t) · B_i' + η · ∇_{B_i'} L_retain
   d. Verify forgetting progress via MIA on forget set
3. Return (A_i', B_i')
```

#### 2.3.3 Cross-Adapter Interference Mitigation

To address potential knowledge leakage across adapters, we introduce an interference regularization term during training:

$$\mathcal{L}_{total} = \sum_{i=1}^{K} \mathcal{L}_i + \alpha \sum_{i \neq j} \|A_i^T A_j\|_F^2$$

where $\alpha$ controls the orthogonality constraint strength. This encourages adapters to learn in orthogonal subspaces, minimizing cross-domain interference.

### 2.4 Verification Protocol

#### 2.4.1 Membership Inference Attack (MIA) Evaluation

We employ MIA as the primary verification mechanism, following the MIAU framework. For a trained model $f$ and candidate sample $x$, the MIA success rate measures whether an adversary can determine if $x$ was in the training set:

$$\text{MIA}_{success} = \frac{1}{|D_{test}|} \sum_{x \in D_{test}} \mathbb{1}[\text{Attack}(f, x) = \text{member}(x)]$$

Post-unlearning, we target MIA success rate < 10% on the forget set (compared to ~50% baseline for random guessing).

#### 2.4.2 MIAU Score Computation

The MIAU score provides a normalized measure of forgetting efficacy:

$$\text{MIAU} = 1 - \frac{\text{MIA}_{success}^{unlearned} - 0.5}{\text{MIA}_{success}^{original} - 0.5}$$

A score > 0.9 indicates effective forgetting approaching the theoretical optimum.

#### 2.4.3 Statistical Verification (SMIA)

We employ the Statistical MIA (SMIA) test with hypothesis testing framework:

- $H_0$: The model has effectively forgotten the target data
- $H_1$: Residual data influence remains detectable

Using likelihood ratio tests with significance level $\alpha = 0.05$, we verify that unlearned models cannot be distinguished from models never trained on the target data.

### 2.5 Experimental Design

#### 2.5.1 Model and Dataset Configuration

**Base Model**: LLaMA-7B (frozen pre-trained weights)

**Datasets**:
- **RedPajama**: Multi-domain corpus with natural partitions (CommonCrawl, Wikipedia, Books, ArXiv, GitHub, StackExchange)
- **C4**: Web-crawled text with source metadata for domain assignment
- **WikiMem**: Specialized benchmark for memorization and unlearning evaluation

**Domain Partitioning**: $K \in \{10, 50, 100\}$ domains based on source metadata

#### 2.5.2 Hyperparameter Configuration

| Parameter | Values | Rationale |
|-----------|--------|-----------|
| LoRA rank $r$ | {8, 16, 32, 64} | Trade-off between capacity and localization |
| Decay rate $\lambda_{init}$ | {0.1, 0.5, 0.9} | Forgetting speed vs. stability |
| Decay acceleration $\gamma$ | {0.9, 0.95, 0.99} | Schedule aggressiveness |
| Interference weight $\alpha$ | {0.01, 0.1, 1.0} | Orthogonality constraint strength |
| Unlearning epochs $T$ | {5, 10, 20} | Convergence requirements |

#### 2.5.3 Experimental Conditions

**Full Factorial Design**: 27 configurations (3 decay rates × 3 accelerations × 3 interference weights) × 5 random seeds = 135 experimental runs

**Baselines**:
1. **Full Retraining**: Gold standard for exact unlearning
2. **Gradient Ascent**: Standard approximate unlearning
3. **SISA**: Sharded training with isolated retraining
4. **AdapterSwap**: Simple adapter removal without decay
5. **LUNE**: State-of-the-art LLM unlearning method

#### 2.5.4 Evaluation Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Forgetting Efficacy | MIA success < 10% | MIA attack on forget set |
| MIAU Score | > 0.9 | Normalized forgetting measure |
| Utility Retention | > 95% | Perplexity/accuracy on retain set |
| Computational Efficiency | < 1% retraining cost | GPU-hours comparison |
| Cross-Adapter Interference | < 20% | Activation overlap analysis |

#### 2.5.5 Statistical Analysis

- **Primary Analysis**: Paired t-tests comparing HUA-LoRA to baselines ($\alpha = 0.05$)
- **Effect Size**: Cohen's d with 95% confidence intervals
- **Multiple Comparisons**: Bonferroni correction for baseline comparisons
- **Sample Size Justification**: $n \geq 15$ per condition for 80% power to detect medium effects

### 2.6 Ablation Studies

1. **Domain Granularity**: Vary $K$ from 10 to 100 to assess localization-efficiency trade-offs
2. **Decay Mechanism**: Compare multiplicative decay to additive decay and gradient ascent
3. **Interference Regularization**: Evaluate impact of orthogonality constraints
4. **Adapter Rank**: Assess how rank affects both utility and forgetting efficacy

## 3. Expected Outcomes & Impact

### 3.1 Technical Outcomes

We anticipate HUA-LoRA will achieve:

1. **Verified Forgetting**: MIA success rate < 10% on forget sets, with MIAU scores > 0.9, demonstrating forgetting efficacy comparable to full retraining.

2. **Preserved Utility**: Retain set performance within 5% of original model, measured by perplexity and downstream task accuracy.

3. **Computational Efficiency**: Unlearning operations requiring < 1% of full retraining compute, enabling practical deployment for frequent deletion requests.

4. **Bounded Interference**: Cross-adapter activation overlap < 20%, validating the compartmentalization hypothesis.

### 3.2 Scientific Contributions

1. **Novel Architecture**: First framework combining domain-partitioned adapters with targeted decay for LLM unlearning, establishing a new paradigm for compliant model development.

2. **Verification Protocol**: Rigorous MIA-based verification methodology applicable beyond this specific framework, advancing the field of unlearning evaluation.

3. **Empirical Insights**: Comprehensive analysis of knowledge localization in adapter-based fine-tuning, informing future architectural decisions.

### 3.3 Regulatory Impact

HUA-LoRA directly operationalizes GDPR Article 17 for LLM deployments by providing:

1. **Auditable Compliance**: Quantitative verification metrics that regulators can assess
2. **Practical Implementation**: Computationally feasible unlearning for production systems
3. **Scalable Architecture**: Framework applicable to models of varying sizes and domains

### 3.4 Broader Implications

This research establishes foundations for trustworthy AI systems where data subjects maintain meaningful control over their contributions. By demonstrating that regulatory compliance and model utility are not mutually exclusive, HUA-LoRA encourages responsible AI development practices. The framework's principles extend beyond GDPR to other regulatory contexts requiring selective information removal, including copyright compliance for generative models and safety-critical applications requiring knowledge quarantine.

### 3.5 Limitations and Future Directions

We acknowledge several limitations requiring future investigation: (1) the framework assumes training-time access for domain partitioning, limiting applicability to pre-trained base models; (2) domain label availability may vary across deployment contexts; (3) adversarial attacks specifically targeting partitioned architectures require further security analysis. Future work will explore retrofit mechanisms for existing models, automated domain discovery, and formal privacy guarantees through differential privacy integration.