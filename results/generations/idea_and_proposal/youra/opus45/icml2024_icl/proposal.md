# Research Proposal: Developmental Transition of In-Context Learning Mechanisms: From Induction Heads to Function Vector Heads Across Model Scale

## 1. Introduction

### 1.1 Background

In-context learning (ICL) represents one of the most remarkable emergent capabilities of large language models (LLMs), enabling these systems to acquire new skills directly from input examples without explicit parameter updates. First systematically documented in GPT-3, ICL allows models to perform novel tasks—from translation to arithmetic—simply by conditioning on a few demonstrations within the prompt. This capability has profound implications for AI deployment, enabling rapid adaptation to new domains without costly fine-tuning procedures.

Despite the practical significance of ICL, the underlying mechanisms remain poorly understood. Two prominent lines of research have proposed competing explanations for how transformers implement ICL. Olsson et al. (2022) identified **induction heads**—attention head circuits that perform pattern matching by copying tokens that follow similar preceding contexts—as "the mechanism for the majority of all in-context learning." Their analysis demonstrated that induction heads emerge during a specific training phase that coincides with sharp improvements in ICL performance. Conversely, recent work by Yin & Steinhardt (2025) discovered **function vector (FV) heads**, which encode abstract task representations that can be extracted and transferred between contexts. Critically, they found that FV heads are "primarily responsible" for ICL in larger models, with many FV heads appearing to develop from induction head scaffolds during training.

This apparent contradiction—induction heads versus function vector heads as the primary ICL mechanism—presents a fundamental puzzle. We propose that this tension reflects not conflicting findings but rather a **scale-dependent developmental transition** that has not been systematically characterized. Just as biological neural systems exhibit developmental staging where simpler mechanisms scaffold more complex ones, transformer ICL mechanisms may undergo analogous transitions as model capacity increases.

### 1.2 Research Objectives

This research aims to:

1. **Characterize the mechanism transition**: Systematically quantify the relative contributions of induction heads and function vector heads to ICL performance across model scales from 100M to 7B parameters.

2. **Identify the crossover point**: Determine the critical model scale at which function vector heads become the dominant ICL mechanism, superseding induction heads.

3. **Validate the developmental scaffold hypothesis**: Test whether function vector heads emerge from induction head precursors during training, establishing a causal developmental pathway.

4. **Examine task-dependent modulation**: Investigate how task complexity influences the transition dynamics between mechanisms.

### 1.3 Significance

This research addresses a core theoretical question in ICL: how do transformers implement in-context learning, and how does this implementation change with scale? Resolving the apparent contradiction between induction head and function vector head theories would unify competing mechanistic accounts and provide a coherent developmental framework for understanding ICL emergence.

Beyond theoretical contributions, this work has practical implications for architecture design. If the transition from induction heads to function vector heads follows predictable patterns, practitioners could design more efficient architectures that accelerate FV head development or optimize the induction-to-FV transition. Understanding the crossover point could inform decisions about model scaling for specific ICL applications, potentially enabling smaller models to achieve ICL capabilities currently requiring larger systems.

## 2. Methodology

### 2.1 Experimental Framework Overview

Our methodology employs systematic ablation studies across multiple model scales, using mechanistic interpretability tools to isolate and quantify the contributions of specific attention head types to ICL performance. The experimental design follows a factorial structure examining model scale, mechanism type, and task complexity.

### 2.2 Model Selection and Preparation

**Model Family**: We utilize the Pythia model suite (Biderman et al., 2023), which provides checkpoints at multiple scales trained on identical data (The Pile), enabling controlled comparisons across scale without confounding from training data differences.

**Model Scales**: Five scales will be examined:
- Pythia-160M (proxy for 100M scale)
- Pythia-410M (proxy for 500M scale)  
- Pythia-1B
- Pythia-2.8B (proxy for 3B scale)
- Pythia-6.9B (proxy for 7B scale)

**Controlled Variables**: All models share identical tokenization, training data, and architectural design (differing only in depth and width), isolating scale as the primary independent variable.

### 2.3 Mechanism Identification

**Induction Head Detection**: Following Olsson et al. (2022), we identify induction heads using the prefix matching score:

$$\text{IH-Score}(h) = \mathbb{E}_{x \sim \mathcal{D}} \left[ \sum_{t} A^{(h)}_{t, t-k} \cdot \mathbb{1}[x_t = x_{t-k+1}] \right]$$

