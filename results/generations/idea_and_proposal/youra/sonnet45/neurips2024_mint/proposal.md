# Research Proposal: SAE-Guided Activation Steering for Interpretable and Capability-Preserving Control of Foundation Models

## 1. Title

**SAE-Guided Activation Steering: Interpretable and Capability-Preserving Control of Foundation Models Through Mechanistic Feature Discovery**

## 2. Introduction

### 2.1 Background

Foundation models have demonstrated remarkable capabilities across diverse domains, yet their increasing power raises critical concerns about generating harmful content, perpetuating biases, and producing factually incorrect outputs. The challenge of controlling these models while preserving their general capabilities has become a central problem in AI safety research. Current intervention approaches face a fundamental trade-off: methods that achieve effective control often lack interpretability, making it difficult to debug failures or understand unintended side effects, while interpretable approaches may not guarantee preservation of the model's broader capabilities.

Recent work has explored various intervention strategies. SafeSteer (Ghosh et al., 2025) demonstrates fine-grained safety control through category-specific steering vectors computed via contrastive examples, achieving 87% toxicity reduction while maintaining 96% text quality. However, this heuristic approach operates in a black-box manner, providing no mechanistic understanding of why interventions succeed or fail. Conversely, Dubey (2025) employs linear probes to identify bias-relevant activation dimensions, offering some interpretability but achieving only 97% capability preservation on MMLU benchmarks and focusing solely on bias mitigation.

Mechanistic interpretability (MI) has emerged as a promising paradigm for understanding foundation model internals. Campbell et al. (2023) successfully localized lying behavior to specific attention heads in LLaMA models using activation patching, demonstrating that causal analysis can identify functionally relevant model components. Sparse autoencoders (SAEs) have shown particular promise for discovering monosemantic features—individual dimensions corresponding to single interpretable concepts. Abdulaal et al. (2024) demonstrated that SAE features in vision transformers align with radiologist-interpretable concepts, while Villegas Garcia and Ansuini (2025) showed that manipulating SAE features in protein language models enables targeted generation of specific protein domains.

Despite these advances, no existing framework systematically integrates mechanistic interpretability into intervention design with validated multi-objective control. This creates deployment risks: interventions may cause unintended capability degradation, fail unpredictably across different control objectives, or exhibit opaque failure modes that resist debugging.

### 2.2 Research Objectives

This research proposes a novel three-phase framework that uses sparse autoencoder features as the foundation for designing activation steering interventions. Our primary objectives are:

**Objective 1: Develop an interpretability-first intervention framework** that discovers monosemantic, causally-relevant features through SAE training and activation patching validation, enabling systematic intervention design in interpretable feature space rather than raw activation space.

**Objective 2: Demonstrate multi-objective control** across safety (toxicity reduction), factuality (hallucination mitigation), and style (sentiment control) domains, validating that the framework generalizes beyond single-task applications.

**Objective 3: Establish superior capability preservation** by monitoring SAE feature activations during generation to detect unintended effects early, enabling iterative refinement before catastrophic capability degradation occurs.

**Objective 4: Quantify interpretability gains** through expert evaluation, establishing whether SAE-guided steering provides practical debugging advantages over heuristic and probe-only baselines.

### 2.3 Research Hypothesis

**Main Hypothesis (H-01):** If we use sparse autoencoder (SAE) features to guide the design and validation of activation steering interventions (rather than using heuristic or probe-only approaches), then we can achieve more interpretable, targeted, and capability-preserving control over foundation model behavior across multiple objectives (safety, factuality, style), because SAE features provide monosemantic, causally-relevant control dimensions that enable systematic intervention design and feature-space validation of intervention effects.

**Alternative Hypothesis (H0):** Heuristic activation steering methods (SafeSteer-style category contrasts) or probe-only approaches achieve equivalent control effectiveness, interpretability, and capability preservation compared to SAE-guided steering, rendering the additional computational cost of SAE training and feature-space validation unjustified.

### 2.4 Significance

