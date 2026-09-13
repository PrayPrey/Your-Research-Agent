# Research Proposal: Concept-Aligned Sparse Autoencoders via Self-Generated Contrastive Learning for Interpretable LLM Features

## 1. Introduction

### 1.1 Background

The rapid advancement of large language models (LLMs) has revolutionized artificial intelligence, enabling unprecedented capabilities in natural language understanding, generation, and reasoning. However, as these models scale to billions of parameters and are deployed in high-stakes domains such as healthcare diagnostics, legal decision-making, and financial risk assessment, the imperative for interpretability has become paramount. Understanding *why* a model produces a particular output is no longer merely an academic curiosity—it is a fundamental requirement for ensuring safety, fairness, accountability, and alignment with human values.

Interpretability research spans a broad spectrum of approaches. Classical methods, designed for tabular data and smaller models, leverage inherently transparent architectures such as decision trees, rule-based systems, and sparse linear models. These approaches provide faithful explanations by construction, as the model's decision process is directly observable. However, they struggle to scale to the complexity of modern foundation models. On the opposite end, post-hoc explainability methods attempt to explain black-box models after training, but these explanations may be unfaithful—they describe what the explanation method *thinks* the model does, not necessarily what the model *actually* does.

Sparse Autoencoders (SAEs) have emerged as a promising middle ground for mechanistic interpretability of LLMs. By learning sparse, overcomplete representations of neural network activations, SAEs decompose the superposed representations in LLMs into interpretable features. Recent industrial-scale efforts such as Gemma Scope and Llama Scope have demonstrated that SAEs can scale to hundreds of thousands of features while maintaining interpretability. However, a critical limitation persists: the meaning of discovered features is typically assigned through post-hoc labeling, where human annotators or automated systems examine top-activating examples and generate descriptions. This process introduces a faithfulness gap—the assigned labels may not accurately reflect the causal role of features in model computation.

### 1.2 Research Problem

The fundamental challenge addressed in this proposal is the **semantic grounding problem** for SAE features in LLMs. Unlike vision models, which can leverage external grounding through object detectors or image-text pairs (as demonstrated by VLG-CBM achieving 4-51% improvement in concept faithfulness), language models lack equivalent semantic anchors. Current SAE interpretability relies on post-hoc labeling that may produce unfaithful explanations, undermining the reliability of SAE-based interpretability in applications where explanation accuracy is critical.

We pose the central research question: *Can training-time concept alignment produce genuinely grounded SAE features without external supervision, using language itself as the semantic anchor?*

### 1.3 Research Objectives

This research proposes **CA-SAE-V (Concept-Aligned Sparse Autoencoder with Verification)**, a novel two-stage training framework that embeds concept structure directly into SAE feature geometry through self-generated contrastive learning. Our specific objectives are:

1. **Develop a two-stage training methodology** that first discovers meaningful feature directions through standard SAE pretraining, then aligns these features with LLM self-generated descriptions using contrastive learning.

2. **Establish a verification protocol** using activation patching to validate that aligned features exhibit description-consistent causal behavior.

3. **Demonstrate measurable improvement** in concept grounding quality (≥5% ANEC-5 improvement) while maintaining reconstruction fidelity (<20% degradation).

4. **Bridge classical and modern interpretability** by bringing faithfulness guarantees from inherently interpretable models to foundation model scale.

### 1.4 Significance

This research addresses a critical gap in the interpretability landscape. By embedding semantic grounding during training rather than post-hoc, CA-SAE-V offers several advantages:

- **Faithfulness by construction**: Features are trained to align with their descriptions, reducing the risk of unfaithful explanations.
- **Self-contained grounding**: No external supervision or annotation is required, leveraging the LLM's own linguistic capabilities.
- **Verifiable interpretability**: The activation patching verification protocol provides empirical validation of feature-concept correspondence.
- **Scalability**: The approach builds on existing SAE infrastructure and can scale to large foundation models.

The significance extends to practical applications in AI safety, model auditing, and regulatory compliance, where reliable interpretability is increasingly mandated.

---

## 2. Methodology

### 2.1 Overview of CA-SAE-V Framework

CA-SAE-V operates in two stages followed by a verification phase:

**Stage 1: SAE Pretraining** — Standard sparse autoencoder training to discover meaningful feature directions.

**Stage 2: Contrastive Concept Alignment** — Fine-tuning with InfoNCE loss to align features with self-generated descriptions.

**Verification Phase** — Activation patching to validate feature-concept correspondence.

### 2.2 Stage 1: SAE Pretraining

We employ a TopK Sparse Autoencoder architecture with expansion factor $r = 8$ and sparsity level $k = 32$. Given input activations $\mathbf{x} \in \mathbb{R}^d$ from a target layer of the LLM, the SAE computes:

$$\mathbf{z} = \text{TopK}(\text{ReLU}(\mathbf{W}_e \mathbf{x} + \mathbf{b}_e), k)$$

$$\hat{\mathbf{x}} = \mathbf{W}_d \mathbf{z} + \mathbf{b}_d$$

where $\mathbf{W}_e \in \mathbb{R}^{rd \times d}$ is the encoder, $\mathbf{W}_d \in \mathbb{R}^{d \times rd}$ is the decoder, and TopK retains only the $k$ largest activations.

The Stage 1 loss function combines reconstruction and sparsity:

$$\mathcal{L}_{\text{Stage1}} = \mathcal{L}_{\text{rec}} + \lambda_1 \mathcal{L}_{\text{sparsity}}$$

where:

$$\mathcal{L}_{\text{rec}} = \|\mathbf{x} - \hat{\mathbf{x}}\|_2^2$$

$$\mathcal{L}_{\text{sparsity}} = \|\mathbf{z}\|_1$$

We train on a large corpus (e.g., The Pile, RedPajama) for approximately 100K steps with $\lambda_1 = 0.01$.

### 2.3 Self-Description Generation

After Stage 1, we generate semantic descriptions for each feature. For feature $i$, we:

1. **Collect top-activating examples**: Identify the top-$N$ text sequences (we use $N=10$) that maximally activate feature $i$.

2. **Prompt the LLM for description**: Using a standardized template:

```
The following text examples strongly activate a particular pattern in a language model:
[Example 1]: "..."
[Example 2]: "..."
...
[Example 10]: "..."

Describe in one sentence what semantic concept or pattern these examples share:
```

3. **Generate description embedding**: Pass the generated description through the LLM and extract the final hidden state as the description embedding $\mathbf{d}_i \in \mathbb{R}^d$.

This process yields a set of (feature, description) pairs $\{(\mathbf{f}_i, \mathbf{d}_i)\}_{i=1}^{M}$ where $\mathbf{f}_i = \mathbf{W}_d[:, i]$ is the decoder column (feature direction) and $M$ is the number of aligned features (typically 1000-5000 top features by activation frequency).

### 2.4 Stage 2: Contrastive Concept Alignment

We fine-tune the SAE using InfoNCE contrastive loss to align feature representations with their descriptions. For a batch of $B$ feature-description pairs, the alignment loss is:

$$\mathcal{L}_{\text{align}} = -\frac{1}{B} \sum_{i=1}^{B} \log \frac{\exp(\text{sim}(\mathbf{f}_i, \mathbf{d}_i) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(\mathbf{f}_i, \mathbf{d}_j) / \tau)}$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity and $\tau = 0.07$ is the temperature parameter.

To preserve reconstruction quality, we maintain a combined objective:

$$\mathcal{L}_{\text{Stage2}} = \mathcal{L}_{\text{rec}} + \lambda_1 \mathcal{L}_{\text{sparsity}} + \lambda_2 \mathcal{L}_{\text{align}}$$

We set $\lambda_2 \in [0.01, 0.1]$ and fine-tune for 1-5 epochs on the alignment objective. The encoder weights $\mathbf{W}_e$ and decoder weights $\mathbf{W}_d$ are both updated, with learning rate reduced by 10× from Stage 1.

### 2.5 Verification via Activation Patching

To validate that aligned features genuinely correspond to their descriptions, we employ activation patching verification:

**Protocol for feature $i$ with description $d_i$:**

1. **Generate test prompts**: Create prompts where the concept described by $d_i$ should be relevant (positive) and irrelevant (negative).

2. **Measure baseline behavior**: Record model outputs on positive prompts without intervention.

3. **Patch feature activation**: Artificially increase/decrease feature $i$'s activation by $\pm 2\sigma$ (where $\sigma$ is the feature's activation standard deviation).

4. **Measure intervention effect**: Record changes in model output probabilities for concept-related tokens.

5. **Verify consistency**: Feature $i$ passes verification if:
   - Increasing activation increases probability of concept-related outputs
   - Decreasing activation decreases probability of concept-related outputs
   - Effect magnitude exceeds random baseline by $>2\times$

A feature is considered **verified** if it passes this protocol. We target $>70\%$ verification rate for aligned features.

### 2.6 Evaluation Metrics

**Primary Metric: Number of Effective Concepts (NEC)**

Following VLG-CBM, we compute NEC to measure concept grounding quality:

$$\text{NEC} = \exp\left(-\sum_{i=1}^{C} p_i \log p_i\right)$$

where $p_i$ represents the normalized contribution of concept $i$ to downstream predictions. Higher NEC indicates better-distributed, more interpretable concept usage.

We report **ANEC-5** (Accuracy at NEC=5), measuring downstream task accuracy when constrained to use only 5 effective concepts.

**Secondary Metrics:**

