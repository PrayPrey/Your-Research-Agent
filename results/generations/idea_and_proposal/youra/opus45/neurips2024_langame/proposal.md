# Research Proposal: Contrastive Differential Evaluation of Language Acquisition (C-DELA): Measuring How Multi-Agent Language Games Improve LLM Compositional Abilities

## 1. Introduction

### 1.1 Background

The dominant paradigm for training Large Language Models (LLMs) has remained remarkably stable over recent years, relying almost exclusively on supervised learning and preference-based losses. While this approach has yielded impressive capabilities, it fundamentally diverges from how humans acquire language. Ludwig Wittgenstein's concept of "language games" in *Philosophical Investigations* emphasized that words acquire meaning through use within social, interactive contexts. Cognitive science research reinforces this perspective, demonstrating that genuine language acquisition thrives on dynamic, context-driven interactions rather than passive exposure to static corpora.

Recent work in language emergence simulations has shown that multi-agent communication games produce languages with remarkable properties: compositionality, generalizability, and efficient transmission. Rodriguez Luna et al. (2020) demonstrated that functional pressures in such games—including referential success and communicative efficiency—produce emergent languages with "less redundancy, more focus on high-level conceptual information, and better abilities of generalisation." These findings suggest that interactive training may address fundamental limitations in current LLMs.

Despite their impressive performance, LLMs exhibit a well-documented "compositionality gap" (Press et al., 2023), failing to systematically combine known concepts in novel ways. This limitation manifests in restricted planning abilities, insufficient personalization, and brittle generalization. The gap between small-scale emergent communication agents—which develop compositional languages through interaction—and large-scale LLMs trained on static data suggests that the lack of interactive training may be a critical deficiency.

### 1.2 Research Problem

A fundamental barrier to advancing interactive LLM training is the absence of rigorous measurement frameworks. Current evaluation approaches rely primarily on behavioral metrics (task accuracy, perplexity) that cannot distinguish genuine representational improvements from superficial performance gains. Without principled metrics that can detect whether interactive training actually improves fundamental language properties, the field cannot systematically compare approaches or identify which aspects of language games drive improvements.

### 1.3 Research Objectives

This research proposes the **Contrastive Differential Evaluation of Language Acquisition (C-DELA)** framework with the following objectives:

1. **Primary Objective**: Develop and validate a measurement framework that can detect whether multi-agent language games induce genuine representational improvements in LLMs, as opposed to mere behavioral changes.

2. **Secondary Objective**: Quantify improvements across four fundamental language properties derived from Hockett's design features: compositionality, grounding, displacement, and transmission efficiency.

3. **Tertiary Objective**: Establish calibrated metrics with noise floors that enable principled comparison of different interactive training approaches.

### 1.4 Significance

This research addresses a critical gap in the emerging field of Language Gamification. By providing the first rigorous measurement framework for interactive LLM training, C-DELA will:

- Enable systematic comparison of different language game designs and training protocols
- Distinguish genuine language property improvements from measurement artifacts
- Bridge the gap between small-scale emergent communication research and large-scale LLM training
- Provide actionable insights for designing more effective interactive training paradigms

## 2. Methodology

### 2.1 Theoretical Framework

Our core hypothesis states: Under conditions of multi-agent interactive training with language games, if LLMs undergo contrastive differential assessment using probing classifiers, then measurable improvements in compositionality (CGS), grounding (GAI), displacement (DCM), and transmission (TES) will be detected, because interactive training induces representational changes that enhance these language properties beyond what supervised pretraining alone provides.

The proposed causal mechanism operates through three steps:

$$\text{Interactive Training} \xrightarrow{\text{functional pressures}} \text{Representational Change} \xrightarrow{\text{altered activations}} \text{Probing Signal Difference} \xrightarrow{\text{calibration}} \text{Quantified Metrics}$$

### 2.2 Multi-Agent Language Game Design

#### 2.2.1 Referential Game Setup

We employ a referential game paradigm with 2-4 LLM agents. In each round:

1. A **sender agent** observes a target object $o_t$ from a set of candidates $O = \{o_1, ..., o_k\}$
2. The sender generates a message $m$ using its language model: $m \sim P_\theta(m|o_t)$
3. A **receiver agent** observes the message and all candidates, selecting the predicted target: $\hat{o} = \arg\max_{o \in O} P_\phi(o|m, O)$
4. Both agents receive reward $r = \mathbb{1}[\hat{o} = o_t]$

