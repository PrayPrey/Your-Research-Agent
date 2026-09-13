# Research Proposal: Isolation-Aware Mixture-of-Experts Training for Efficient and Surgical Machine Unlearning

## 1. Introduction

### Background

The rapid proliferation of large-scale deep learning models has created unprecedented capabilities in artificial intelligence, yet it has simultaneously introduced significant challenges in model governance, privacy compliance, and sustainable development. One particularly pressing concern is **machine unlearning**—the ability to selectively remove specific knowledge from trained models without compromising their overall utility. This capability has become legally mandated in many jurisdictions through regulations such as the European Union's General Data Protection Regulation (GDPR), which establishes individuals' "right to be forgotten," and similar frameworks emerging globally.

Current approaches to machine unlearning in monolithic neural networks face fundamental limitations rooted in the entangled nature of learned representations. In conventional architectures, knowledge is distributed diffusely across millions or billions of parameters, making targeted removal computationally prohibitive and often catastrophically damaging to model performance. Existing methods typically require either complete retraining from scratch—negating the efficiency gains of the original training—or approximate techniques such as gradient ascent, influence function estimation, or knowledge distillation, which frequently fail to achieve complete forgetting while degrading performance on retained knowledge.

The emerging paradigm of **Mixture-of-Experts (MoE)** architectures presents a compelling alternative framework for addressing the unlearning challenge. MoE models partition computation across multiple specialized expert networks, with learned routers directing inputs to relevant expert subsets. This inherent modularity suggests the possibility of **surgical unlearning**: if specific knowledge can be localized within dedicated experts, removal could become a targeted operation affecting only relevant parameters while preserving the broader model's capabilities.

However, current MoE training methodologies do not explicitly optimize for knowledge isolation. Standard load-balancing objectives and routing mechanisms distribute information across experts based on computational efficiency rather than semantic coherence, resulting in knowledge entanglement that undermines unlearning potential. Recent work such as GRIP (Zhu et al., 2026) has begun addressing unlearning in MoE through geometric router constraints, yet these approaches operate post-hoc on models not designed for compartmentalization.

### Research Objectives

This research proposes **Isolation-Aware MoE Training (IA-MoE)**, a novel framework that fundamentally reconceptualizes MoE training to enable efficient machine unlearning through explicit knowledge compartmentalization. Our primary objectives are:

1. **Develop domain-guided routing regularization** techniques that encourage consistent assignment of semantically coherent data categories to dedicated expert subsets during training.

2. **Design sparse activation tracking mechanisms** that maintain lightweight, queryable mappings between data sources and expert utilization patterns.

3. **Establish surgical unlearning protocols** that leverage compartmentalized knowledge for near-instantaneous, minimally disruptive forgetting operations.

4. **Validate the framework** across text and image domains using established unlearning benchmarks, demonstrating superior forgetting efficacy, utility retention, and computational efficiency compared to existing approaches.

### Significance

This research addresses critical needs at the intersection of machine learning methodology, privacy engineering, and sustainable AI development. By enabling efficient unlearning, IA-MoE directly supports regulatory compliance while dramatically reducing the computational and environmental costs associated with model retraining. Furthermore, the explicit knowledge compartmentalization achieved through our approach has broader implications for model interpretability, continual learning, and collaborative model development—key themes in the advancement of modular deep learning systems.

## 2. Methodology

### 2.1 Problem Formulation

Consider a Mixture-of-Experts model with $N$ experts $\{E_1, E_2, \ldots, E_N\}$ and a router network $R$. For an input $x$, the router produces gating weights $g(x) = [g_1(x), \ldots, g_N(x)]$ where typically:

$$g(x) = \text{TopK}(\text{softmax}(W_r \cdot h(x)))$$

where $h(x)$ is an intermediate representation and $W_r$ are router parameters. The model output is:

$$y = \sum_{i=1}^{N} g_i(x) \cdot E_i(x)$$

**Unlearning Problem**: Given a trained MoE model $\mathcal{M}$ and a forget set $\mathcal{D}_f \subset \mathcal{D}_{train}$, produce an updated model $\mathcal{M}'$ such that:
- $\mathcal{M}'$ behaves as if never trained on $\mathcal{D}_f$ (forgetting criterion)
- $\mathcal{M}'$ maintains performance on retain set $\mathcal{D}_r = \mathcal{D}_{train} \setminus \mathcal{D}_f$ (utility criterion)

### 2.2 Isolation-Aware MoE Training Framework

