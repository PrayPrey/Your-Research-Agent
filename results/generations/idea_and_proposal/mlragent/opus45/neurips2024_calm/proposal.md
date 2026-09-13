# Research Proposal: Causal Intervention Probing: Discovering and Manipulating Causal Mechanisms in Large Language Model Representations

## 1. Introduction

### Background

Large language models (LLMs) have emerged as remarkably capable systems, demonstrating unprecedented performance across diverse tasks ranging from text generation to complex reasoning. Despite being trained on largely unstructured data using self-supervised objectives, these models exhibit emergent abilities that sometimes rival or exceed human experts. However, a fundamental question persists: *how* do these models internally represent and process information to achieve such capabilities? This question becomes particularly pressing when considering causal reasoning—a cornerstone of human cognition essential for understanding cause-and-effect relationships, predicting intervention outcomes, and making robust decisions.

Recent research has begun evaluating whether LLMs possess causal knowledge. Kıcıman et al. (2023) demonstrated that LLMs can generate correct causal arguments with high probability, while Cai et al. (2023) revealed their reliance on contextual information for causal reasoning. Liu et al. (2023) showed that code-trained LLMs exhibit enhanced causal reasoning due to explicit causal structures in programming languages. However, these studies primarily assess *what* LLMs know about causality rather than *where* and *how* this knowledge is encoded within their architectures.

This gap in understanding presents significant challenges for deploying LLMs in safety-critical applications. Without knowing which components encode causal reasoning, we cannot reliably diagnose failures, correct errors efficiently, or provide guarantees about model behavior under distribution shifts. The "black box" nature of these models undermines trustworthiness precisely where causal understanding matters most—healthcare diagnostics, policy evaluation, and scientific discovery.

### Research Objectives

This research proposes **Causal Intervention Probing (CIP)**, a novel framework designed to:

1. **Discover causal reasoning circuits**: Systematically identify which layers, attention heads, and representation subspaces encode specific causal concepts (e.g., confounder recognition, intervention prediction, counterfactual reasoning).

2. **Map representations to formal causal operations**: Establish correspondences between discovered neural circuits and operations in causal graphical models, including d-separation reasoning and do-calculus applications.

3. **Develop targeted editing mechanisms**: Create lightweight intervention methods that can correct identified causal reasoning failures without degrading general model capabilities.

4. **Characterize scaling effects**: Understand how causal reasoning mechanisms emerge and strengthen across model scales.

### Significance

This research addresses the critical "causality of large models" direction by opening the black box of LLM causal reasoning. The expected contributions include: (1) interpretable maps revealing how causal knowledge is organized within transformers, (2) practical tools for diagnosing and repairing causal reasoning errors, (3) theoretical insights connecting neural representations to formal causal semantics, and (4) enhanced trustworthiness for LLM deployment in high-stakes domains. By bridging mechanistic interpretability with causal inference, this work advances both our understanding of why large models work and our ability to improve their reliability.

## 2. Methodology

### 2.1 Overview

The CIP framework comprises three interconnected phases: (1) Causal Circuit Discovery through systematic interventions, (2) Structured Representation Analysis mapping circuits to causal operations, and (3) Targeted Editing for correcting identified failures. We detail each phase below.

### 2.2 Phase 1: Causal Circuit Discovery

#### 2.2.1 Task Suite Construction

We construct a comprehensive suite of causal reasoning tasks derived from formal causal inference operations:

- **Confounder Identification**: Given a narrative describing variables and their relationships, identify which variables act as confounders for a specified causal query.
- **Intervention Prediction**: Predict the effect of an intervention $do(X=x)$ on outcome $Y$ given a described causal structure.
- **Counterfactual Reasoning**: Answer counterfactual questions of the form "What would $Y$ have been if $X$ had been $x'$?"
- **Causal Direction Discrimination**: Determine whether $X \rightarrow Y$ or $Y \rightarrow X$ given observational descriptions.
- **Instrumental Variable Recognition**: Identify valid instrumental variables in described scenarios.

Each task includes controlled variations manipulating: (1) surface features (names, domains), (2) structural complexity (number of variables, path lengths), and (3) reasoning depth required.

