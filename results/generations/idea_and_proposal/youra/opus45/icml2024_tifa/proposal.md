# Research Proposal: Safety Binding Theory: Understanding Compositional Safety Failures in Vision-Language Models

## 1. Introduction

### 1.1 Background

The rapid advancement of Multi-modal Foundation Models (MFMs) and AI Agents has ushered in a new era of artificial intelligence capabilities. Vision-Language Models (VLMs), a prominent class of MFMs, integrate visual and textual modalities to enable sophisticated reasoning across diverse inputs. Models such as LLaVA, InstructBLIP, Qwen-VL, and GPT-4V have demonstrated remarkable performance in tasks ranging from visual question answering to complex multimodal reasoning. However, as these systems are increasingly deployed in high-stakes applications—including healthcare diagnostics, autonomous systems, and content moderation—understanding and ensuring their safety becomes paramount.

A critical and puzzling vulnerability has emerged in VLM research: individually safe visual and textual components can become unsafe when combined. This phenomenon, which we term *compositional safety failure*, represents a fundamental challenge to the trustworthiness of multimodal AI systems. Current research has predominantly framed this issue as a "modality gap" problem, focusing on representation alignment between visual and textual embeddings. However, this perspective fails to explain *why* safety specifically degrades at cross-modal integration points, leaving a significant theoretical and practical gap in our understanding.

Recent empirical evidence underscores the severity of this challenge. Wang et al. (2025) demonstrated that multimodal safety is inherently asymmetric, with visual alignment creating uneven safety constraints across modalities. Xu et al. (2025) showed that hidden states at specific transformer layers play crucial roles in safety mechanism activation, yet vision-language alignment fails to preserve these safety patterns. These findings suggest that compositional safety failures are not merely artifacts of poor representation quality but emerge from fundamental interference at the integration process itself.

### 1.2 Research Objectives

This research proposes **Safety Binding Theory (SBT)**, a novel theoretical framework that explains compositional safety failures in VLMs through the lens of *binding interference* at cross-modal attention layers. Our primary objectives are:

1. **Theoretical Development**: Formalize the Safety Binding Algebra to model how safety properties compose (or fail to compose) across modalities, introducing the binding interference term $\varepsilon_{\text{bind}}$ that captures emergent safety degradation.

2. **Empirical Validation**: Demonstrate that adversarial attack success rates are significantly higher (≥15%) at integration layers compared to unimodal layers, and establish a strong correlation (r ≥ 0.5) between cross-modal attention entropy and safety degradation.

3. **Practical Intervention**: Develop binding-aware training objectives that extend existing multimodal adversarial training frameworks (specifically MMCoA) to improve compositional safety by ≥10% on standardized benchmarks without sacrificing unimodal safety.

4. **Diagnostic Tool Development**: Create a predictive diagnostic using attention entropy to identify high-risk modal combinations before deployment.

### 1.3 Significance

This research addresses a critical gap in multimodal AI safety by providing the first mechanistic explanation for *where* and *why* compositional safety fails. The significance extends across multiple dimensions:

**Scientific Contribution**: SBT bridges cognitive science concepts (the binding problem) with AI safety, offering a principled framework for understanding emergent vulnerabilities in multimodal systems. This theoretical foundation enables systematic study of compositional safety rather than ad-hoc vulnerability patching.

**Practical Impact**: The binding-aware defenses and diagnostic tools developed through this research will directly benefit practitioners deploying VLMs in safety-critical applications, enabling proactive risk assessment and mitigation.

**Regulatory Relevance**: As AI governance frameworks increasingly demand transparency and safety assurance for foundation models, SBT provides quantifiable metrics and interpretable mechanisms that support regulatory compliance and model auditing.

## 2. Methodology

### 2.1 Theoretical Framework: Safety Binding Algebra

We formalize compositional safety through the **Safety Binding Algebra**, which models how safety properties transform during cross-modal integration:

$$S_{\text{compose}}(v, t) = S(v) \otimes S(t) + \varepsilon_{\text{bind}}$$

where:
- $S(v) \in [0,1]$ represents the safety score of the visual input $v$
- $S(t) \in [0,1]$ represents the safety score of the textual input $t$
- $\otimes$ denotes the non-commutative composition operator reflecting asymmetric integration
- $\varepsilon_{\text{bind}}$ captures the emergent binding interference term

The binding interference term is operationalized as:

$$\varepsilon_{\text{bind}} = \alpha \cdot H(\text{attn}_{\text{cross}}) + \beta \cdot \|\Delta h_{\text{safety}}\|$$

where $H(\text{attn}_{\text{cross}})$ is the entropy of cross-modal attention distributions at integration layers, $\|\Delta h_{\text{safety}}\|$ measures the semantic shift in safety-relevant hidden states, and $\alpha, \beta$ are learnable coefficients calibrated per architecture.

The **Binding Interference Measure (BIM)** is thus defined as:

$$\text{BIM} = H(\text{attn}_{\text{cross}}) + \|\Delta h_{\text{safety}}\|$$

### 2.2 Data Collection and Experimental Setup

