# Research Proposal: StyleToM: Dual-Adapter Personalization for Code Generation via Style Learning and Theory-of-Mind Intent Inference

## 1. Introduction

### 1.1 Background

The rapid advancement of large language models (LLMs) has revolutionized code generation, with tools like GitHub Copilot, Amazon CodeWhisperer, and various open-source alternatives becoming integral to modern software development workflows. Despite their impressive capabilities, these code assistants suffer from a fundamental limitation: they generate generic suggestions that fail to account for individual developer preferences and contextual intent. Empirical studies report acceptance rates hovering around 40%, indicating that developers frequently reject or substantially modify generated code before integration into their projects.

This personalization gap stems from two orthogonal dimensions that current systems fail to address simultaneously. First, developers exhibit distinct **coding styles**—encompassing naming conventions, formatting preferences, design patterns, and code organization strategies—that reflect their experience, team standards, and personal aesthetics. Second, developers have dynamic **intents** that vary across tasks, influenced by project constraints, current goals, and implicit requirements that may not be fully articulated in their prompts. Recent research has begun addressing these dimensions independently: MPCoder (Dai et al., ACL 2024) demonstrated that explicit and implicit style patterns can be learned from developer history, while TOM-SWE (Zhou et al., 2025) showed that theory-of-mind modeling can dramatically improve intent inference, achieving 59.7% versus 18.1% on stateful SWE-bench tasks.

However, no existing approach integrates both style adaptation and intent inference into a unified personalization framework. This represents a significant missed opportunity, as style captures *how* developers prefer code written, while intent captures *what* they currently need—fundamentally orthogonal dimensions that should provide additive benefits when combined.

### 1.2 Research Objectives

This research proposes **StyleToM**, a dual-adapter architecture that unifies LoRA-based style representation learning with retrieval-augmented theory-of-mind intent inference for personalized code generation. Our primary objectives are:

1. **Design and implement** a dual-adapter architecture where a Style Adapter captures developer-specific coding patterns and a ToM Module infers contextual intent from interaction history.

2. **Validate the orthogonality hypothesis** that style and intent represent separable personalization dimensions providing additive benefits when combined.

3. **Demonstrate practical improvements** in developer satisfaction (>20% improvement) and code acceptance rate (from ~40% baseline to >55%) through comprehensive evaluation.

4. **Establish efficiency constraints** ensuring the dual-module architecture maintains practical deployment viability with <30% latency overhead.

### 1.3 Significance

This research addresses critical challenges in the DL4C community, particularly in **Developer Productivity and HCI for Code** and **Post-training and Alignment for Code**. By demonstrating that personalization requires addressing both style and intent dimensions, we provide a principled framework for building developer-adaptive code assistants. The practical implications extend to enterprise code assistants, IDE plugins, and any context where sustained developer-AI collaboration benefits from personalization. Furthermore, our ablation methodology establishes rigorous evaluation practices for personalization research, contributing to the **Benchmarking and Evaluation for Code** theme.

## 2. Methodology

### 2.1 System Architecture Overview

StyleToM comprises three primary components operating on a frozen base LLM (CodeLlama-34B): (1) a **Style Adapter** that learns developer-specific coding patterns, (2) a **ToM Intent Module** that infers current goals and constraints, and (3) an **Integration Layer** that combines both signals for personalized generation.

### 2.2 Style Adapter Design

The Style Adapter employs LoRA-based dual representation learning to capture both explicit and implicit style patterns from developer code history.

**Explicit Pattern Extraction:** We extract surface-level style features including:
- Naming conventions (camelCase, snake_case, prefixes/suffixes)
- Formatting patterns (indentation, line length, bracket placement)
- Comment density and documentation style
- Import organization and module structure

These features are encoded as a style vector $\mathbf{s}_{explicit} \in \mathbb{R}^{d_e}$ using rule-based extractors combined with learned embeddings.

**Implicit Pattern Learning:** For semantic patterns (design preferences, abstraction levels, error handling strategies), we employ contrastive learning. Given a developer's code corpus $\mathcal{C}_u = \{c_1, c_2, ..., c_n\}$ where $n \in [50, 100]$ files, we train the Style Adapter using:

$$\mathcal{L}_{style} = -\log \frac{\exp(\text{sim}(h_i, h_j^+) / \tau)}{\exp(\text{sim}(h_i, h_j^+) / \tau) + \sum_{k=1}^{K} \exp(\text{sim}(h_i, h_k^-) / \tau)}$$