#### 2.2.2 Interchange Intervention Methodology

We employ activation patching to identify causally relevant components. Let $M$ denote the LLM with layers $\{L_1, \ldots, L_N\}$, each containing attention heads $\{H_1^{(l)}, \ldots, H_K^{(l)}\}$ and MLP components. For input $x$ and alternative input $x'$ (a controlled variation), we define the interchange intervention:

$$\text{Patch}(M, x, x', C) = M(x; a_C \leftarrow a_C')$$

where $a_C$ denotes activations at component $C$, and $a_C'$ denotes activations from processing $x'$.

The causal effect of component $C$ on output $y$ is measured as:

$$\text{CE}(C) = \mathbb{E}_{x, x'}[\mathcal{L}(M(x), y) - \mathcal{L}(\text{Patch}(M, x, x', C), y)]$$

where $\mathcal{L}$ is the task-specific loss function. Components with high $|\text{CE}(C)|$ are identified as causally relevant.

#### 2.2.3 Circuit Identification Algorithm

**Algorithm 1: Causal Circuit Discovery**

```
Input: Model M, Task dataset D, Threshold τ
Output: Causal circuit C* for task

1. Initialize component_effects = {}
2. For each layer l in {1, ..., N}:
   a. For each attention head h in layer l:
      - Compute CE(H_h^(l)) over D using Eq. (1)
      - component_effects[H_h^(l)] = CE(H_h^(l))
   b. Compute CE(MLP^(l)) over D
   c. component_effects[MLP^(l)] = CE(MLP^(l))
3. Rank components by |CE|
4. C* = {C : |CE(C)| > τ}
5. Validate circuit sufficiency:
   - Compute performance with only C* active
   - Iterate threshold if necessary
6. Return C*
```

To address concerns raised by Grant et al. (2025) regarding divergent representations from interventions, we incorporate the Counterfactual Latent (CL) loss:

$$\mathcal{L}_{CL} = \mathbb{E}[\|a_C^{\text{patched}} - \mathcal{P}(a_C^{\text{natural}})\|^2]$$

where $\mathcal{P}$ projects patched activations onto the manifold of natural activations.

### 2.3 Phase 2: Structured Representation Analysis

#### 2.3.1 Causal Abstraction Mapping

We establish formal correspondences between discovered circuits and causal graphical model operations using causal abstraction theory. Define a high-level causal model $\mathcal{M}_H$ representing ideal causal reasoning (e.g., a Bayesian network implementing d-separation) and a low-level model $\mathcal{M}_L$ (the neural circuit).

An abstraction function $\alpha: \mathcal{M}_L \rightarrow \mathcal{M}_H$ is valid if interventions commute:

$$\alpha(do_L(x)) = do_H(\alpha(x))$$

We search for abstraction functions mapping circuit activations to causal graph variables using the interchange intervention interchange (IIT) framework:

$$\text{IIT-Score}(\alpha, C) = \mathbb{E}[\mathbf{1}[\alpha(\text{Patch}(M, x, x', C)) = do_H(\alpha(x), \alpha(x'))]]$$

#### 2.3.2 Representation Probing

For each identified circuit, we train linear probes to decode causal graph properties:

$$\hat{G} = W \cdot h_C + b$$

where $h_C$ are activations from circuit $C$, and $\hat{G}$ represents predicted graph properties (edges, d-separation sets, adjustment sets). Probe accuracy indicates how explicitly causal structure is encoded.

We additionally apply distributed alignment search (DAS) to identify linear subspaces encoding specific causal concepts:

$$v_{\text{concept}} = \arg\max_{\|v\|=1} \text{Corr}(v^\top h_C, \text{concept\_label})$$

### 2.4 Phase 3: Targeted Editing

#### 2.4.1 Steering Vector Construction

For identified causal concepts, we construct steering vectors that shift model behavior:

$$v_{\text{steer}} = \mathbb{E}[h_C | \text{correct reasoning}] - \mathbb{E}[h_C | \text{incorrect reasoning}]$$

During inference, we apply:

$$h_C' = h_C + \lambda \cdot v_{\text{steer}}$$