1. **Alignment Fidelity Score (AFS)**: Percentage of features passing activation patching verification.
   $$\text{AFS} = \frac{|\{\text{verified features}\}|}{|\{\text{aligned features}\}|} \times 100\%$$

2. **Reconstruction Degradation Ratio (RDR)**:
   $$\text{RDR} = \frac{\mathcal{L}_{\text{rec}}^{\text{post-align}}}{\mathcal{L}_{\text{rec}}^{\text{pre-align}}}$$
   Target: RDR $< 1.20$

3. **Human Interpretability Rating**: Expert annotators rate feature-description pairs on a 1-5 scale for accuracy and usefulness.

### 2.7 Experimental Design

**Models and Datasets:**

- **Base LLMs**: Gemma-2-2B (primary), Llama-3.1-8B (secondary)
- **Training data**: The Pile (800GB), RedPajama (1.2T tokens)
- **Evaluation tasks**: Sentiment classification, topic detection, factual recall

**Baselines:**

1. **Standard SAE**: SAE with post-hoc labeling (no alignment training)
2. **Self-explaining SAE** (Kharlapenko et al., 2024): Post-hoc self-explanation without training-time alignment
3. **PCBM** (Yuksekgonul et al., 2022): Post-hoc concept bottleneck model

**Ablation Studies:**

1. **Alignment strength**: Vary $\lambda_2 \in \{0.01, 0.05, 0.1\}$
2. **Number of aligned features**: $M \in \{500, 1000, 2500, 5000\}$
3. **Description quality**: Compare LLM self-descriptions vs. human annotations
4. **Architecture**: TopK SAE vs. Gated SAE

**Statistical Analysis:**

- Minimum 25 random seeds per configuration
- Paired t-tests with Bonferroni correction for multiple comparisons
- Effect size reporting (Cohen's d) with 95% confidence intervals
- Significance threshold: $\alpha = 0.05$

**Computational Requirements:**

- 8× A100 GPUs (80GB)
- Estimated training time: 2-4 days for full CA-SAE-V pipeline
- Storage: ~500GB for checkpoints and activations

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect CA-SAE-V to achieve ANEC-5 improvement of ≥5% over standard SAE baselines ($p < 0.05$). Based on VLG-CBM's 4-51% improvement in vision models through grounded annotation, we anticipate similar gains from training-time alignment in language models.

**Secondary Outcomes:**
- **P2 (Alignment Fidelity):** >70% of aligned features will pass activation patching verification, demonstrating genuine concept-feature correspondence.
- **P3 (Reconstruction Preservation):** Post-alignment reconstruction loss will remain within 20% of baseline, confirming that alignment does not destroy SAE quality.

**Falsification Criteria:** The hypothesis will be rejected if: (1) ANEC-5 improvement <2%, (2) alignment fidelity <50%, (3) reconstruction degradation >30%, or (4) performance worse than post-hoc self-explanation baselines.

### 3.2 Scientific Contributions

1. **Methodological Innovation:** CA-SAE-V introduces the first training-time concept alignment approach for SAE interpretability, bridging the gap between classical interpretable ML's faithfulness guarantees and modern foundation model scale.

2. **Theoretical Insight:** We demonstrate that language itself can serve as a semantic anchor for grounding neural network features, without requiring external supervision—a finding with implications for self-supervised interpretability more broadly.

3. **Verification Protocol:** The activation patching verification framework provides a principled method for validating feature-concept correspondence, addressing the faithfulness problem in mechanistic interpretability.

4. **Empirical Benchmarks:** We establish NEC-based evaluation protocols for LLM interpretability, enabling standardized comparison of future methods.

### 3.3 Practical Impact

**AI Safety and Alignment:** Verified interpretable features enable more reliable model auditing, helping identify potential failure modes, biases, or misalignment before deployment.

**Regulatory Compliance:** As AI regulations increasingly mandate explainability (e.g., EU AI Act), CA-SAE-V provides a pathway to inherently interpretable foundation models that satisfy legal requirements.

**Domain Applications:** In healthcare, finance, and legal domains where explanation accuracy is critical, CA-SAE-V offers more trustworthy interpretability than post-hoc methods.

### 3.4 Limitations and Future Directions

**Known Limitations:**
- Selective alignment (top-K features only) leaves most features ungrounded
- Self-description circularity may introduce LLM biases into feature semantics
- Scalability beyond 8B parameters remains untested

**Future Work:**
- Extension to multimodal models with cross-modal grounding
- Integration with steering and control applications
- Scaling studies on 70B+ parameter models
- Human-in-the-loop refinement of feature descriptions

### 3.5 Conclusion

CA-SAE-V represents a significant step toward bridging classical interpretability's faithfulness guarantees with modern foundation model capabilities. By embedding concept structure during training and validating through causal intervention, we move beyond post-hoc explanation toward genuinely interpretable neural network features. Success in this research would establish a new paradigm for trustworthy AI interpretability at scale.