#### 2.2.1 Domain-Guided Routing Regularization

We introduce auxiliary losses that encourage the router to consistently assign data from identifiable semantic categories to dedicated expert subsets. Let $\mathcal{C} = \{c_1, c_2, \ldots, c_M\}$ denote a set of identifiable data categories (e.g., user IDs, topic labels, content domains).

**Category-Expert Affinity Matrix**: We maintain a learnable soft assignment matrix $A \in \mathbb{R}^{M \times N}$ where $A_{c,i}$ represents the target affinity between category $c$ and expert $E_i$. This matrix is initialized uniformly and updated during training.

**Isolation Loss**: For a batch of inputs $\{(x_j, c_j)\}$ where $c_j$ denotes the category label, we define:

$$\mathcal{L}_{isolation} = \frac{1}{|\mathcal{B}|} \sum_{j \in \mathcal{B}} D_{KL}(g(x_j) \| \tilde{A}_{c_j})$$

where $\tilde{A}_{c_j} = \text{softmax}(A_{c_j} / \tau)$ is the temperature-scaled target distribution and $\tau$ is an annealing temperature.

**Mutual Information Minimization**: To further encourage separation, we minimize mutual information between expert activations for different categories:

$$\mathcal{L}_{MI} = \sum_{c \neq c'} I(G_c; G_{c'})$$

where $G_c$ represents the aggregated gating distribution for category $c$. We estimate this using a variational upper bound:

$$\mathcal{L}_{MI} \approx \sum_{c \neq c'} \mathbb{E}[\log q_\phi(G_c | G_{c'})] - H(G_c)$$

where $q_\phi$ is a learned discriminator network.

**Complete Training Objective**: The total loss combines task performance with isolation objectives:

$$\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda_1 \mathcal{L}_{isolation} + \lambda_2 \mathcal{L}_{MI} + \lambda_3 \mathcal{L}_{balance}$$

where $\mathcal{L}_{balance}$ is the standard load-balancing loss and $\lambda_1, \lambda_2, \lambda_3$ are hyperparameters.

#### 2.2.2 Sparse Activation Tracking

We maintain a lightweight activation logging system that records expert utilization patterns without storing raw data:

**Activation Log Structure**: For each category $c$, we maintain:
- **Expert frequency vector**: $F_c \in \mathbb{R}^N$ counting activations per expert
- **Activation strength matrix**: $S_c \in \mathbb{R}^{N \times L}$ storing average gating weights across $L$ layers
- **Sample count**: $n_c$ tracking total samples processed

**Incremental Update**: For each training sample $(x, c)$:

$$F_c \leftarrow F_c + \mathbb{1}[g(x) > 0]$$
$$S_c \leftarrow \frac{n_c \cdot S_c + g(x)}{n_c + 1}$$
$$n_c \leftarrow n_c + 1$$

**Storage Efficiency**: The activation log requires $O(M \times N \times L)$ storage, independent of dataset size, making it practical for large-scale deployments.

#### 2.2.3 Surgical Unlearning Protocol

When an unlearning request for category $c_f$ is received, the protocol proceeds in three phases:

**Phase 1: Expert Identification**
Identify the set of implicated experts $\mathcal{E}_f$ using the activation log:

$$\mathcal{E}_f = \{E_i : F_{c_f,i} / n_{c_f} > \theta_{act}\}$$

where $\theta_{act}$ is an activation threshold (typically 0.1).

**Phase 2: Contamination Assessment**
For each implicated expert, compute contamination ratio:

$$\rho_i = \frac{F_{c_f,i}}{\sum_{c \in \mathcal{C}} F_{c,i}}$$

This ratio determines the unlearning strategy for each expert.

**Phase 3: Surgical Intervention**
Apply category-specific interventions:

- **High contamination** ($\rho_i > 0.8$): Complete expert reinitialization
  $$E_i \leftarrow \text{Init}(E_i)$$
  
- **Medium contamination** ($0.3 < \rho_i \leq 0.8$): Targeted fine-tuning on retain set
  $$E_i \leftarrow E_i - \eta \nabla_{E_i} \mathcal{L}_{retain}(\mathcal{D}_r)$$
  with other experts frozen
  
- **Low contamination** ($\rho_i \leq 0.3$): Router adjustment only
  $$A_{c_f, i} \leftarrow -\infty$$

**Router Update**: After expert intervention, fine-tune router parameters to redirect queries previously routed to affected experts:

$$W_r \leftarrow W_r - \eta_r \nabla_{W_r} \mathcal{L}_{redirect}$$