where $h_i$ represents the hidden representation of code from developer $u$, $h_j^+$ is a positive sample from the same developer, $h_k^-$ are negative samples from other developers, $\text{sim}(\cdot, \cdot)$ denotes cosine similarity, and $\tau$ is a temperature parameter.

**LoRA Integration:** The Style Adapter modifies attention weights in the base LLM through low-rank decomposition:

$$W' = W + \Delta W = W + BA$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times d}$, and rank $r \in [8, 64]$ is a hyperparameter. The combined style representation is:

$$\mathbf{s}_u = \text{MLP}([\mathbf{s}_{explicit}; \mathbf{s}_{implicit}])$$

### 2.3 Theory-of-Mind Intent Module

The ToM Module maintains persistent memory of interaction history to infer developer intent through a lightweight partner agent architecture.

**Memory Structure:** We maintain a retrieval-augmented memory bank $\mathcal{M}_u$ for each developer containing:
- Recent interactions: $\{(q_t, r_t, f_t)\}_{t=1}^{T}$ where $q_t$ is the query, $r_t$ is the response, and $f_t$ is feedback
- Inferred preferences: Accumulated beliefs about developer goals and constraints
- Task context: Current project state and recent code changes

**Intent Inference:** Given a new instruction $x$ and memory $\mathcal{M}_u$, the ToM Module computes:

$$\mathbf{i}_u = \text{ToM}(x, \text{Retrieve}(\mathcal{M}_u, x, k))$$

where $\text{Retrieve}(\cdot)$ returns the $k$ most relevant memory entries using dense retrieval:

$$\text{Retrieve}(\mathcal{M}_u, x, k) = \text{TopK}_{m \in \mathcal{M}_u}(\text{sim}(\phi(x), \phi(m)))$$

The ToM inference follows a structured reasoning process:

$$\mathbf{i}_u = [\mathbf{g}_u; \mathbf{c}_u; \mathbf{p}_u]$$

where $\mathbf{g}_u$ represents inferred goals, $\mathbf{c}_u$ represents constraints, and $\mathbf{p}_u$ represents preferences derived from the interaction history.

### 2.4 Integration Layer

The Integration Layer combines style and intent signals through gated fusion:

$$\alpha = \sigma(W_g[\mathbf{s}_u; \mathbf{i}_u; \mathbf{h}_x])$$

$$\mathbf{z}_u = \alpha \odot \mathbf{s}_u + (1 - \alpha) \odot \mathbf{i}_u$$

where $\mathbf{h}_x$ is the instruction encoding, $\sigma$ is the sigmoid function, and $\odot$ denotes element-wise multiplication. The final generation conditions on:

$$P(y | x, u) = \text{LLM}(x, \mathbf{z}_u)$$

### 2.5 Training Procedure

**Stage 1: Style Adapter Pre-training**
- Dataset: Developer code histories from GitHub (minimum 50 files per developer, 500+ developers)
- Objective: Contrastive style learning + LoRA fine-tuning
- Duration: ~10 epochs until style classification accuracy >85%

**Stage 2: ToM Module Training**
- Dataset: Developer interaction logs with feedback signals
- Objective: Intent prediction accuracy on held-out interactions
- Duration: Until convergence on validation set

**Stage 3: Joint Fine-tuning**
- Dataset: Combined style + interaction data
- Objective: End-to-end optimization with acceptance rate as reward signal
- Duration: ~5 epochs with early stopping

### 2.6 Experimental Design

**Research Questions:**
- RQ1: Does StyleToM improve developer satisfaction compared to non-personalized baselines?
- RQ2: Do style and intent provide additive personalization benefits?
- RQ3: What is the latency overhead of the dual-adapter architecture?

**Baselines:**
1. **OpenHands (No Personalization):** State-of-the-art code agent without personalization
2. **Style-Only:** StyleToM with ToM Module disabled
3. **ToM-Only:** StyleToM with Style Adapter disabled
4. **MPCoder:** Prior work on style-based personalization
5. **TOM-SWE:** Prior work on intent-based personalization

**Evaluation Metrics:**

| Metric | Description | Target |
|--------|-------------|--------|
| Developer Satisfaction | Likert scale 1-5 from surveys | >20% improvement |
| Code Acceptance Rate | % suggestions accepted without major modification | >55% (baseline ~40%) |
| Style Similarity Score | Automated comparison to developer history | >0.75 |
| Intent Alignment Score | Human evaluation of goal satisfaction | >0.80 |
| Latency Overhead | Additional inference time vs. baseline | <30% |

