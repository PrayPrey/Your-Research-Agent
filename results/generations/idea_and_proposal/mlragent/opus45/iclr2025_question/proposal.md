# Research Proposal: Semantic Entropy Decomposition for Efficient Hallucination Detection in Large Language Models

## 1. Introduction

### Background

Large Language Models (LLMs) have demonstrated remarkable capabilities across diverse applications, from medical diagnosis assistance to legal document analysis and autonomous decision-making systems. However, their deployment in high-stakes domains is severely constrained by a fundamental challenge: these models generate outputs with apparent confidence regardless of their actual reliability, frequently producing hallucinations—plausible but factually incorrect statements. This limitation poses significant risks in safety-critical applications where erroneous outputs can lead to severe consequences.

Uncertainty quantification (UQ) has emerged as a crucial mechanism for assessing the reliability of model predictions. Existing approaches to UQ in LLMs can be broadly categorized into sampling-based methods and single-pass estimation techniques. Sampling-based methods, exemplified by semantic entropy computation, generate multiple responses and measure their semantic consistency to estimate uncertainty. While effective, these approaches require 5-20 forward passes per query, rendering them computationally prohibitive for real-time applications. Recent surveys (Liu et al., 2025; Chen et al., 2025) have highlighted the pressing need for scalable, interpretable UQ methods that can operate efficiently at inference time.

A critical yet underexplored dimension in current UQ research is the distinction between epistemic and aleatoric uncertainty. Epistemic uncertainty arises from the model's lack of knowledge—gaps in training data or limitations in learned representations—and serves as a direct indicator of potential hallucinations. Aleatoric uncertainty, conversely, reflects inherent ambiguity in the input query itself, where multiple valid interpretations or answers may exist. Conflating these uncertainty types leads to suboptimal decision-making: epistemic uncertainty should trigger retrieval augmentation or human oversight, while aleatoric uncertainty may warrant clarification requests or acknowledgment of genuine ambiguity.

### Research Objectives

This research proposes **Semantic Entropy Decomposition (SED)**, a novel framework for efficient uncertainty quantification that addresses three key objectives:

1. **Develop a computationally efficient uncertainty estimation mechanism** that achieves comparable accuracy to multi-sample methods while requiring only a single forward pass augmented with lightweight probing.

2. **Design a principled decomposition framework** that separates epistemic uncertainty from aleatoric uncertainty, enabling targeted interventions for hallucination mitigation.

3. **Validate the practical utility of SED** across multiple domains and LLM architectures, establishing benchmarks for uncertainty-aware deployment in high-stakes applications.

### Significance

The proposed research addresses a critical bottleneck in reliable AI deployment. By enabling real-time uncertainty quantification with explicit epistemic-aleatoric decomposition, SED will: (1) make uncertainty-aware LLM deployment practical in latency-sensitive applications; (2) provide actionable confidence signals that trigger appropriate interventions; and (3) advance theoretical understanding of how uncertainty manifests in transformer architectures. Success in this research could fundamentally transform how foundation models are deployed in healthcare, legal, and autonomous systems.

## 2. Methodology

### 2.1 Overview

The SED framework comprises three main components: (1) semantic entropy ground truth generation for training supervision, (2) auxiliary probe network training on intermediate representations, and (3) uncertainty decomposition through contrastive learning. We detail each component below.

### 2.2 Semantic Entropy Ground Truth Generation

We first establish ground truth uncertainty estimates using established multi-sample semantic entropy computation, which serves as training signal for our efficient probes.

For a given input query $x$, we generate $K$ responses $\{y_1, y_2, \ldots, y_K\}$ through temperature-scaled sampling. Responses are clustered into semantic equivalence classes $\mathcal{C} = \{C_1, C_2, \ldots, C_M\}$ using a semantic similarity model (e.g., NLI-based entailment classifier). The semantic entropy is computed as:

$$H_{sem}(x) = -\sum_{m=1}^{M} P(C_m | x) \log P(C_m | x)$$

where $P(C_m | x) = \sum_{y_i \in C_m} P(y_i | x)$ represents the probability mass assigned to semantic cluster $C_m$.

### 2.3 Probe Network Architecture

We design lightweight auxiliary probe networks that operate on intermediate layer representations of the LLM. Let $\mathbf{h}_l^{(t)} \in \mathbb{R}^d$ denote the hidden state at layer $l$ and token position $t$. We aggregate representations across the final $T'$ tokens of the input using attention pooling:

$$\mathbf{z}_l = \sum_{t=1}^{T'} \alpha_t \mathbf{h}_l^{(t)}, \quad \text{where} \quad \alpha_t = \frac{\exp(\mathbf{w}_a^\top \mathbf{h}_l^{(t)})}{\sum_{t'} \exp(\mathbf{w}_a^\top \mathbf{h}_l^{(t')})}$$

The probe network for layer $l$ consists of a two-layer MLP with residual connection:

$$\hat{u}_l = \sigma\left(\mathbf{W}_2 \cdot \text{ReLU}(\mathbf{W}_1 \mathbf{z}_l + \mathbf{b}_1) + \mathbf{b}_2\right)$$

where $\sigma$ is the sigmoid function and $\hat{u}_l \in [0, 1]$ represents the predicted uncertainty score from layer $l$.

The final uncertainty estimate aggregates predictions across multiple layers $\mathcal{L}$ using learned weights:

$$\hat{u}_{total} = \sum_{l \in \mathcal{L}} \beta_l \hat{u}_l, \quad \text{where} \quad \sum_{l \in \mathcal{L}} \beta_l = 1$$

### 2.4 Epistemic-Aleatoric Decomposition

The core innovation of SED lies in decomposing total uncertainty into epistemic and aleatoric components. We achieve this through contrastive training on carefully curated datasets with known uncertainty characteristics.

**Dataset Construction:**

We construct three dataset categories:
- **High Epistemic ($\mathcal{D}_E$)**: Factual questions about rare entities or recent events where the model lacks knowledge, verified through knowledge cutoff dates and entity frequency analysis.
- **High Aleatoric ($\mathcal{D}_A$)**: Inherently ambiguous queries (e.g., "What's the best programming language?") or questions with multiple valid answers.
- **Low Uncertainty ($\mathcal{D}_L$)**: Well-established factual questions with unambiguous answers that the model reliably handles.

**Contrastive Probe Training:**

We train separate probe heads for epistemic ($f_E$) and aleatoric ($f_A$) uncertainty using a multi-task objective:

$$\mathcal{L}_{total} = \mathcal{L}_{recon} + \lambda_1 \mathcal{L}_{contrast} + \lambda_2 \mathcal{L}_{consist}$$

The reconstruction loss ensures the decomposed components sum to approximate total semantic entropy:

$$\mathcal{L}_{recon} = \mathbb{E}_{x}\left[\left(H_{sem}(x) - (\hat{u}_E(x) + \hat{u}_A(x))\right)^2\right]$$

The contrastive loss encourages correct attribution:

$$\mathcal{L}_{contrast} = \mathbb{E}_{x \in \mathcal{D}_E}\left[\max(0, \hat{u}_A(x) - \hat{u}_E(x) + \gamma)\right] + \mathbb{E}_{x \in \mathcal{D}_A}\left[\max(0, \hat{u}_E(x) - \hat{u}_A(x) + \gamma)\right]$$

where $\gamma$ is a margin hyperparameter.

The consistency loss enforces that both uncertainty types are low for confident, correct predictions:

$$\mathcal{L}_{consist} = \mathbb{E}_{x \in \mathcal{D}_L}\left[\hat{u}_E(x)^2 + \hat{u}_A(x)^2\right]$$

### 2.5 Experimental Design

**Models and Datasets:**

We evaluate SED on three model families: LLaMA-2 (7B, 13B, 70B), Mistral (7B), and GPT-3.5/4 (via API with embedding access). Evaluation spans multiple benchmarks:

- **TriviaQA** and **Natural Questions**: Factual question answering
- **TruthfulQA**: Hallucination-prone queries
- **AmbigQA**: Inherently ambiguous questions
- **MedQA** and **LegalBench**: Domain-specific high-stakes evaluation
- **HaluEval**: Dedicated hallucination detection benchmark

**Evaluation Metrics:**

1. **Hallucination Detection Performance:**
   - AUROC and AUPRC for binary hallucination classification
   - Selective prediction accuracy at various coverage levels

2. **Uncertainty Calibration:**
   - Expected Calibration Error (ECE): $ECE = \sum_{b=1}^{B} \frac{|S_b|}{N} |acc(S_b) - conf(S_b)|$
   - Brier Score for probabilistic calibration

3. **Decomposition Quality:**
   - Mutual information between $\hat{u}_E$ and hallucination labels
   - Correlation of $\hat{u}_A$ with human-annotated ambiguity scores

4. **Computational Efficiency:**
   - Latency overhead per query (ms)
   - Throughput comparison with multi-sample baselines

**Baselines:**

We compare against: (1) Semantic Entropy (Kuhn et al., 2023) with 10 samples; (2) P(True) verbalized confidence; (3) Token-level entropy; (4) Amortized semantic embeddings (Grewal et al., 2024); (5) Graph signal processing diagnostics (Noël, 2025).

**Ablation Studies:**

We systematically ablate: (1) number of layers used for probing; (2) probe architecture complexity; (3) training dataset composition; (4) contrastive margin values; and (5) layer aggregation strategies.

### 2.6 Implementation Details

Probes are trained using AdamW optimizer with learning rate $10^{-4}$ and cosine annealing over 50 epochs. We use $K=10$ samples for ground truth semantic entropy computation during training. Layer selection for probing targets the upper third of transformer layers based on preliminary analysis showing these layers encode more task-relevant semantic information. The total probe parameter count is kept under 1% of the base model to ensure minimal overhead.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Performance Targets:**

1. **Computational Efficiency**: We anticipate achieving 10-50x speedup over sampling-based semantic entropy methods. Specifically, we target <50ms overhead per query on standard GPU hardware, compared to 500-2000ms for 10-sample semantic entropy computation.

2. **Hallucination Detection**: We expect AUROC improvements of 5-15% over single-pass baselines on TruthfulQA and HaluEval benchmarks, approaching within 2-3% of computationally expensive multi-sample methods.

3. **Uncertainty Decomposition**: The epistemic uncertainty component should achieve >0.7 correlation with actual hallucination occurrence, while aleatoric uncertainty correlates >0.6 with human-annotated query ambiguity.

4. **Calibration Quality**: We target ECE < 0.05, representing well-calibrated uncertainty estimates that accurately reflect model reliability.

**Deliverables:**

- Open-source implementation of SED compatible with HuggingFace Transformers
- Pre-trained probe weights for popular LLM architectures
- Curated training datasets with epistemic/aleatoric annotations
- Comprehensive benchmark suite for uncertainty decomposition evaluation

### Broader Impact

**Scientific Contributions:**

This research advances the theoretical understanding of how uncertainty manifests in transformer representations. By demonstrating that epistemic and aleatoric uncertainty have distinct signatures in intermediate layer activations, we provide new insights into the information processing of LLMs. The contrastive training framework establishes a principled methodology for disentangling uncertainty sources that could extend to other generative models.

**Practical Applications:**

SED enables practical deployment of uncertainty-aware LLMs in latency-sensitive, high-stakes domains:

- **Healthcare**: Real-time flagging of uncertain medical recommendations for physician review
- **Legal**: Highlighting potentially unreliable case citations in legal document generation
- **Autonomous Systems**: Triggering human oversight when planning under high epistemic uncertainty

**Societal Benefits:**

By making uncertainty quantification practical for deployed systems, this research contributes to more trustworthy AI. Users gain actionable signals about when to trust model outputs, reducing over-reliance on potentially unreliable generations. The explicit separation of epistemic uncertainty enables targeted retrieval augmentation, improving factual accuracy without sacrificing response latency.

### Limitations and Future Directions

We acknowledge several limitations that define future research directions: (1) probe transfer across model architectures requires retraining, though we will investigate zero-shot transfer through representation alignment; (2) the method assumes access to intermediate representations, limiting applicability to API-only models; (3) the training dataset construction requires careful curation to avoid distribution shift. Future work will explore adaptive probe networks that generalize across architectures and investigation of uncertainty decomposition in multimodal foundation models.

### Conclusion

This proposal presents Semantic Entropy Decomposition, a novel framework for efficient uncertainty quantification in LLMs that decomposes uncertainty into actionable epistemic and aleatoric components. By combining lightweight probing with contrastive training, SED bridges the gap between accurate multi-sample methods and practical real-time deployment requirements. Success in this research will enable a new generation of uncertainty-aware AI systems that know what they don't know—a crucial step toward reliable foundation model deployment in high-stakes applications.