This research addresses critical gaps at the intersection of mechanistic interpretability and AI safety:

**Scientific Significance:** The framework establishes SAE feature space as a principled substrate for intervention design, moving beyond heuristic approaches. By integrating activation patching into intervention validation, we formalize the interpretability→intervention→validation cycle missing in prior work, contributing to theoretical understanding of how mechanistic insights translate to practical control.

**Practical Significance:** Production deployment of foundation models requires interventions that are simultaneously effective, capability-preserving, and debuggable. Our framework's feature-space monitoring enables transparent diagnosis of steering failures (e.g., "Feature 42 insufficiently suppressed") versus black-box failure modes, reducing deployment risks. The multi-objective validation protocol addresses real-world scenarios where models must satisfy multiple constraints simultaneously (e.g., safe AND factually accurate).

**Methodological Significance:** We introduce the first comprehensive benchmark suite for evaluating intervention methods across three dimensions: control effectiveness, capability preservation, and interpretability. The expert rating protocol for interpretability establishes a quantitative baseline for future work, addressing the current lack of standardized interpretability metrics.

If successful, this research will enable safer deployment of foundation models by providing interpretable, multi-objective control mechanisms with validated capability preservation—a critical requirement for high-stakes applications in healthcare, education, and public-facing AI systems.

## 3. Methodology

### 3.1 Research Design Overview

We employ a 2×3 factorial experimental design with control condition:
- **Factor 1 (Model):** 2 levels—GPT-2-large (774M parameters), LLaMA-7B
- **Factor 2 (Method):** 3 levels—SAE-guided (proposed), Heuristic steering (SafeSteer baseline), Probe-only (Dubey baseline)
- **Control:** No intervention baseline
- **Total conditions:** 8 (2 models × 4 methods)

Each method is evaluated across three control objectives: safety (toxicity reduction), factuality (hallucination mitigation), and style (sentiment control). Power analysis (target power=0.80, α=0.05, expected effect size d=0.5) indicates n=64 evaluation prompts per condition, yielding 192 total prompts across objectives.

### 3.2 Phase 1: SAE Feature Discovery and Causal Validation

#### 3.2.1 SAE Training

We train sparse autoencoders on model activations to discover monosemantic features. For a given transformer layer $l$ with residual stream activations $\mathbf{x} \in \mathbb{R}^{d_{model}}$, the SAE consists of:

**Encoder:**
$$\mathbf{f} = \text{ReLU}(\mathbf{W}_{enc}\mathbf{x} + \mathbf{b}_{enc})$$

where $\mathbf{W}_{enc} \in \mathbb{R}^{d_{hidden} \times d_{model}}$, $\mathbf{f} \in \mathbb{R}^{d_{hidden}}$ are sparse feature activations, and $d_{hidden} > d_{model}$ (overcomplete representation).

**Decoder:**
$$\hat{\mathbf{x}} = \mathbf{W}_{dec}\mathbf{f} + \mathbf{b}_{dec}$$

where $\mathbf{W}_{dec} \in \mathbb{R}^{d_{model} \times d_{hidden}}$.

**Training Objective:**
$$\mathcal{L} = \|\mathbf{x} - \hat{\mathbf{x}}\|_2^2 + \lambda \|\mathbf{f}\|_1$$

The L1 penalty (sparsity coefficient $\lambda$) encourages monosemantic feature learning. We perform grid search over:
- $d_{hidden} \in \{2048, 4096, 8192\}$
- $\lambda \in \{10^{-3}, 10^{-4}, 10^{-5}\}$

**Data Collection:** Extract activations from middle-to-late layers (layers 15-20 for GPT-2-large, layers 18-24 for LLaMA-7B) on 100,000 diverse text samples from The Pile dataset. Training uses Adam optimizer with learning rate $10^{-4}$ for 50,000 steps.

**Hyperparameter Selection:** Choose configuration maximizing:
$$\text{Score} = \frac{\text{Reconstruction Quality}}{\text{Mean Feature Polysemanticity}}$$