where $\lambda$ controls intervention strength.

#### 2.4.2 Lightweight Adapter Modules

We design LoRA-style adapters targeting identified circuits:

$$h_C' = h_C + B \cdot A \cdot h_C$$

where $A \in \mathbb{R}^{r \times d}$, $B \in \mathbb{R}^{d \times r}$, and $r \ll d$. Adapters are trained on causal reasoning correction tasks while freezing base model parameters.

#### 2.4.3 Correction Training Objective

$$\mathcal{L}_{\text{correct}} = \mathcal{L}_{\text{causal}}(M', D_{\text{causal}}) + \beta \cdot \mathcal{L}_{\text{preserve}}(M', D_{\text{general}})$$

where $\mathcal{L}_{\text{causal}}$ encourages correct causal reasoning, $\mathcal{L}_{\text{preserve}}$ maintains general capabilities, and $\beta$ balances these objectives.

### 2.5 Experimental Design

#### 2.5.1 Models

We evaluate across model families and scales:
- **GPT-2** (124M, 355M, 774M, 1.5B parameters)
- **LLaMA-2** (7B, 13B, 70B parameters)
- **Pythia** (70M to 12B parameters for scaling analysis)

#### 2.5.2 Datasets

- **CLADDER** (Jin et al., 2023): Benchmark covering three rungs of the causal ladder
- **CausalBench**: Our constructed benchmark with controlled structural variations
- **BIG-bench Causal Judgment**: Real-world causal reasoning scenarios
- **Custom Synthetic DAGs**: Procedurally generated graphs with known ground truth

#### 2.5.3 Evaluation Metrics

1. **Circuit Localization**:
   - Faithfulness: $\text{Faith} = \text{Corr}(\text{CE}(C), \Delta\text{Performance})$
   - Minimality: $|C^*| / |C_{\text{all}}|$

2. **Abstraction Quality**:
   - IIT-Score (intervention interchange accuracy)
   - Probe accuracy for causal graph properties

3. **Editing Effectiveness**:
   - Causal Reasoning Accuracy (pre/post intervention)
   - Causal Explanation Coherence (CEC) from Muhebwa & Osman (2025)
   - General capability retention (MMLU, HellaSwag scores)

4. **Generalization**:
   - Transfer accuracy to held-out causal reasoning tasks
   - Out-of-distribution robustness on novel graph structures

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Interpretable Circuit Maps**: We expect to identify distinct circuits for different causal operations—potentially finding that confounder reasoning localizes to specific attention patterns while intervention prediction relies on MLP layers. These maps will reveal whether causal knowledge is distributed or modular.

2. **Formal Abstraction Correspondences**: We anticipate discovering that certain circuits implement approximate versions of d-separation via attention masking patterns, providing theoretical grounding for LLM causal reasoning.

3. **Effective Targeted Corrections**: We expect steering vectors and adapters to improve causal reasoning accuracy by 15-25% on CLADDER while maintaining >95% of general capabilities, demonstrating that surgical interventions can outperform full fine-tuning for targeted improvements.

4. **Scaling Laws for Causal Circuits**: Analysis across model scales will characterize how causal reasoning mechanisms emerge, potentially revealing phase transitions in capability development.

### Broader Impact

This research advances multiple frontiers:

- **Trustworthy AI**: By enabling targeted diagnosis and repair of causal reasoning failures, CIP enhances LLM reliability for safety-critical applications in healthcare, policy, and scientific discovery.

- **Mechanistic Understanding**: The framework contributes fundamental insights into how transformer architectures represent structured knowledge, advancing interpretability science.

- **Efficient Improvement**: Targeted editing provides resource-efficient alternatives to full retraining, democratizing access to reliable causal reasoning capabilities.

- **Causal AI Integration**: By bridging neural representations and formal causal semantics, this work enables tighter integration between LLMs and classical causal inference methods, addressing the collaborative potential highlighted by Liu et al. (2025).

The CIP framework opens new avenues for understanding *why* large models work while providing practical tools for making them more trustworthy—directly addressing both foundational questions motivating research at the intersection of causality and large models.