where $A^{(h)}_{t,i}$ denotes the attention weight from position $t$ to position $i$ in head $h$, and $k$ is the offset for repeated patterns. Heads with IH-Score > 0.4 are classified as induction heads.

**Function Vector Head Detection**: Following Yin & Steinhardt (2025), we identify FV heads by measuring task-encoding capacity:

$$\text{FV-Score}(h) = \text{Acc}(\text{ICL with } \mathbf{v}^{(h)}_{\text{task}}) - \text{Acc}(\text{ICL with } \mathbf{v}^{(h)}_{\text{random}})$$

where $\mathbf{v}^{(h)}_{\text{task}}$ is the function vector extracted from head $h$ on task demonstrations, computed as:

$$\mathbf{v}^{(h)}_{\text{task}} = \frac{1}{N} \sum_{i=1}^{N} \text{Output}^{(h)}(x_i^{\text{demo}})$$

Heads with FV-Score > 0.15 (accuracy improvement) are classified as FV heads.

### 2.4 Ablation Protocol

**TransformerLens Implementation**: We use the TransformerLens library (Nanda et al., 2022) for surgical interventions on attention heads. For each identified mechanism head, we perform mean ablation:

$$\tilde{A}^{(h)} = \mathbb{E}_{x \sim \mathcal{D}_{\text{ref}}}[A^{(h)}(x)]$$

replacing the head's output with its average activation over a reference distribution.

**Contribution Measurement**: The contribution of mechanism type $M$ (induction or FV) is quantified as:

$$\text{Contrib}(M) = \frac{\text{Acc}_{\text{baseline}} - \text{Acc}_{\text{ablate-}M}}{\text{Acc}_{\text{baseline}}} \times 100\%$$

**Mechanism Ratio**: The primary dependent variable is the FV/IH contribution ratio:

$$R_{\text{FV/IH}} = \frac{\text{Contrib}(\text{FV})}{\text{Contrib}(\text{IH})}$$

### 2.5 ICL Benchmark Tasks

We employ a standardized benchmark suite adapted from Garg et al. (2022):

1. **Linear Regression**: $y = \mathbf{w}^T \mathbf{x} + \epsilon$, where $\mathbf{w} \sim \mathcal{N}(0, I_d)$, $d \in \{5, 10, 20\}$

2. **Sparse Linear Regression**: Same as above with $k$-sparse weights, $k \in \{2, 5\}$

3. **Two-Layer Neural Network**: $y = \text{ReLU}(\mathbf{W}_2 \cdot \text{ReLU}(\mathbf{W}_1 \mathbf{x}))$

4. **Classification Tasks**: Binary and multi-class classification with varying decision boundaries

**Task Complexity Levels**: Tasks are categorized into three complexity tiers based on the minimum model capacity required for above-chance ICL performance, enabling analysis of task-dependent transition dynamics.

### 2.6 Experimental Design

**Factorial Structure**:
- 5 model scales × 3 task complexity levels × 2 mechanism types × 3 random seeds = 90 experimental conditions

**Per-Condition Protocol**:
1. Generate 1,000 ICL episodes per task (varying in-context examples)
2. Identify induction and FV heads using detection criteria
3. Measure baseline ICL accuracy
4. Perform mechanism-specific ablations
5. Compute contribution scores and ratios

**Training Dynamics Analysis** (for developmental scaffold hypothesis):
- Analyze intermediate Pythia checkpoints (every 1B tokens)
- Track head classification transitions (IH → FV)
- Measure attention pattern similarity between early IH and mature FV heads

### 2.7 Statistical Analysis

**Primary Analysis (P1 - Mechanism Transition)**:

Spearman rank correlation between model scale and $R_{\text{FV/IH}}$:

$$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2-1)}$$

**Hypothesis**: $\rho > 0.8$ with $p < 0.05$
**Falsification**: $\rho < 0.5$ or $p > 0.10$

**Crossover Point Estimation (P2)**:

Fit a logistic transition model:

$$P(\text{FV dominant}) = \frac{1}{1 + e^{-\beta(\log S - \log S_c)}}$$

where $S$ is model scale and $S_c$ is the crossover point. Estimate $S_c$ via maximum likelihood with 95% confidence intervals.

**Task Modulation Analysis (P3)**:

ANOVA examining interaction between task complexity and scale on $R_{\text{FV/IH}}$:

$$R_{\text{FV/IH}} = \mu + \alpha_{\text{scale}} + \beta_{\text{complexity}} + (\alpha\beta)_{\text{interaction}} + \epsilon$$

**Developmental Trajectory Analysis (P4)**:

Compute attention pattern similarity between checkpoint $t$ and final checkpoint:

$$\text{Sim}(h, t) = \cos(\text{vec}(A^{(h)}_t), \text{vec}(A^{(h)}_{\text{final}}))$$

Track transition timing for heads that begin as IH-classified and end as FV-classified.

### 2.8 Evaluation Metrics

| Metric | Description | Success Criterion |
|--------|-------------|-------------------|
| $\rho_{\text{scale-ratio}}$ | Correlation between scale and FV/IH ratio | $\rho > 0.8$, $p < 0.05$ |
| $S_c$ | Crossover point estimate | Within 500M-3B range |
| Transition Rate | Proportion of IH→FV head transitions | > 30% of FV heads |
| Task Modulation | Interaction effect size | $\eta^2 > 0.06$ |

### 2.9 Computational Resources

**Estimated Requirements**:
- GPU hours: ~500 A100 hours (inference and ablation studies)
- Storage: ~2TB for checkpoints and results
- Estimated cost: ~$5,000 (cloud compute)

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1)**: We expect to observe a strong monotonic relationship between model scale and the FV/IH contribution ratio ($\rho > 0.8$). Specifically:
- At 160M parameters: IH contribution > FV contribution (ratio < 1.0)
- At 6.9B parameters: FV contribution > IH contribution (ratio > 1.0)

**Crossover Point (P2)**: Based on preliminary evidence from Yin & Steinhardt (2025), we predict the crossover occurs between 500M and 3B parameters, likely near 1B parameters where models first exhibit robust abstract reasoning capabilities.

**Task Modulation (P3)**: More complex tasks (e.g., two-layer NN regression) should shift the crossover point to larger scales, as abstract task encoding requires greater capacity for complex function classes.

**Developmental Scaffold (P4)**: We expect >30% of mature FV heads to show induction-like attention patterns in early training checkpoints, supporting the scaffold hypothesis.

### 3.2 Theoretical Impact

This research would provide the first unified mechanistic account of ICL across model scales, resolving the apparent contradiction between induction head and function vector head theories. The developmental staging framework—where simpler mechanisms scaffold more complex ones—offers a principled explanation for why different studies emphasize different mechanisms: they examined models at different points along the developmental trajectory.

This framework connects transformer learning dynamics to broader principles in developmental systems, potentially enabling cross-pollination of ideas between AI and cognitive science. The identification of specific transition points and mechanisms could inform theories of emergent capabilities more broadly.

### 3.3 Practical Impact

**Architecture Design**: Understanding the IH→FV transition could guide architectural innovations that accelerate FV head development. For instance, if specific layer configurations facilitate the transition, practitioners could incorporate these patterns into smaller models.

**Efficient Scaling**: The crossover point identification provides actionable guidance for model selection. Applications requiring abstract ICL capabilities should target models above the crossover threshold, while simpler pattern-matching tasks may be adequately served by smaller models.

**Training Optimization**: If the developmental scaffold hypothesis is confirmed, training curricula could be designed to first establish robust induction heads before introducing tasks requiring abstract function encoding, potentially improving training efficiency.

### 3.4 Limitations and Future Directions

**Limitations**:
- Results may be specific to the Pythia architecture and training data
- Ablation studies provide correlational rather than strictly causal evidence
- The 7B upper bound may miss transitions occurring at larger scales

**Future Directions**:
- Extension to encoder-decoder and encoder-only architectures
- Investigation of the transition in multimodal models
- Development of interventions to accelerate or modify the transition
- Theoretical analysis connecting capacity bounds to mechanism transitions

### 3.5 Conclusion

This research proposes a systematic investigation of how in-context learning mechanisms evolve across model scale, testing the hypothesis that transformers undergo a developmental transition from induction heads to function vector heads. By combining rigorous ablation methodology with comprehensive scale analysis, we aim to unify competing mechanistic theories and provide actionable insights for the design of efficient, ICL-capable architectures. The expected outcomes would advance both theoretical understanding of emergent capabilities and practical approaches to model development.