#### 2.2.1 Model Selection

We evaluate SBT across three representative VLM architectures:
- **LLaVA-1.5-7B**: Open-source model with well-documented architecture
- **InstructBLIP-7B**: Alternative integration mechanism (Q-Former)
- **Qwen-VL-7B**: Production-grade model with different pretraining

#### 2.2.2 Benchmark and Datasets

**Primary Evaluation**: MMDT (Multimodal Decoding Trust) benchmark suite, which provides standardized safety evaluation across:
- Toxic content generation resistance
- Harmful instruction refusal
- Jailbreak attack defense
- Privacy preservation

**Adversarial Attack Suite**: We employ multiple attack types to ensure robustness:
- Visual adversarial perturbations (PGD-based)
- Textual jailbreak prompts (GCG-style)
- Compositional attacks targeting integration (novel, SBT-informed)

**Sample Size**: Minimum n = 20 runs per condition (attack type × layer type × model) to achieve statistical power of 0.8 for detecting 15% ASR differences.

### 2.3 Experimental Design

#### Experiment 1: Existence Verification (SH1)

**Objective**: Demonstrate that safety binding interference exists at cross-modal integration layers.

**Procedure**:
1. Identify integration layers in each VLM architecture (typically layers 12-24 where vision-language features merge)
2. Conduct layer-wise adversarial attacks:
   - **Unimodal attacks**: Target only visual encoder or text embeddings
   - **Integration attacks**: Target cross-modal attention layers specifically
3. Measure Attack Success Rate (ASR) for each condition

**Metrics**:
- $\text{ASR}_{\text{integration}}$: Attack success rate when targeting integration layers
- $\text{ASR}_{\text{unimodal}}$: Attack success rate when targeting unimodal components
- $\Delta\text{ASR} = \text{ASR}_{\text{integration}} - \text{ASR}_{\text{unimodal}}$

**Statistical Analysis**: Paired t-test with $\alpha = 0.05$ (one-tailed), reporting Cohen's d effect size.

**Success Criterion**: $\Delta\text{ASR} \geq 15\%$ with $p < 0.05$

**Falsification Criterion**: $\text{ASR}_{\text{integration}} \leq \text{ASR}_{\text{unimodal}}$

#### Experiment 2: Mechanism Validation (SH2)

**Objective**: Establish that cross-modal attention entropy correlates with safety degradation.

**Procedure**:
1. For each input pair $(v, t)$, compute cross-modal attention entropy at integration layers:
   $$H(\text{attn}_{\text{cross}}) = -\sum_{i,j} a_{ij} \log a_{ij}$$
   where $a_{ij}$ represents attention weights between visual token $i$ and text token $j$
2. Measure safety property preservation via refusal rate on MMDT toxic content tasks
3. Compute hidden state semantic shift:
   $$\|\Delta h_{\text{safety}}\| = \|h_{\text{multimodal}}^{(l)} - h_{\text{text-only}}^{(l)}\|_2$$
   at safety-critical layers $l$ identified via TGA methodology

**Metrics**:
- Pearson correlation $r$ between $H(\text{attn}_{\text{cross}})$ and $(1 - \text{refusal\_rate})$
- Pearson correlation $r$ between BIM and ASR

**Statistical Analysis**: Correlation analysis with $p < 0.05$ significance threshold.

**Success Criterion**: $r \geq 0.5$ for attention entropy-safety degradation correlation

**Falsification Criterion**: $|r| < 0.3$ (no meaningful correlation)

#### Experiment 3: Causal Chain Verification (SH2 Sub-hypotheses)

**Objective**: Validate the three-step causal mechanism.

**Sub-hypothesis H-M1** (Input → Integration):
- Intervention: Ablate cross-modal attention heads
- Prediction: Ablation eliminates binding interference signal

**Sub-hypothesis H-M2** (Integration → Interference):
- Intervention: Apply representation alignment at integration layers
- Prediction: Reduced hidden state semantic shift correlates with reduced BIM

**Sub-hypothesis H-M3** (Interference → Degradation):
- Intervention: Inject noise at integration layers vs. other layers
- Prediction: Integration layer noise causes disproportionate safety degradation

**Analysis**: Mediation analysis to quantify indirect effects through the causal chain.

#### Experiment 4: Binding-Aware Training (SH3)

**Objective**: Demonstrate that binding-aware training improves compositional safety.

**Algorithm: Binding-Aware Multimodal Contrastive Adversarial Training (BA-MMCoA)**

```
Input: VLM model M, training data D, binding coefficient λ
Output: Safety-enhanced model M*

1. Initialize M* ← M
2. For each epoch:
   a. For each batch (v, t, y) ∈ D:
      i.   Compute standard MMCoA loss: L_MMCoA
      ii.  Extract cross-modal attention at integration layers
      iii. Compute attention entropy: H(attn_cross)
      iv.  Compute binding regularization loss:
           L_bind = λ · max(0, H(attn_cross) - τ)
           where τ is the entropy threshold
      v.   Compute safety-coherence loss:
           L_coherence = ||S(v,t) - min(S(v), S(t))||²
      vi.  Total loss: L = L_MMCoA + L_bind + L_coherence
      vii. Update M* via gradient descent
3. Return M*
```