#### 2.2.2 Training Protocol

Training proceeds via policy gradient methods with the following objective:

$$\mathcal{L}(\theta, \phi) = -\mathbb{E}_{o_t \sim O, m \sim P_\theta}\left[r \cdot \log P_\theta(m|o_t) + r \cdot \log P_\phi(o_t|m, O)\right] + \lambda \mathcal{L}_{reg}$$

where $\mathcal{L}_{reg}$ includes KL-divergence regularization to prevent catastrophic forgetting:

$$\mathcal{L}_{reg} = D_{KL}(P_\theta || P_{\theta_0}) + D_{KL}(P_\phi || P_{\phi_0})$$

Training hyperparameters:
- Epochs: 1-10 (varied experimentally)
- Agents: 2-4 (varied experimentally)
- Candidate set size: $k \in \{4, 8, 16\}$
- Learning rate: $\eta = 10^{-5}$ with cosine annealing
- KL coefficient: $\lambda = 0.1$

### 2.3 C-DELA Metric Framework

#### 2.3.1 Compositional Gain Score (CGS)

CGS measures improvement in compositional structure using topological similarity (TopSim) between meaning space and message space:

$$\text{TopSim} = \rho\left(d_M(m_i, m_j), d_O(o_i, o_j)\right)$$

where $\rho$ is Spearman correlation, $d_M$ is edit distance in message space, and $d_O$ is semantic distance in object space.

The calibrated CGS is computed as:

$$\text{CGS} = \frac{\text{TopSim}_{post} - \text{TopSim}_{pre}}{\sigma_{noise}}$$

where $\sigma_{noise}$ is established through contrastive perturbation (Section 2.3.5).

#### 2.3.2 Grounding Alignment Index (GAI)

GAI quantifies symbol-referent binding using Representational Similarity Analysis (RSA). We train probing classifiers $f_\psi$ on intermediate layer activations $h^{(l)}$ to predict object properties:

$$\hat{y} = f_\psi(h^{(l)}), \quad \mathcal{L}_{probe} = \text{CrossEntropy}(\hat{y}, y)$$

GAI is computed as the RSA correlation between probing classifier representations and ground-truth object features:

$$\text{GAI} = \rho\left(\text{RDM}_{probe}, \text{RDM}_{objects}\right)$$

where RDM denotes the representational dissimilarity matrix.

#### 2.3.3 Displacement Capability Metric (DCM)

DCM measures the ability to reference non-present entities. We construct evaluation tasks where agents must communicate about objects not currently visible:

$$\text{DCM} = \text{Accuracy}_{post}(\mathcal{T}_{displacement}) - \text{Accuracy}_{pre}(\mathcal{T}_{displacement})$$

Tasks include temporal displacement (past/future objects) and counterfactual reference (hypothetical objects).

#### 2.3.4 Transmission Efficiency Score (TES)

TES evaluates whether improved language properties transfer to novel receiver architectures. After training sender $S$ with receiver $R_1$, we pair $S$ with architecturally-diverse receivers $\{R_2, ..., R_n\}$:

$$\text{TES} = \frac{1}{n-1}\sum_{i=2}^{n} \text{Accuracy}(S, R_i) - \text{Accuracy}_{random}$$

This measures whether the sender's language is genuinely more structured (transferable) rather than merely co-adapted to a specific receiver.

#### 2.3.5 Contrastive Perturbation Calibration

To establish reliable noise floors, we apply controlled perturbations that should not affect language properties:

1. **Random seed variation**: Train identical configurations with different random seeds
2. **Initialization perturbation**: Small Gaussian noise added to initial weights
3. **Data order shuffling**: Randomize training example order

The noise floor $\sigma_{noise}$ is computed as:

$$\sigma_{noise} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(\Delta_i - \bar{\Delta})^2}$$

where $\Delta_i$ represents metric differences under perturbation condition $i$.

### 2.4 Experimental Design

#### 2.4.1 Model Selection

We use LLaMA-7B as the primary model due to:
- Open-source availability enabling representation access
- Sufficient capacity for complex language games
- Established baseline performance on compositionality benchmarks

Secondary experiments will include LLaMA-13B and Mistral-7B for generalization analysis.

#### 2.4.2 Baseline Conditions

1. **No-interaction baseline**: Standard supervised fine-tuning on game transcripts without interactive training
2. **Self-play baseline**: Single-agent self-play without multi-agent dynamics
3. **Behavioral-only baseline**: Metrics computed from outputs only, without representation probing