where reconstruction quality = $1 - \frac{\mathcal{L}_{reconstruction}}{\text{baseline variance}}$ and polysemanticity is measured via human annotation (Section 3.2.2).

#### 3.2.2 Feature Interpretability Assessment

For each trained SAE, we evaluate monosemanticity of the top-100 features (ranked by activation frequency):

**Annotation Protocol:**
1. For each feature $f_i$, extract 10 text examples with highest activations
2. Two independent annotators classify each feature as:
   - **Monosemantic:** Activates for single interpretable concept (e.g., "medical terminology")
   - **Polysemantic:** Activates for multiple unrelated concepts
   - **Unclear:** No discernible pattern

3. Compute inter-rater agreement using Cohen's κ; require κ > 0.7
4. Resolve disagreements through discussion

**Success Criterion:** ≥60% of top-100 features classified as monosemantic. If violated, adjust SAE hyperparameters and retrain.

#### 3.2.3 Causal Validation via Activation Patching

Following Campbell et al. (2023), we validate that identified features causally influence model outputs:

**Patching Procedure:**
1. For feature $f_i$, select 64 validation prompts relevant to target control objective
2. Run clean forward pass: $\mathbf{x}^{clean} \rightarrow \mathbf{f}^{clean} \rightarrow \mathbf{y}^{clean}$
3. Run ablated pass: Replace $f_i^{clean}$ with mean activation $\bar{f}_i$ (computed over validation set)
4. Measure causal effect: 
$$\Delta_{logit}(f_i) = \frac{1}{64}\sum_{j=1}^{64} \left| \text{logit}(\mathbf{y}_j^{clean}) - \text{logit}(\mathbf{y}_j^{ablated}) \right|$$

**Feature Selection:** Retain features with $\Delta_{logit} \geq 0.2$ for steering vector computation. This threshold ensures features have meaningful causal effects (Campbell et al. found lying-relevant heads with $\Delta_{logit} \approx 0.3$-0.5).

**Objective-Specific Feature Discovery:**
- **Safety:** Identify features activating strongly on toxic vs. neutral text pairs from RealToxicityPrompts
- **Factuality:** Identify features differentiating truthful vs. false statements from TruthfulQA
- **Style:** Identify features correlating with sentiment (positive/negative) from SST-2 dataset

### 3.3 Phase 2: Feature-Space Steering Vector Computation

#### 3.3.1 Steering Vector Design

Unlike heuristic methods that compute steering vectors directly in activation space, we compute them in SAE feature space:

**Feature-Space Contrast:**
For control objective $O$ (e.g., toxicity reduction), collect paired examples:
- $\mathcal{D}_{target}$: Examples exhibiting desired behavior (neutral text)
- $\mathcal{D}_{avoid}$: Examples exhibiting undesired behavior (toxic text)

Compute mean feature activations:
$$\bar{\mathbf{f}}_{target} = \frac{1}{|\mathcal{D}_{target}|}\sum_{\mathbf{x} \in \mathcal{D}_{target}} \text{SAE}_{enc}(\mathbf{x})$$
$$\bar{\mathbf{f}}_{avoid} = \frac{1}{|\mathcal{D}_{avoid}|}\sum_{\mathbf{x} \in \mathcal{D}_{avoid}} \text{SAE}_{enc}(\mathbf{x})$$

**Feature-Space Steering Vector:**
$$\mathbf{s}_{feature} = \bar{\mathbf{f}}_{target} - \bar{\mathbf{f}}_{avoid}$$

**Projection to Activation Space:**
$$\mathbf{s}_{activation} = \mathbf{W}_{dec} \cdot \mathbf{s}_{feature}$$

This two-step process ensures steering operates along interpretable feature dimensions rather than arbitrary activation directions.

#### 3.3.2 Selective Feature Steering

To minimize interference, we apply steering only to causally-validated features:

$$\mathbf{s}_{selective} = \mathbf{W}_{dec} \cdot (\mathbf{s}_{feature} \odot \mathbf{m})$$

