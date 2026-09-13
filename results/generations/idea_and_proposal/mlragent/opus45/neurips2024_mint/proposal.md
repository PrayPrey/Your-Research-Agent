# Research Proposal: Sparse Activation Steering: Targeted Interventions via Learned Intervention Masks

## 1. Introduction

### Background

Foundation models, including large language models (LLMs) and vision-language models, have demonstrated remarkable capabilities across diverse tasks. However, their increasing deployment raises critical concerns about generating harmful content, perpetuating societal biases, and enabling potential misuse. Traditional approaches to mitigating these risks—such as reinforcement learning from human feedback (RLHF) or full fine-tuning—are computationally expensive, may compromise general capabilities, and often lack interpretability regarding *where* behavioral control is enacted within the model.

Activation engineering has emerged as a promising paradigm for fine-grained control over model behavior without retraining. Methods such as steering vectors, contrastive activation addition, and activation patching enable targeted modifications by intervening directly on intermediate representations during inference. Recent advances have demonstrated the effectiveness of sparse representations—particularly through sparse autoencoders (SAEs)—for creating interpretable and targeted interventions. However, a fundamental challenge persists: current methods either apply interventions uniformly across layers and dimensions, potentially disrupting unrelated capabilities, or rely on manual heuristics to identify intervention points, limiting their precision and scalability.

The literature reveals significant progress in this domain. SAE-SSV (He et al., 2025) demonstrates that supervised steering in sparse representation spaces achieves higher success rates with minimal quality degradation. LinEAS (Rodriguez et al., 2025) shows that end-to-end learning with global loss functions can effectively mitigate toxicity through sparse interventions. Additionally, work on activation space transferability (Oozeer et al., 2025) suggests that intervention mechanisms may generalize across models. Despite these advances, key challenges remain: (1) identifying the *minimal* set of activation dimensions requiring intervention, (2) balancing behavioral control with capability preservation, and (3) achieving computational efficiency during deployment.

### Research Objectives

This research proposes **Sparse Activation Steering (SAS)**, a novel framework for learning lightweight binary intervention masks that identify the minimal subset of activation dimensions requiring modification for targeted behavioral control. Our specific objectives are:

1. **Develop a principled mask learning framework** using differentiable relaxations that discovers critical intervention points through end-to-end optimization.
2. **Design a joint optimization procedure** that simultaneously learns intervention masks and steering vectors while preserving model capabilities.
3. **Quantify the trade-off** between intervention sparsity, control effectiveness, and capability retention across multiple foundation models and behavioral modification tasks.
4. **Extract mechanistic insights** about where specific behaviors are encoded within foundation models.

### Significance

This research addresses a core challenge in foundation model safety: achieving precise behavioral control without broad capability degradation. By learning to intervene only where necessary, SAS promises interventions requiring 10-100× fewer modified activations than existing methods. This surgical approach not only improves efficiency but also enhances interpretability—the learned masks reveal which model components encode specific behaviors. The framework directly contributes to the MINT workshop's goals of understanding inner workings and developing actionable intervention mechanisms.

## 2. Methodology

### 2.1 Problem Formulation

Let $f_\theta$ denote a foundation model with parameters $\theta$, producing activations $\mathbf{a}_l \in \mathbb{R}^{d_l}$ at layer $l \in \{1, \ldots, L\}$. Given a target behavior modification task $\mathcal{T}$ (e.g., toxicity suppression), we seek to learn:

1. **Binary masks** $\mathbf{m}_l \in \{0, 1\}^{d_l}$ identifying intervention points at each layer
2. **Steering vectors** $\mathbf{s}_l \in \mathbb{R}^{d_l}$ specifying the direction and magnitude of intervention

The intervened activation at layer $l$ becomes:
$$\tilde{\mathbf{a}}_l = \mathbf{a}_l + \mathbf{m}_l \odot \mathbf{s}_l$$

where $\odot$ denotes element-wise multiplication. Our goal is to learn $\{\mathbf{m}_l, \mathbf{s}_l\}_{l=1}^L$ such that interventions are maximally sparse while achieving the desired behavioral change and preserving general capabilities.

### 2.2 Mask Learning via Gumbel-Softmax Relaxation

