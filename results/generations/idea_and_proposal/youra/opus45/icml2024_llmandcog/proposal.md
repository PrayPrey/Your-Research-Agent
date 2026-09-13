# Research Proposal: Validating LLM Reasoning via Predictive Coding-Inspired Residual Stream Analysis

## 1. Title

**V-PC-RAS: A Mechanistic Framework for Distinguishing Genuine Reasoning from Heuristic Shortcuts in Large Language Models through Predictive Coding-Inspired Residual Stream Analysis**

---

## 2. Introduction

### 2.1 Background

Large Language Models (LLMs) have demonstrated remarkable performance across diverse cognitive tasks, including Theory of Mind (ToM) reasoning, logical inference, and complex problem-solving. These capabilities have sparked intense debate about whether LLMs exhibit genuine reasoning or merely sophisticated pattern matching. This distinction carries profound implications: if LLMs rely on superficial heuristics rather than compositional reasoning, their deployment in high-stakes domains—medical diagnosis, legal reasoning, scientific discovery—poses significant risks.

The "Clever Hans" problem, named after the horse that appeared to perform arithmetic but actually responded to subtle cues from its handler, aptly characterizes this challenge. Recent work by Shapira et al. (2023) demonstrated that LLMs achieving high accuracy on standard Theory of Mind benchmarks often fail dramatically on adversarial variants designed to disrupt surface-level patterns. This behavioral evidence suggests heuristic reliance but cannot reveal the underlying computational mechanisms. Current evaluation paradigms measure *what* models produce but not *how* they produce it.

Mechanistic interpretability offers a promising avenue for addressing this gap. Techniques such as activation patching, circuit discovery, and sparse autoencoder analysis have begun illuminating the internal computations of transformers. However, these methods typically focus on identifying *which* components contribute to behavior rather than characterizing the *nature* of the computational process—specifically, whether it reflects genuine compositional reasoning.

Predictive coding theory from cognitive neuroscience provides a principled theoretical framework for this characterization. Under predictive coding, the brain operates as a hierarchical generative model that continuously generates predictions and propagates prediction errors upward through the cortical hierarchy. Genuine understanding manifests as hierarchical error decay: high prediction errors at lower levels (processing novel sensory input), progressively reduced errors at higher levels (as abstract representations successfully predict lower-level patterns), and minimal errors at the highest levels (confident inference). This framework has been extensively validated in neuroscience and offers a normative account of how hierarchical systems should process information during genuine comprehension versus superficial pattern matching.

### 2.2 Research Objectives

This research proposes to bridge predictive coding theory with transformer mechanistic interpretability to develop **V-PC-RAS (Validated Predictive Coding Residual Analysis Score)**, a mechanistic diagnostic tool for distinguishing genuine reasoning from heuristic shortcuts in LLMs. Our specific objectives are:

1. **Validate the theoretical bridge**: Establish that residual stream activation changes across transformer layers carry information analogous to prediction errors, using correlation with Multi-Layer Sparse Autoencoder (MLSAE) latent variance as an empirical proxy validation.

2. **Develop and compute V-PC-RAS**: Create a complexity-normalized metric quantifying hierarchical decay patterns in layer-wise residual deltas, distinguishing exponential decay (genuine reasoning) from flat patterns (heuristic shortcuts).

3. **Demonstrate behavioral relevance**: Show that V-PC-RAS predicts adversarial Theory of Mind benchmark performance while discriminating between correct and incorrect responses on challenging cognitive tasks.

4. **Characterize scale effects**: Investigate how hierarchical reasoning signatures emerge across model scales in the Pythia family (70M to 2.8B parameters).

### 2.3 Significance

This research addresses a critical gap at the intersection of AI safety, cognitive science, and mechanistic interpretability. The theoretical contribution lies in the first systematic integration of predictive coding principles with transformer analysis, providing a principled framework for characterizing computational processes rather than merely identifying contributing components. The methodological contribution introduces a validated, reproducible metric for cognitive auditing that can be applied before deployment. The practical contribution enables stakeholders to assess whether LLM reasoning is robust and generalizable or brittle and heuristic-dependent—a distinction essential for responsible AI deployment.

By grounding our approach in established cognitive neuroscience theory, we also contribute to the workshop's goal of understanding LLMs' position in the landscape of intelligent systems. If transformers exhibit predictive coding-like signatures during genuine reasoning, this suggests deeper computational parallels with biological cognition than previously recognized.