**Hyperparameters**:
- $\lambda \in \{0.1, 0.5, 1.0\}$ (binding coefficient)
- $\tau$ calibrated per architecture based on baseline entropy distribution
- Learning rate: $1 \times 10^{-5}$ with cosine annealing

**Baselines**:
- Standard adversarial training (AT)
- MMCoA without binding awareness
- Multimodal Adversarial Training (MAT)

**Metrics**:
- MMDT compositional safety score
- Unimodal safety preservation (≤2% degradation acceptable)
- General task performance (VQA accuracy, captioning quality)

**Statistical Analysis**: Independent t-test comparing BA-MMCoA vs. baselines, $\alpha = 0.05$ (two-tailed).

**Success Criterion**: ≥10% improvement on MMDT compositional safety with ≤2% unimodal degradation

**Falsification Criterion**: No improvement OR >5% unimodal safety degradation

### 2.4 Diagnostic Tool Development

Based on validated BIM metrics, we develop a **Compositional Safety Risk Predictor**:

$$\text{Risk}(v, t) = \sigma(w_1 \cdot H(\text{attn}_{\text{cross}}) + w_2 \cdot \|\Delta h_{\text{safety}}\| + b)$$

where $\sigma$ is the sigmoid function and weights $(w_1, w_2, b)$ are learned from validation data.

**Deployment Protocol**:
1. Pre-compute attention entropy thresholds for target VLM
2. At inference, compute BIM for input pair
3. Flag high-risk combinations (Risk > 0.7) for human review or rejection

### 2.5 Evaluation Metrics Summary

| Metric | Definition | Target |
|--------|------------|--------|
| $\Delta$ASR | Integration vs. unimodal attack success difference | ≥15% |
| Entropy-Safety Correlation | Pearson r between H(attn) and safety degradation | ≥0.5 |
| MMDT Improvement | Compositional safety score increase | ≥10% |
| Unimodal Preservation | Safety score change on single-modality inputs | ≤2% degradation |
| Risk Predictor AUC | Area under ROC for safety risk prediction | ≥0.8 |

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Theoretical Outcomes**:
- Validated Safety Binding Theory providing mechanistic explanation for compositional safety failures
- Formalized Safety Binding Algebra enabling quantitative analysis of multimodal safety composition
- Empirically calibrated Binding Interference Measure (BIM) applicable across VLM architectures

**Empirical Outcomes**:
- Demonstration of ≥15% higher attack success rates at integration layers vs. unimodal layers across three VLM architectures
- Established correlation (r ≥ 0.5) between attention entropy and safety degradation
- Validated three-step causal chain from multimodal input to compositional safety failure

**Practical Outcomes**:
- BA-MMCoA training protocol achieving ≥10% compositional safety improvement on MMDT
- Deployable risk prediction tool with AUC ≥ 0.8 for identifying dangerous modal combinations
- Open-source implementation enabling community adoption and extension

### 3.2 Broader Impact

**Advancing Multimodal AI Safety**: SBT provides the foundational theory needed to systematically address compositional vulnerabilities, moving the field beyond reactive patching toward principled safety engineering.

**Enabling Trustworthy Deployment**: The diagnostic tools and training protocols developed through this research directly support safe deployment of VLMs in healthcare, education, and content moderation applications where compositional attacks pose significant risks.

**Informing AI Governance**: By providing interpretable metrics (attention entropy, BIM) and clear failure mechanisms, SBT supports regulatory frameworks requiring transparency and safety assurance for foundation models.

**Future Research Directions**: SBT establishes a framework extensible to:
- Agent-level compositional safety (tool use, API access)
- Additional modalities (audio, video)
- Scalable oversight mechanisms leveraging binding-aware monitoring

### 3.3 Limitations and Mitigation

**Limitation 1**: SBT requires attention-level access, limiting applicability to closed-source models.
*Mitigation*: Develop black-box approximations using output-based probing.

**Limitation 2**: Binding interference metrics require per-architecture calibration.
*Mitigation*: Establish calibration protocols and publish reference values for common architectures.

**Limitation 3**: Current scope limited to vision-language; extension to other modalities requires validation.
*Mitigation*: Design experiments with modular framework enabling future modality extensions.

### 3.4 Timeline and Resources

**Phase 1 (Months 1-3)**: Theoretical development and experimental infrastructure
**Phase 2 (Months 4-6)**: Existence and mechanism validation experiments
**Phase 3 (Months 7-9)**: Binding-aware training development and evaluation
**Phase 4 (Months 10-12)**: Diagnostic tool development, documentation, and dissemination

**Computational Requirements**: 4× A100 GPUs for 12 weeks (layer-wise analysis, training experiments)

This research will establish Safety Binding Theory as a foundational framework for understanding and mitigating compositional safety failures in multimodal AI systems, directly contributing to the development of trustworthy Multi-modal Foundation Models and AI Agents.