where $\mathcal{L}_{redirect}$ encourages redistribution of $c_f$-like queries to non-implicated experts.

### 2.3 Experimental Design

#### 2.3.1 Datasets and Domains

**Text Domain**:
- **TOFU Benchmark**: Synthetic biography dataset with clear entity boundaries for unlearning evaluation
- **MultiNews**: Multi-domain news corpus for topic-based compartmentalization
- **Enron Email Corpus**: User-specific communication data for user-level unlearning

**Image Domain**:
- **CIFAR-100**: Class-based compartmentalization with hierarchical structure
- **CelebA**: Identity-based unlearning with attribute annotations
- **ImageNet-100**: Large-scale evaluation with domain diversity

#### 2.3.2 Baseline Methods

We compare against:
1. **Full Retraining**: Gold standard for complete unlearning
2. **Gradient Ascent**: Standard approximate unlearning via loss maximization on forget set
3. **SISA (Sharded, Isolated, Sliced, and Aggregated)**: Ensemble-based exact unlearning
4. **Influence Functions**: Sample-weighted parameter updates
5. **GRIP**: State-of-the-art MoE unlearning via geometric router constraints
6. **Standard MoE + Unlearning**: Baseline MoE without isolation-aware training

#### 2.3.3 Evaluation Metrics

**Forgetting Efficacy**:
- **Membership Inference Attack (MIA) Accuracy**: Should approach random (50%) for forgotten data
- **Extraction Attack Success Rate**: Measure information leakage about forgotten data
- **Model Inversion Distance**: Semantic distance between reconstructed and original forgotten samples

**Utility Retention**:
- **Retain Set Accuracy**: Performance on data not targeted for unlearning
- **Generalization Gap**: Difference between pre- and post-unlearning performance
- **Cross-domain Transfer**: Performance on held-out domains

**Computational Efficiency**:
- **Unlearning Time**: Wall-clock time for complete unlearning operation
- **FLOPs Ratio**: Computational cost relative to full retraining
- **Memory Overhead**: Additional storage required for activation logs

**Isolation Quality**:
- **Expert Purity Score**: Entropy of category distribution per expert
- **Routing Consistency**: Variance of expert assignments for same-category inputs
- **Compartmentalization Index**: Novel metric measuring knowledge localization

#### 2.3.4 Implementation Details

**Model Architecture**: Transformer-based MoE with 8-32 experts per layer, top-2 routing, and 125M-1.3B total parameters.

**Training Configuration**: 
- Isolation hyperparameters: $\lambda_1 = 0.1$, $\lambda_2 = 0.05$, $\lambda_3 = 0.01$
- Temperature annealing: $\tau: 1.0 \rightarrow 0.1$ over training
- Activation threshold: $\theta_{act} = 0.1$

**Ablation Studies**:
1. Impact of isolation loss weight $\lambda_1$
2. Number of experts vs. compartmentalization quality
3. Category granularity effects
4. Activation threshold sensitivity

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Performance**: We anticipate IA-MoE will achieve:
   - 95%+ forgetting efficacy (MIA accuracy < 52%) compared to 70-85% for baseline methods
   - <3% utility degradation on retain sets versus 5-15% for gradient-based approaches
   - 10-100× speedup over full retraining for unlearning operations
   - Near-constant unlearning time regardless of model size (dependent only on affected expert count)

2. **Qualitative Insights**: 
   - Emergence of semantically coherent expert specialization
   - Clear visualization of knowledge boundaries through routing patterns
   - Interpretable unlearning decisions via activation logs

3. **Methodological Contributions**:
   - Novel isolation-aware training objectives with theoretical grounding
   - Efficient activation tracking system scalable to billion-parameter models
   - Comprehensive surgical unlearning protocol with multiple intervention strategies

### Broader Impact

**Privacy and Compliance**: IA-MoE provides a practical pathway for organizations to implement data subject rights at scale, potentially transforming how AI systems handle personal data throughout their lifecycle.

**Sustainable AI Development**: By enabling targeted modifications rather than complete retraining, this work contributes to reducing the environmental footprint of AI systems and supports the broader goal of sustainable machine learning.

**Modular AI Paradigm**: The explicit knowledge compartmentalization techniques developed here extend beyond unlearning to support continual learning, model editing, and collaborative development—advancing the vision of truly modular deep learning systems.

**Reproducibility Commitment**: All code, trained models, and evaluation protocols will be released publicly to enable community validation and extension of this work.