---

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Predictive Coding in Hierarchical Systems

Predictive coding posits that hierarchical generative systems minimize prediction errors across levels. For a system with $L$ layers, each layer $l$ generates predictions $\hat{x}_l$ of the layer below and computes prediction errors:

$$\epsilon_l = x_l - \hat{x}_l$$

In systems exhibiting genuine understanding, prediction errors decay hierarchically: high at lower levels (novel input), progressively reduced at intermediate levels (successful abstraction), and minimal at higher levels (confident inference). Formally, for genuine reasoning:

$$\|\epsilon_l\| > \|\epsilon_{l+1}\| > \cdots > \|\epsilon_L\|$$

following approximately exponential decay.

#### 3.1.2 Residual Stream as Prediction Error Proxy

In transformers, the residual stream carries the cumulative representation across layers. We define the layer-wise residual delta as:

$$\delta_l = h_l - h_{l-1}$$

where $h_l$ is the residual stream activation at layer $l$. We hypothesize that $\|\delta_l\|_2$ approximates prediction error magnitude: large deltas indicate substantial representational updates (high "surprise"), while small deltas indicate the representation is already well-formed (low "surprise").

**Critical Assumption**: This analogy is structural, not mechanistic—transformers are trained via backpropagation, not predictive coding. We therefore require empirical validation that residual deltas carry prediction-error-like information.

### 3.2 Research Design Overview

Our methodology comprises four phases:

| Phase | Objective | Success Criterion |
|-------|-----------|-------------------|
| **Phase 0** | Proxy Validation | MLSAE correlation $r > 0.5$ |
| **Phase 1** | V-PC-RAS Computation | Metric successfully computed |
| **Phase 2** | Behavioral Correlation | Adversarial accuracy correlation $r > 0.4$; discrimination $d > 0.5$ |
| **Phase 3** | Scale Analysis | Significant scale effects on PC-RAS |

### 3.3 Phase 0: Proxy Validation via MLSAE Correlation

#### 3.3.1 Rationale

Multi-Layer Sparse Autoencoders (MLSAEs) decompose residual stream activations into interpretable latent features. Lawson et al. (2024) demonstrated that individual MLSAE latents activate at specific layers, reflecting layer-specific computations. If residual deltas approximate prediction errors, they should correlate with the variance of MLSAE latent activations—both capturing the "informativeness" of layer-wise processing.

#### 3.3.2 Procedure

1. **Extract activations**: For each input $x$ and Pythia model, extract residual stream activations $h_l$ at all layers using TransformerLens.

2. **Compute residual deltas**: Calculate $\delta_l = h_l - h_{l-1}$ and $\|\delta_l\|_2$ for each layer.

3. **Compute MLSAE latent variance**: Pass $h_l$ through pre-trained MLSAE encoder to obtain latent activations $z_l$. Compute variance $\text{Var}(z_l)$ across latent dimensions.

4. **Correlation analysis**: For each model and input, compute Pearson correlation between the layer-wise sequences $\{\|\delta_l\|_2\}_{l=1}^L$ and $\{\text{Var}(z_l)\}_{l=1}^L$.

5. **Aggregate**: Report mean correlation across inputs with 95% confidence intervals.

#### 3.3.3 Success Criterion

Mean correlation $r > 0.5$ across all Pythia checkpoints. If $r < 0.3$, the core proxy assumption is invalidated, and the research pivots to alternative metrics.

### 3.4 Phase 1: V-PC-RAS Metric Computation

#### 3.4.1 PC-RAS: Hierarchical Decay Score

For each input, we fit two models to the layer-wise residual delta sequence $\{\|\delta_l\|_2\}_{l=1}^L$:

**Exponential decay model**:
$$\|\delta_l\|_2 \approx a \cdot e^{-\lambda l} + c$$

**Linear model**:
$$\|\delta_l\|_2 \approx \alpha l + \beta$$

We compute $R^2$ for each fit and define:

$$\text{PC-RAS} = R^2_{\text{exp}} - R^2_{\text{linear}}$$

Positive PC-RAS indicates hierarchical decay (exponential fits better); near-zero or negative PC-RAS indicates flat or non-hierarchical patterns.

#### 3.4.2 Complexity Normalization

