# Research Proposal: Cognitive Stress Testing: Evaluating LLM Reasoning Under Adversarial Perturbations Inspired by Human Cognitive Biases

## 1. Introduction

### Background

Large Language Models (LLMs) have demonstrated remarkable capabilities across diverse tasks, from machine translation to complex reasoning problems. These achievements have sparked debates about whether LLMs possess genuine cognitive abilities or merely sophisticated pattern matching. A critical question emerges: do these models reason in ways that parallel human cognition, or do they employ fundamentally different computational strategies that happen to produce similar outputs?

Human cognition, despite its sophistication, exhibits systematic errors known as cognitive biases—predictable deviations from rational judgment documented extensively in psychological research. These biases, including anchoring effects, framing effects, confirmation bias, and base-rate neglect, reveal the heuristic nature of human reasoning and define its boundaries. Understanding whether LLMs share these vulnerabilities, or exhibit entirely different failure patterns, offers a unique window into the fundamental nature of machine "reasoning."

Current evaluation paradigms face significant limitations. Static benchmarks suffer from potential data contamination during training, and many assessments fail to probe the robustness of reasoning under perturbation. Recent surveys confirm that LLMs exhibit cognitive biases (Malberg et al., 2024; Sumita et al., 2024), but systematic investigation of how these biases manifest under adversarial conditions—and how they compare to documented human behavioral patterns—remains nascent.

### Research Objectives

This research proposes the development of a **Cognitive Bias Probe Suite (CBPS)**, a dynamic evaluation framework designed to:

1. **Systematically assess** LLM vulnerability to adversarial perturbations inspired by human cognitive biases across multiple reasoning domains.
2. **Compare failure patterns** between LLMs and documented human behavioral data to characterize shared versus divergent reasoning mechanisms.
3. **Develop a taxonomy** of LLM cognitive vulnerabilities that distinguishes human-like heuristic failures from machine-specific brittleness patterns.
4. **Create a contamination-resistant** evaluation methodology through procedural generation of novel test instances.

### Significance

This research bridges cognitive psychology and AI evaluation, addressing central questions posed by the workshop: Where do LLMs stand on cognitive tasks? What are their fundamental limits? The proposed framework offers both theoretical insights—illuminating what reasoning mechanisms LLMs may have learned—and practical implications for AI safety by identifying predictable failure conditions. By establishing rigorous methods to probe cognitive abilities, this work contributes to improving benchmarks and evaluation methods, a key workshop topic.

## 2. Methodology

### 2.1 Research Design Overview

The CBPS framework comprises four interconnected components: (1) bias paradigm selection and formalization, (2) adversarial perturbation generation, (3) systematic evaluation protocol, and (4) comparative analysis with human behavioral data.

### 2.2 Bias Paradigm Selection and Formalization

We select ten well-documented cognitive biases from psychological literature, organized into three categories:

**Reasoning Biases:**
- *Confirmation Bias*: Tendency to favor information confirming prior beliefs
- *Base-Rate Neglect*: Ignoring prior probabilities when presented with specific information
- *Belief Bias*: Evaluating arguments based on conclusion believability rather than logical validity

**Judgment Biases:**
- *Anchoring Effect*: Over-reliance on initial information when making estimates
- *Framing Effect*: Different decisions based on how information is presented
- *Availability Heuristic*: Judging probability by ease of recall

**Decision Biases:**
- *Sunk Cost Fallacy*: Continuing investment based on past costs rather than future benefits
- *Status Quo Bias*: Preference for current state over change
- *Decoy Effect*: Preference shifts when asymmetrically dominated options are introduced
- *Loss Aversion*: Weighing losses more heavily than equivalent gains

For each bias $b \in B$, we formalize the expected deviation from rational response:

$$\Delta_b = f_{\text{biased}}(x, c) - f_{\text{rational}}(x)$$

where $x$ represents the core problem information, $c$ represents bias-triggering context, and $f$ denotes the response function.

### 2.3 Adversarial Perturbation Generation

We develop a procedural generation system that creates task variants through systematic perturbations. For each bias paradigm, we define:

**Base Task Template** $T_b$: A parameterized problem structure capturing the essential reasoning challenge.

**Perturbation Functions** $P = \{p_1, p_2, ..., p_k\}$: Transformations that introduce bias-triggering elements while preserving the underlying logical structure.

The generation process follows:

$$T'_b = P_i(T_b, \theta)$$

where $\theta$ represents perturbation parameters (e.g., anchor values, frame polarity, irrelevant context magnitude).

**Example: Anchoring Effect Perturbation**

Base task: "Estimate the population of City X given the following facts: [relevant demographic data]"

Perturbation function $p_{\text{anchor}}$:
$$T'_{\text{anchor}} = \text{Prepend}(T_b, \text{"A random number generator produced: } a \text{"})$$

where $a \in \{a_{\text{low}}, a_{\text{high}}\}$ represents high or low anchors designed to influence estimates.

**Perturbation Intensity Scaling:**

For each perturbation type, we define intensity levels $\lambda \in [0, 1]$:

$$p_i(T_b, \theta, \lambda) = (1-\lambda) \cdot T_b + \lambda \cdot p_i(T_b, \theta)$$

This allows graduated stress testing from subtle to extreme perturbations.

### 2.4 Evaluation Protocol

**Models Under Evaluation:**
We evaluate a diverse set of LLMs including GPT-4, GPT-3.5, Claude-3, Llama-2 (70B, 13B), Mistral, and Gemini Pro, representing different architectures, scales, and training approaches.

**Task Administration:**

For each bias paradigm $b$ and model $m$:

1. **Baseline Assessment**: Administer $N=100$ unperturbed base tasks to establish baseline reasoning accuracy $A_{\text{base}}(m, b)$.