where $\mathbf{m} \in \{0,1\}^{d_{hidden}}$ is a binary mask with $m_i = 1$ if $\Delta_{logit}(f_i) \geq 0.2$, else $m_i = 0$.

#### 3.3.3 Steering Strength Optimization

For fair comparison across methods, we optimize steering coefficient $\alpha$ to achieve target control level:

**Steered Generation:**
$$\mathbf{x}_{steered}^{(l)} = \mathbf{x}_{original}^{(l)} + \alpha \cdot \mathbf{s}_{activation}$$

where $\mathbf{x}^{(l)}$ denotes layer $l$ activations.

**Optimization:** Binary search over $\alpha \in [0.1, 2.0]$ to achieve 80% control effectiveness (e.g., 80% toxicity reduction on validation set). This normalized comparison isolates capability preservation differences.

### 3.4 Phase 3: Multi-Objective Validation and Monitoring

#### 3.4.1 Feature-Space Monitoring

During steered generation, we track SAE feature activations to detect unintended effects:

**Monitoring Protocol:**
1. For each generated token, compute feature activations: $\mathbf{f}_{gen} = \text{SAE}_{enc}(\mathbf{x}_{steered})$
2. Compare to baseline distribution: $\mathbf{f}_{baseline}$ (computed on unsteered generations)
3. Flag anomalies: Features with $|f_{gen,i} - \bar{f}_{baseline,i}| > 2\sigma_{baseline,i}$

**Intervention Refinement:** If monitoring detects unintended feature changes (e.g., factuality features suppressed during safety steering), iteratively adjust feature mask $\mathbf{m}$ to exclude interfering features.

#### 3.4.2 Control Effectiveness Evaluation

**Safety (Toxicity Reduction):**
- **Dataset:** RealToxicityPrompts (100,000 prompts)
- **Metric:** Perspective API toxicity score; compute reduction:
$$\text{Toxicity Reduction} = \frac{\text{Toxicity}_{baseline} - \text{Toxicity}_{steered}}{\text{Toxicity}_{baseline}} \times 100\%$$
- **Target:** ≥80% reduction

**Factuality (Hallucination Mitigation):**
- **Dataset:** TruthfulQA (817 questions)
- **Metric:** Accuracy of truthful responses (GPT-4-based evaluation following TruthfulQA protocol)
- **Target:** ≥85% accuracy (vs. baseline ~60% for GPT-2-large)

**Style (Sentiment Control):**
- **Dataset:** Custom prompts (192 neutral prompts)
- **Metric:** Sentiment classifier agreement (DistilBERT fine-tuned on SST-2)
$$\text{Style Success} = \frac{\text{Generations matching target sentiment}}{\text{Total generations}} \times 100\%$$
- **Target:** ≥90% agreement

#### 3.4.3 Capability Preservation Evaluation

**Benchmarks:**
- **MMLU (Massive Multitask Language Understanding):** 57 tasks, 5-shot evaluation
- **BBH (Big-Bench Hard):** 23 challenging tasks, 3-shot evaluation

**Metric:**
$$\text{Capability Retention} = \frac{\text{Score}_{steered}}{\text{Score}_{baseline}} \times 100\%$$