To account for input complexity effects, we normalize:

$$\text{CN-PC-RAS} = \frac{\text{PC-RAS}}{\log(N_{\text{tokens}})}$$

where $N_{\text{tokens}}$ is the input token count. We also test perplexity-based normalization as a robustness check.

#### 3.4.3 Implementation Details

- **Models**: Pythia-70M, Pythia-410M, Pythia-1.4B, Pythia-2.8B
- **Activation extraction**: TransformerLens library
- **Token position**: Primary analysis on final token (answer prediction); secondary analysis on full sequence
- **Inference settings**: temperature=0, top_p=1.0 for deterministic generation

### 3.5 Phase 2: Behavioral Correlation and Discrimination

#### 3.5.1 Benchmarks

**ToMBench** (ACL 2024): Systematic Theory of Mind benchmark with ~2,860 items across multiple ToM dimensions (false belief, intention understanding, emotion recognition).

**HI-TOM** (He et al., 2023): Adversarial ToM benchmark with ~1,000 items designed to disrupt surface-level heuristics through higher-order belief reasoning and counterfactual scenarios.

We partition each benchmark into:
- **Standard split**: Items solvable via common patterns
- **Adversarial split**: Items requiring genuine compositional reasoning

#### 3.5.2 Correlation Analysis

**Prediction P2**: CN-PC-RAS correlates more strongly with adversarial accuracy than standard accuracy.

For each model, we compute:
- $r_{\text{adv}}$: Correlation between CN-PC-RAS and adversarial split accuracy
- $r_{\text{std}}$: Correlation between CN-PC-RAS and standard split accuracy

We test:
- $H_1$: $r_{\text{adv}} > 0.4$
- $H_2$: $r_{\text{adv}} > r_{\text{std}}$

Statistical test: Fisher z-transformation for comparing correlations; partial correlation controlling for input length.

#### 3.5.3 Discrimination Analysis

**Prediction P4**: Within each model, adversarial-correct responses show higher PC-RAS than adversarial-incorrect responses.

For each model on adversarial items:
- Group A: Items answered correctly
- Group B: Items answered incorrectly

We compute:
$$d = \frac{\mu_A - \mu_B}{\sigma_{\text{pooled}}}$$

Success criterion: Cohen's $d > 0.5$ (medium effect size).

Statistical test: Independent t-test with Welch's correction for unequal variances.

### 3.6 Phase 3: Scale Analysis

**Prediction P3**: Larger models exhibit stronger hierarchical decay on adversarial ToM tasks.

We fit a mixed-effects model:

$$\text{PC-RAS}_{ij} = \beta_0 + \beta_1 \cdot \log(\text{params}_i) + \beta_2 \cdot \text{task\_type}_j + \beta_3 \cdot \log(\text{params}_i) \times \text{task\_type}_j + u_j + \epsilon_{ij}$$

where $i$ indexes models, $j$ indexes benchmark items, $u_j$ is a random intercept for items, and task_type is binary (standard/adversarial).

We test whether $\beta_3 > 0$: larger models show disproportionately higher PC-RAS on adversarial tasks, suggesting emergent reasoning circuits.

### 3.7 Statistical Considerations

#### 3.7.1 Power Analysis

For correlation $r = 0.4$ with $\alpha = 0.05$ and power $= 0.80$, minimum sample size is $n = 46$. With 1,000+ benchmark items per split, we are adequately powered.

For discrimination with $d = 0.5$, assuming 50% accuracy on adversarial items, we need ~64 items per group. With 500+ adversarial items, we are adequately powered.

#### 3.7.2 Multiple Comparison Correction

We apply Bonferroni correction for four primary predictions: adjusted $\alpha = 0.0125$.

#### 3.7.3 Falsification Criteria

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| MLSAE correlation $r < 0.3$ | Phase 0 | **Abandon**: Core proxy assumption invalid |
| CN-PC-RAS vs adversarial accuracy $r < 0.2$ | Phase 2 | **Major revision**: Metric doesn't capture reasoning |
| Task discrimination $d < 0.3$ | Phase 2 | **Major revision**: PC-RAS not discriminative |
| No scale effect ($\beta_3$ not significant) | Phase 3 | **Minor revision**: Reasoning circuits not emergent with scale |

### 3.8 Data Collection and Resources

**Models**: Pythia family from EleutherAI (publicly available on HuggingFace)