2. **Perturbation Testing**: For each perturbation type $p_i$ and intensity $\lambda_j$:
   - Generate $N=100$ perturbed variants
   - Record model responses $R_{m,b,p_i,\lambda_j}$
   - Calculate perturbed accuracy $A_{\text{perturbed}}(m, b, p_i, \lambda_j)$

3. **Bias Susceptibility Score (BSS)**:

$$\text{BSS}(m, b, p_i) = \frac{1}{|\Lambda|} \sum_{\lambda \in \Lambda} \frac{A_{\text{base}}(m, b) - A_{\text{perturbed}}(m, b, p_i, \lambda)}{A_{\text{base}}(m, b)}$$

4. **Response Pattern Analysis**: Beyond accuracy, we analyze response distributions to detect systematic biases:

$$\text{Bias Direction Score} = \mathbb{E}[R_{\text{high anchor}}] - \mathbb{E}[R_{\text{low anchor}}]$$

**Prompting Variations:**

Each task is administered under multiple prompting conditions:
- Zero-shot direct questioning
- Zero-shot with chain-of-thought instruction
- Few-shot with unbiased examples
- Few-shot with biased examples (to test bias amplification)

### 2.5 Human Behavioral Data Comparison

We compile a reference database of human behavioral results from:

1. **Meta-analyses** of psychological studies for each bias paradigm
2. **Replication studies** providing effect sizes with confidence intervals
3. **Original data collection** ($N=500$ participants via Prolific) on a subset of our generated tasks to ensure direct comparability

**Comparison Metrics:**

1. **Effect Size Correlation**: Spearman correlation $\rho$ between human and LLM bias effect sizes across paradigms.

2. **Failure Mode Similarity Index (FMSI)**:

$$\text{FMSI}(m) = \frac{|\mathcal{F}_m \cap \mathcal{F}_h|}{|\mathcal{F}_m \cup \mathcal{F}_h|}$$

where $\mathcal{F}_m$ and $\mathcal{F}_h$ represent sets of failure conditions for model $m$ and humans, respectively.

3. **Divergence Detection**: Tasks where LLM and human responses differ significantly ($p < 0.01$, Bonferroni corrected) are flagged for qualitative analysis.

### 2.6 Robustness and Contamination Prevention

To ensure evaluation validity:

1. **Procedural Generation**: All tasks are generated programmatically with randomized surface features (names, numbers, contexts) while preserving logical structure.

2. **Temporal Novelty**: The generation system produces previously unseen combinations, resistant to training data memorization.

3. **Structural Consistency Check**: We verify that perturbations preserve problem solvability through human validation ($N=50$ per paradigm).

4. **Statistical Validity**: We employ bootstrap confidence intervals and multiple comparison corrections for all statistical tests.

### 2.7 Experimental Timeline

- **Months 1-2**: Formalize bias paradigms, develop perturbation functions, build generation pipeline
- **Months 3-4**: Pilot testing, human behavioral data collection, generation system refinement
- **Months 5-6**: Full-scale LLM evaluation across all models and conditions
- **Months 7-8**: Comparative analysis, taxonomy development, manuscript preparation

## 3. Expected Outcomes & Impact

### 3.1 Primary Deliverables

1. **Cognitive Bias Probe Suite (CBPS)**: An open-source benchmark comprising:
   - 10 bias paradigms with 1,000+ generated instances each
   - Perturbation generation code enabling unlimited novel instances
   - Standardized evaluation protocols and scoring implementations

2. **Taxonomy of LLM Cognitive Vulnerabilities**: A systematic classification distinguishing:
   - *Human-parallel biases*: Failures that mirror human cognitive limitations, suggesting shared heuristic processing
   - *Human-divergent biases*: LLM-specific failure patterns revealing fundamentally different processing mechanisms
   - *Robustness asymmetries*: Tasks where LLMs outperform or underperform human baselines

3. **Empirical Findings Database**: Comprehensive results for all evaluated models, enabling longitudinal tracking as new models emerge.

### 3.2 Scientific Contributions

**To Cognitive Science:**
Our results will illuminate whether LLMs have learned reasoning strategies that approximate human heuristics through exposure to human-generated text. Strong human-LLM correlations would suggest that text exposure induces human-like cognitive shortcuts, while divergence would indicate fundamentally different computational strategies producing surface-similar outputs.

**To AI/ML Research:**
The framework provides actionable diagnostics for model developers, identifying specific failure conditions predictable from cognitive science literature. This enables targeted improvements in training procedures or architectural designs.

**To AI Safety:**
By cataloging predictable failure modes, we contribute to the broader goal of reliable AI systems. Understanding when LLMs will exhibit systematic errors allows for appropriate deployment constraints and human oversight protocols.

### 3.3 Broader Impact

This research directly addresses multiple workshop themes:

- **Fundamental limits of LLMs**: Our taxonomy characterizes the boundaries of LLM reasoning under adversarial conditions inspired by cognitive science.
- **Improving benchmarks**: CBPS provides a contamination-resistant evaluation methodology that probes genuine reasoning rather than memorization.
- **Similarities and differences with human cognition**: Our comparative framework enables precise characterization of human-LLM cognitive alignment.

The procedural generation approach ensures ongoing relevance as new models emerge, providing the research community with a sustainable evaluation infrastructure. By bridging cognitive psychology and AI evaluation, this work exemplifies the interdisciplinary collaboration essential for understanding where LLMs stand in the landscape of intelligent systems.

### 3.4 Limitations and Future Directions

We acknowledge that cognitive biases represent only one dimension of cognitive ability. Future extensions could incorporate biases in perception, memory, and social reasoning. Additionally, multimodal extensions testing whether visual-language models exhibit similar or different vulnerability patterns would address the workshop's interest in multimodal approaches to cognitive tasks.