#### 2.4.3 Experimental Conditions

| Condition | Agents | Epochs | Game Type |
|-----------|--------|--------|-----------|
| C1 | 2 | 5 | Referential |
| C2 | 4 | 5 | Referential |
| C3 | 2 | 10 | Referential |
| C4 | 4 | 10 | Referential |
| C5 | 2 | 5 | Cooperative |
| C6 | 4 | 5 | Competitive |

#### 2.4.4 Evaluation Benchmarks

- **COGS** (Kim & Linzen, 2020): Compositional generalization benchmark
- **SCAN** (Lake & Baroni, 2018): Systematic compositionality assessment
- **Custom displacement tasks**: Novel benchmark for non-present entity reference

#### 2.4.5 Statistical Analysis

**Sample Size**: $n = 25$ runs per condition (exceeding minimum $n = 20$ for power = 0.8)

**Primary Analysis**: Paired t-tests comparing pre/post training metrics
- Significance threshold: $\alpha = 0.05$ (one-tailed)
- Multiple comparison correction: Bonferroni ($\alpha_{adj} = 0.0125$ for 4 metrics)

**Effect Size**: Cohen's $d$ with target $d \geq 0.5$ (medium effect)

**Reporting**: Mean $\pm$ SD, 95% confidence intervals, effect sizes, p-values

### 2.5 Implementation Details

#### 2.5.1 Probing Classifier Architecture

Linear probes applied to layers $\{6, 12, 18, 24\}$ of LLaMA-7B:

$$f_\psi(h^{(l)}) = \text{softmax}(W h^{(l)} + b)$$

Training: 1000 steps, Adam optimizer, learning rate $10^{-3}$

#### 2.5.2 Compute Requirements

- Interactive training: ~100 GPU-hours per condition (A100 80GB)
- Probing and metric computation: ~20 GPU-hours per condition
- Total estimated compute: ~3000 GPU-hours

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Prediction P1 (Compositional Improvement)**: We expect CGS > 0.1 (normalized) for multi-agent training conditions, demonstrating that interactive training produces measurable compositional improvements exceeding the calibrated noise floor. Based on Rodriguez Luna et al.'s findings in smaller-scale systems, we anticipate effect sizes of $d \approx 0.6-0.8$.

**Prediction P2 (Grounding Enhancement)**: GAI improvements of >0.15 RSA correlation points, indicating that interactive grounding pressures strengthen symbol-referent binding in LLM representations.

**Prediction P3 (Transmission Efficiency)**: TES exceeding random baseline by >10 percentage points, demonstrating that improved language properties transfer to novel architectures—evidence of genuinely more structured representations rather than co-adaptation.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. CGS ≤ 0.1 across all training conditions
2. All four metrics show null results (no detectable changes)
3. Contrastive perturbation fails to establish stable noise floors

### 3.3 Scientific Impact

**Methodological Contribution**: C-DELA provides the first rigorous measurement framework for Language Gamification research. By establishing calibrated metrics with noise floors, the framework enables:
- Principled comparison of different interactive training approaches
- Detection of genuine representational improvements vs. behavioral artifacts
- Systematic investigation of which game properties drive language improvements

**Theoretical Contribution**: Results will clarify whether the compositionality gap in LLMs can be addressed through interactive training, bridging findings from small-scale emergent communication to large-scale language models.

### 3.4 Practical Impact

**For LLM Development**: If successful, C-DELA metrics can guide the design of more effective interactive training protocols, potentially addressing fundamental limitations in planning, reasoning, and generalization.

**For Evaluation Standards**: The framework establishes new standards for evaluating language properties beyond behavioral metrics, applicable to future interactive training research.

**For Multi-Agent Systems**: Insights into how language games improve LLM representations will inform the development of more effective multi-agent communication systems and embodied agents.

### 3.5 Limitations and Future Directions

**Limitations**:
- Results may be architecture-specific; generalization across model families requires additional validation
- Compute requirements limit the number of experimental conditions
- Metrics require representation access, excluding black-box API models

**Future Directions**:
- Extension to larger models (70B+) and different architectures
- Investigation of which specific game properties (competition, cooperation, population size) drive improvements
- Application to embodied agents and real-world interactive scenarios

This research establishes foundational measurement infrastructure for the emerging field of Language Gamification, enabling rigorous scientific investigation of how interactive training can address fundamental limitations in current LLM training paradigms.