**Automated Evaluation:**
- Dataset: SWE-bench Verified subset (500 tasks, medium difficulty)
- Style similarity computed using AST-based pattern matching and embedding similarity
- Acceptance rate simulated using edit distance thresholds

**User Study Design:**
- Participants: 30 professional developers (minimum 2 years experience)
- Design: Within-subjects, counterbalanced condition order
- Tasks: 10 realistic coding tasks per participant across conditions
- Measures: Post-task satisfaction surveys, acceptance decisions, qualitative feedback
- Statistical Analysis: Paired t-test for satisfaction (α = 0.05, one-tailed), chi-square for acceptance rate

**Ablation Study:**
To validate the orthogonality hypothesis, we conduct systematic ablation:

| Condition | Style Adapter | ToM Module | Expected Outcome |
|-----------|---------------|------------|------------------|
| Baseline | ✗ | ✗ | Reference performance |
| Style-Only | ✓ | ✗ | +Style contribution |
| ToM-Only | ✗ | ✓ | +Intent contribution |
| StyleToM | ✓ | ✓ | Additive benefits |

We test for interaction effects using two-way ANOVA:

$$Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \epsilon_{ijk}$$

where $\alpha_i$ represents Style Adapter effect, $\beta_j$ represents ToM Module effect, and $(\alpha\beta)_{ij}$ captures interaction.

### 2.7 Implementation Details

- Base Model: CodeLlama-34B (frozen weights)
- Style Adapter: LoRA rank 16, applied to attention layers
- ToM Memory: Maximum 100 interactions, dense retrieval with top-5
- Hardware: 4× A100 GPUs for training, single A100 for inference
- Framework: PyTorch + HuggingFace Transformers + PEFT

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes:**
1. **Developer Satisfaction Improvement:** We expect StyleToM to achieve >20% improvement in developer satisfaction scores compared to non-personalized baselines, with statistical significance (p < 0.05). Based on TOM-SWE's 86% usefulness rating and MPCoder's demonstrated style learning capability, we anticipate satisfaction scores of 4.0+ on a 5-point scale (baseline estimated at ~3.3).

2. **Code Acceptance Rate:** We project acceptance rates improving from the ~40% baseline to >55%, representing a substantial reduction in developer effort for code modification.

3. **Ablation Findings:** We hypothesize that the ablation study will reveal additive benefits, with StyleToM outperforming both Style-Only and ToM-Only conditions. Specifically:
   - Style-Only: +10-15% satisfaction improvement (style alignment)
   - ToM-Only: +15-20% satisfaction improvement (intent alignment)
   - StyleToM: +25-30% satisfaction improvement (combined effect)

4. **Efficiency:** Latency overhead maintained below 30% through efficient LoRA inference and optimized retrieval.

### 3.2 Scientific Contributions

1. **Novel Integration Framework:** First demonstration that style and intent represent orthogonal personalization dimensions with additive benefits for code generation.

2. **Dual-Adapter Architecture:** Practical architecture combining LoRA-based style learning with retrieval-augmented ToM inference, applicable beyond code generation.

3. **Evaluation Methodology:** Rigorous ablation design for personalization research, establishing best practices for the DL4C community.

4. **Empirical Insights:** Quantified understanding of how developers benefit from different personalization dimensions.

### 3.3 Practical Impact

1. **Developer Productivity:** Reduced time spent modifying generated code, enabling developers to focus on higher-level design decisions.

2. **Enterprise Adoption:** Framework for building personalized code assistants that adapt to organizational coding standards and individual preferences.

3. **Open Science:** We commit to releasing code, trained adapters, and evaluation datasets to support reproducibility and future research.

### 3.4 Limitations and Future Work

**Acknowledged Limitations:**
- Cold-start problem for new users with insufficient code history
- Per-language style adapters (no cross-language transfer)
- Style drift over time not addressed in current design

**Future Directions:**
- Few-shot style adaptation for cold-start mitigation
- Cross-language style transfer learning
- Continuous learning for evolving developer preferences
- Extension to multi-developer team settings

### 3.5 Broader Impact

This research contributes to the responsible development of AI coding assistants by prioritizing developer agency and personalization. By adapting to individual preferences rather than imposing generic solutions, StyleToM supports diverse coding practices and reduces the homogenization risk of AI-assisted development. Our commitment to open science ensures that the benefits of this research extend to the broader community.