**Benchmarks**: ToMBench and HI-TOM (publicly available)

**Tools**: 
- TransformerLens for activation extraction
- Pre-trained MLSAE from Lawson et al. (2024); Pythia-specific training if needed
- Standard scientific Python stack (NumPy, SciPy, statsmodels)

**Compute**: Estimated 100 GPU-hours on A100 for full experimental pipeline

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Validated Theoretical Bridge**
We expect to demonstrate that residual stream deltas correlate significantly ($r > 0.5$) with MLSAE latent variance, establishing empirical support for the predictive coding analogy in transformers. This validates the theoretical foundation for interpreting layer-wise activation changes as prediction-error-like signals.

**Primary Outcome 2: Discriminative Mechanistic Metric**
We anticipate that V-PC-RAS will successfully discriminate genuine reasoning from heuristic shortcuts, with adversarial-correct responses showing significantly higher hierarchical decay than adversarial-incorrect responses ($d > 0.5$). This provides a mechanistic signature that complements behavioral evaluation.

**Primary Outcome 3: Predictive Validity**
We expect CN-PC-RAS to predict adversarial ToM accuracy ($r > 0.4$) more strongly than standard accuracy, demonstrating that the metric captures reasoning robustness rather than mere task performance.

**Primary Outcome 4: Scale-Dependent Emergence**
We anticipate observing stronger hierarchical decay signatures in larger Pythia models specifically on adversarial tasks, suggesting that compositional reasoning circuits emerge with scale—providing mechanistic grounding for observed emergent abilities.

### 4.2 Theoretical Impact

This research establishes the first systematic connection between predictive coding theory and transformer mechanistic interpretability. If successful, it demonstrates that:

1. **Computational parallels exist**: Transformers, despite different training mechanisms, may implement computations structurally analogous to predictive coding during genuine reasoning.

2. **Cognitive theory informs AI analysis**: Principles from cognitive neuroscience can guide the development of interpretability metrics, suggesting a productive interdisciplinary research program.

3. **Hierarchical processing matters**: The layer-wise organization of transformers is not merely architectural convenience but reflects meaningful computational structure distinguishing reasoning modes.

### 4.3 Methodological Impact

V-PC-RAS introduces a new paradigm for cognitive auditing of LLMs:

1. **Pre-deployment validation**: Unlike behavioral benchmarks that can be gamed or memorized, mechanistic signatures are harder to superficially satisfy, enabling more robust capability assessment.

2. **Interpretable diagnostics**: The metric provides insight into *why* a model might fail—flat hierarchical patterns suggest heuristic reliance, guiding targeted improvements.

3. **Reproducible framework**: All components use publicly available tools and models, enabling community adoption and extension.

### 4.4 Practical Impact

For AI safety and deployment:

1. **High-stakes applications**: V-PC-RAS can serve as a gating criterion before deploying LLMs in medical, legal, or scientific domains where robust reasoning is essential.

2. **Model selection**: Practitioners can compare models not just on accuracy but on reasoning quality, selecting models with genuine compositional capabilities.

3. **Training guidance**: Low V-PC-RAS scores on target tasks can inform training interventions, such as curriculum design emphasizing compositional generalization.

### 4.5 Limitations and Future Directions

**Limitations**:
- Results are specific to Pythia architecture; generalization to other architectures requires validation
- Theory of Mind is one cognitive domain; extension to planning, causal reasoning, and mathematical reasoning is needed
- The predictive coding analogy is structural, not mechanistic; causal validation via activation patching would strengthen claims

**Future Directions**:
- Extend V-PC-RAS to multimodal models and multi-agent settings
- Develop real-time monitoring tools for production systems
- Investigate whether training with predictive coding objectives enhances reasoning signatures
- Apply framework to other cognitive benchmarks (planning, causal reasoning)

### 4.6 Conclusion

This research proposes a principled, theoretically-grounded approach to one of the most pressing questions in AI: do LLMs genuinely reason or merely pattern match? By bridging predictive coding theory with mechanistic interpretability, V-PC-RAS offers a validated diagnostic tool for distinguishing robust reasoning from brittle heuristics. Success would advance our understanding of LLM cognition, provide practical tools for responsible deployment, and establish a productive interdisciplinary research program connecting AI, cognitive science, and neuroscience.

---

**Word Count**: ~2,150 words