Since binary masks are non-differentiable, we employ the Gumbel-Softmax relaxation to enable gradient-based optimization. For each dimension $i$ at layer $l$, we parameterize the mask probability through learnable logits $\boldsymbol{\pi}_l \in \mathbb{R}^{d_l}$:

$$\tilde{m}_{l,i} = \sigma\left(\frac{\log\pi_{l,i} - \log(1-\pi_{l,i}) + g_1 - g_0}{\tau}\right)$$

where $g_0, g_1 \sim \text{Gumbel}(0, 1)$ are i.i.d. Gumbel noise samples, $\sigma(\cdot)$ is the sigmoid function, and $\tau > 0$ is the temperature parameter. During training, we anneal $\tau$ from a high value (enabling exploration) to near-zero (approximating discrete masks). At inference, we binarize: $m_{l,i} = \mathbb{1}[\tilde{m}_{l,i} > 0.5]$.

### 2.3 Joint Optimization Framework

We formulate a multi-objective loss function combining three components:

**Task Loss ($\mathcal{L}_{\text{task}}$)**: Measures the effectiveness of behavioral modification. For toxicity suppression, we use:
$$\mathcal{L}_{\text{task}} = \mathbb{E}_{x \sim \mathcal{D}_{\text{task}}} \left[ \text{ToxicityScore}(f_\theta^{\text{int}}(x)) \right]$$

where $f_\theta^{\text{int}}$ denotes the model with interventions applied and $\mathcal{D}_{\text{task}}$ is a dataset of prompts that typically elicit toxic responses.

**Sparsity Loss ($\mathcal{L}_{\text{sparse}}$)**: Encourages minimal intervention:
$$\mathcal{L}_{\text{sparse}} = \sum_{l=1}^{L} \|\tilde{\mathbf{m}}_l\|_1 = \sum_{l=1}^{L} \sum_{i=1}^{d_l} \tilde{m}_{l,i}$$

**Capability Preservation Loss ($\mathcal{L}_{\text{cap}}$)**: Penalizes degradation on general benchmarks:
$$\mathcal{L}_{\text{cap}} = \mathbb{E}_{x \sim \mathcal{D}_{\text{gen}}} \left[ D_{\text{KL}}\left(f_\theta(x) \| f_\theta^{\text{int}}(x)\right) \right] + \lambda_{\text{ppl}} \cdot \Delta\text{PPL}$$

where $\mathcal{D}_{\text{gen}}$ represents general capability data, $D_{\text{KL}}$ is the KL divergence between output distributions, and $\Delta\text{PPL}$ measures perplexity increase on held-out text.

The total objective is:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \alpha \cdot \mathcal{L}_{\text{sparse}} + \beta \cdot \mathcal{L}_{\text{cap}}$$

where $\alpha$ and $\beta$ are hyperparameters controlling the trade-off between objectives.

### 2.4 Algorithmic Procedure

**Algorithm 1: Sparse Activation Steering (SAS)**

```
Input: Foundation model f_θ, task dataset D_task, general dataset D_gen
Output: Learned masks {m_l} and steering vectors {s_l}

1. Initialize logits π_l ~ N(0, 0.01), steering vectors s_l ~ N(0, 0.01)
2. Set temperature τ = 5.0
3. For epoch = 1 to E:
   4.   For batch (x_task, x_gen) from (D_task, D_gen):
   5.     Sample Gumbel noise and compute soft masks m̃_l
   6.     Apply interventions: ã_l = a_l + m̃_l ⊙ s_l
   7.     Compute L_task from modified outputs
   8.     Compute L_sparse from soft masks
   9.     Compute L_cap from distribution divergence
   10.    L_total = L_task + α·L_sparse + β·L_cap
   11.    Update {π_l, s_l} via Adam optimizer
   12.  Anneal temperature: τ = max(0.1, τ · 0.99)
13. Binarize masks: m_l = 1[σ(π_l) > 0.5]
14. Return {m_l, s_l}
```

### 2.5 Sparse Autoencoder Integration (Optional Enhancement)

To enhance interpretability, we optionally project interventions into sparse autoencoder (SAE) latent spaces. Given a pre-trained SAE with encoder $E$ and decoder $D$, we learn masks in the sparse latent space:

$$\mathbf{z}_l = E(\mathbf{a}_l), \quad \tilde{\mathbf{z}}_l = \mathbf{z}_l + \mathbf{m}_l^z \odot \mathbf{s}_l^z, \quad \tilde{\mathbf{a}}_l = D(\tilde{\mathbf{z}}_l)$$

This variant enables direct interpretation of which semantic features are modified.

### 2.6 Experimental Design

**Models**: We evaluate on three foundation models of varying scales:
- Llama-2-7B and Llama-3-8B (language models)
- CLIP ViT-L/14 (vision-language model)

**Behavioral Modification Tasks**:
1. **Toxicity Suppression**: Using RealToxicityPrompts and the Perspective API
2. **Bias Mitigation**: Reducing gender and racial biases using StereoSet and BBQ benchmarks
3. **Refusal Behavior**: Modifying responses to harmful requests

**Capability Preservation Benchmarks**:
- Language: MMLU, HellaSwag, ARC-Challenge, TriviaQA
- Vision: ImageNet classification, visual question answering

**Baselines**:
1. Full steering vectors (Activation Addition)
2. SAE-SSV (supervised steering in sparse spaces)
3. LinEAS (end-to-end sparse interventions)
4. Random sparse interventions (control)
5. Layer-specific interventions (fixed layers)

**Evaluation Metrics**:
- **Control Effectiveness**: Attack success rate (ASR) reduction, toxicity score reduction
- **Sparsity**: Percentage of activated mask dimensions ($\sum_l \|\mathbf{m}_l\|_0 / \sum_l d_l$)
- **Capability Retention**: Relative performance on benchmarks vs. unmodified model
- **Computational Cost**: FLOPs overhead during inference
- **Interpretability**: Alignment of masked dimensions with known feature directions

**Ablation Studies**:
1. Effect of sparsity coefficient $\alpha$
2. Layer-wise mask distribution analysis
3. Temperature annealing schedule impact
4. SAE vs. direct activation space interventions

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Results**: We anticipate SAS will achieve:
   - 80-90% reduction in toxicity scores with only 1-5% of activation dimensions modified (10-100× sparser than uniform steering)
   - Less than 2% degradation on capability benchmarks (MMLU, HellaSwag)
   - Inference overhead below 5% compared to baseline model

2. **Mechanistic Insights**: The learned masks will reveal:
   - Layer-wise distribution of behavior-relevant representations (we hypothesize concentration in middle-to-late layers)
   - Dimension-level localization enabling targeted interpretability analysis
   - Potential overlap or independence between different behavioral modification tasks

3. **Transferability Analysis**: We expect partial transferability of masks across:
   - Different prompts eliciting similar behaviors
   - Models within the same family (e.g., Llama-2 to Llama-3)

4. **Open-Source Artifacts**: We will release:
   - Pre-trained masks for common behavioral modifications
   - Efficient inference implementation with learned sparse interventions
   - Analysis toolkit for mask visualization and interpretation

### Broader Impact

**Scientific Contributions**: This work advances the understanding of how specific behaviors are encoded within foundation models. By revealing the minimal circuits responsible for undesirable outputs, SAS contributes to mechanistic interpretability research and provides a principled framework for surgical model modifications.

**Practical Applications**: The learned sparse interventions enable:
- Efficient safety guardrails deployable at inference time
- Customizable behavior controls for different deployment contexts
- Reduced computational overhead compared to multiple model variants

**Safety Considerations**: While this research aims to improve model safety, we acknowledge dual-use concerns—the same framework could theoretically be misused to suppress desirable behaviors. We will include responsible disclosure guidelines and focus on defensive applications.

**Limitations and Future Work**: SAS requires task-specific training data and may not generalize to out-of-distribution behavioral modifications. Future work should explore:
- Zero-shot mask transfer across tasks
- Dynamic mask adaptation during inference
- Integration with constitutional AI approaches

In summary, Sparse Activation Steering provides a principled, efficient, and interpretable framework for targeted behavioral control in foundation models, directly addressing the MINT workshop's mission of developing actionable mechanisms for safer AI systems.