**Success Criterion:** ≥98% retention on both benchmarks (exceeding Dubey's 97% baseline).

**Cross-Objective Interference:**
Measure capability degradation when steering for one objective:
$$\text{Interference}_{O_1 \rightarrow O_2} = \text{Score}_{O_2,baseline} - \text{Score}_{O_2,steered\_for\_O_1}$$

**Target:** ≤5% degradation (vs. expected ≥10% for heuristic methods).

#### 3.4.4 Interpretability Evaluation

**Expert Rating Protocol:**
Recruit 5 mechanistic interpretability researchers to evaluate each method on:

**Rating Dimensions (1-5 Likert scale):**
1. **Feature Clarity:** "Can you identify what concept each steering-relevant feature represents?"
2. **Failure Diagnosis:** "When steering fails, can you determine why from the method's outputs?"
3. **Intervention Transparency:** "Do you understand the mechanism by which this method achieves control?"
4. **Debugging Ease:** "How easily could you modify this intervention to fix unintended effects?"
5. **Overall Interpretability:** "How interpretable is this method overall?"

**Evaluation Materials:**
- Top-10 features/dimensions used by each method
- Activation patterns on 20 example prompts
- Failure cases (5 prompts where steering failed)

**Analysis:** Friedman test (non-parametric repeated measures) across methods, followed by Wilcoxon signed-rank post-hoc tests with Bonferroni correction (α=0.05).

**Success Criterion:** SAE-guided mean rating ≥4.0/5.0, significantly higher than heuristic (expected ≤2.5) and probe-only (expected ≤3.0).

### 3.5 Baseline Implementations

#### 3.5.1 Heuristic Steering (SafeSteer Baseline)

Following Ghosh et al. (2025):
1. Collect 100 paired examples (harmful/neutral for safety, false/true for factuality, negative/positive for style)
2. Compute activation differences: $\mathbf{s}_{heuristic} = \bar{\mathbf{x}}_{target} - \bar{\mathbf{x}}_{avoid}$
3. Apply steering: $\mathbf{x}_{steered} = \mathbf{x}_{original} + \alpha \cdot \mathbf{s}_{heuristic}$
4. Optimize $\alpha$ to match SAE-guided control effectiveness (80% toxicity reduction)

#### 3.5.2 Probe-Only Steering (Dubey Baseline)

Following Dubey (2025):
1. Train linear probe: $\mathbf{w}^T\mathbf{x} + b$ to classify target/avoid examples
2. Use probe direction as steering vector: $\mathbf{s}_{probe} = \mathbf{w}$
3. Apply steering: $\mathbf{x}_{steered} = \mathbf{x}_{original} + \alpha \cdot \mathbf{s}_{probe}$
4. Optimize $\alpha$ to match control effectiveness

### 3.6 Statistical Analysis Plan

**Primary Hypothesis Test (P1 - Capability Preservation):**
- **Test:** Two-sample t-test comparing SAE-guided vs. each baseline
- **Variables:** DV = Capability retention (%), IV = Method
- **Significance:** α=0.05, two-tailed
- **Expected Effect Size:** Cohen's d ≥ 0.5 (medium effect)

**Secondary Hypothesis Test (P2 - Interpretability):**
- **Test:** Friedman test + Wilcoxon post-hoc (Bonferroni corrected)
- **Variables:** DV = Expert ratings (ordinal 1-5), IV = Method
- **Significance:** α=0.05

**Tertiary Hypothesis Test (P3 - Multi-Objective Interference):**
- **Test:** One-way ANOVA
- **Variables:** DV = Cross-objective degradation (%), IV = Method
- **Significance:** α=0.05
- **Expected Effect Size:** η² ≥ 0.14 (large effect)

**Confound Controls:**
- Steering strength normalized across methods (all achieve 80% control)
- Same model checkpoints across conditions
- Same evaluation datasets and metrics
- 3 random seeds for SAE training and baseline initialization

**Falsification Criteria:**
The hypothesis is falsified if:
1. **F1:** No significant improvement (p≥0.05) in control effectiveness OR capability preservation vs. any baseline
2. **F2:** No significant interpretability difference (p≥0.05) vs. probe-only baseline
3. **F3:** <50% of top-10 SAE features are monosemantic
4. **F4:** Multi-objective steering causes >15% capability degradation

### 3.7 Implementation Details

**Computational Resources:**
- SAE training: 4× NVIDIA A100 GPUs, ~8 GPU-hours per model
- Activation patching: ~2 GPU-hours per objective
- Evaluation: ~12 GPU-hours total (benchmarks + control metrics)
- Total: ~30 GPU-hours per model (60 GPU-hours for GPT-2-large + LLaMA-7B)

**Software Stack:**
- PyTorch 2.0 for SAE training and model inference
- TransformerLens library for activation patching
- Hugging Face Transformers for model loading and evaluation
- Perspective API for toxicity scoring
- Custom evaluation harness for TruthfulQA and style metrics

**Reproducibility:**
- All code released on GitHub with Apache 2.0 license
- Pre-trained SAEs and steering vectors published on Hugging Face Hub
- Evaluation datasets and prompts included in repository
- Random seeds fixed (42, 123, 456) for all experiments

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Superior Capability Preservation**
We expect SAE-guided steering to achieve ≥98% capability retention on MMLU and BBH benchmarks, significantly exceeding the 97% baseline from probe-only methods (Dubey, 2025). The feature-space monitoring mechanism should detect unintended feature changes early, enabling iterative refinement before catastrophic degradation occurs. Statistical analysis (two-sample t-test, α=0.05) should demonstrate significant improvement with medium-to-large effect size (Cohen's d ≥ 0.5).

**Primary Outcome 2: Equivalent Control Effectiveness**
SAE-guided steering should match or exceed baseline control effectiveness: ≥80% toxicity reduction (vs. SafeSteer's 87%), ≥85% factuality accuracy (vs. baseline ~60%), and ≥90% style transfer success. This demonstrates that interpretability-first design does not sacrifice control power.

**Primary Outcome 3: Significantly Higher Interpretability**
Expert evaluators should rate SAE-guided steering ≥4.0/5.0 on interpretability dimensions, significantly higher than heuristic methods (≤2.5/5.0) and probe-only approaches (≤3.0/5.0). Friedman test (α=0.05) should confirm statistical significance. Qualitative feedback should highlight specific advantages: ability to identify which features drive control, transparent failure diagnosis, and ease of debugging.

**Secondary Outcome 1: Reduced Multi-Objective Interference**
Cross-objective capability degradation should be ≤5% for SAE-guided steering (vs. ≥10% for heuristic methods). Feature-space monitoring should successfully detect and mitigate interference (e.g., safety steering inadvertently suppressing factuality features). One-way ANOVA (α=0.05) should demonstrate significant reduction in interference with large effect size (η² ≥ 0.14).

**Secondary Outcome 2: Validated Causal Features**
≥70% of top-10 SAE features (per control objective) should demonstrate causal effects with $\Delta_{logit} \geq 0.2$ in activation patching experiments. This validates that SAE features are not merely correlational but causally relevant to model behavior.

**Secondary Outcome 3: Monosemantic Feature Discovery**
≥60% of top-100 SAE features should be classified as monosemantic by human annotators (inter-rater agreement κ>0.7). This confirms that SAE training successfully discovers interpretable control dimensions, supporting the framework's interpretability-first design philosophy.

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Interpretability-First Intervention Paradigm:** This research establishes SAE feature space as a principled substrate for intervention design, moving beyond heuristic or black-box approaches. By formalizing the discover→design→validate cycle, we provide a theoretical framework for systematically translating mechanistic insights into practical control mechanisms. This addresses a critical gap identified in Bereska and Gavves' (2024) MI survey: the lack of systematic integration between interpretability research and intervention development.

2. **Causal Feature Validation Framework:** Integrating activation patching (Campbell et al., 2023) into intervention design ensures features used for steering have verified causal effects rather than mere correlations. This methodological contribution establishes a higher standard for interpretability-based interventions, requiring not just human-interpretable features but causally-validated ones.

3. **Multi-Objective Control Theory:** The framework's explicit modeling of cross-objective interference and feature-space mitigation strategies contributes to understanding how multiple control objectives interact in high-dimensional activation spaces. This addresses a largely unexplored area in current intervention research, which typically focuses on single objectives.

**Methodological Contributions:**

1. **Feature-Space Steering Computation:** Computing steering vectors in SAE feature space (feature-based contrast) rather than raw activation space provides a novel method for designing interpretable interventions. This technique is generalizable beyond our specific control objectives to any behavior where SAE features can be discovered.

2. **Comprehensive Validation Protocol:** The three-dimensional evaluation framework (control effectiveness, capability preservation, interpretability) with quantitative metrics for each dimension establishes a new standard for intervention research. The expert rating protocol for interpretability addresses the current lack of standardized interpretability metrics in the field.

3. **Feature-Space Monitoring System:** Real-time tracking of SAE feature activations during generation provides an early warning system for unintended effects, enabling proactive intervention refinement. This monitoring approach is novel and could be adapted to other intervention methods beyond activation steering.

### 4.3 Practical Impact

**Deployment Safety:**
The framework's interpretability and capability preservation properties directly address deployment risks in production systems. Feature-space monitoring enables transparent diagnosis of steering failures (e.g., "Feature 42 insufficiently suppressed in layer 18"), allowing engineers to debug and refine interventions systematically rather than through trial-and-error. This is critical for high-stakes applications in healthcare, education, and public-facing AI systems where unexplained failures are unacceptable.

**Multi-Objective Control:**
Real-world deployments typically require satisfying multiple constraints simultaneously (e.g., safe AND factually accurate AND appropriate tone). The framework's validated multi-objective capability with interference mitigation provides a practical solution for these scenarios, reducing the need for separate, potentially conflicting intervention systems.

**Regulatory Compliance:**
As AI regulation increasingly demands explainability and safety guarantees, interpretable intervention methods become essential for compliance. The framework's feature-level transparency and causal validation provide auditable evidence of how safety controls function, supporting regulatory requirements for AI system documentation.

**Cost-Effectiveness:**
While SAE training incurs upfront computational cost (~8 GPU-hours per model), the resulting interpretable features enable faster iteration on intervention design compared to black-box methods requiring extensive trial-and-error. For organizations deploying multiple models or frequently updating interventions, this amortizes favorably.

### 4.4 Broader Impact

**AI Safety Research Community:**
This work bridges mechanistic interpretability and AI safety intervention research, demonstrating how MI techniques can directly improve practical control methods. The open-source release of code, pre-trained SAEs, and evaluation protocols will enable other researchers to build on this framework, potentially accelerating progress on interpretable AI safety.

**Foundation Model Developers:**
Major AI labs (OpenAI, Anthropic, Google DeepMind) actively research intervention methods for their deployed models. This framework provides a validated alternative to current approaches, potentially influencing how these organizations implement safety controls. The demonstrated capability preservation is particularly relevant for commercial deployments where maintaining model quality is critical.

**Mechanistic Interpretability Field:**
By demonstrating a concrete application of SAE features to high-value intervention tasks, this research strengthens the case for continued investment in MI research. It addresses a common criticism that interpretability research is purely academic by showing direct practical utility.

**Limitations and Future Work:**
The research scope (GPT-2-large/LLaMA-7B) leaves open questions about scaling to frontier models (70B+ parameters). Future work should investigate selective layer SAE training and sparse caching strategies to make the framework computationally feasible at larger scales. Additionally, adversarial robustness testing (jailbreak resistance) is critical for production deployment but beyond initial scope. The framework's performance under adversarial conditions requires dedicated investigation.

### 4.5 Success Metrics Summary

The research will be considered successful if:

1. **Control Effectiveness:** ≥80% toxicity reduction, ≥85% factuality accuracy, ≥90% style transfer (matching or exceeding baselines)
2. **Capability Preservation:** ≥98% MMLU/BBH retention (significantly better than 97% baseline, p<0.05)
3. **Interpretability:** ≥4.0/5.0 expert rating (significantly better than ≤3.0 baselines, p<0.05)
4. **Multi-Objective:** ≤5% cross-objective interference (significantly better than ≥10% baseline, p<0.05)
5. **Feature Quality:** ≥60% monosemantic features, ≥70% causally-validated features

Achieving these metrics would validate the core hypothesis that SAE-guided steering provides superior interpretability and capability preservation while maintaining control effectiveness, establishing a new paradigm for interpretable foundation model interventions suitable for production deployment.