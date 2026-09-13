# Research Proposal: Cross-Modal Binding Red Teaming: Exploiting Emergent Semantics in Multimodal LLMs Through Compositional Adversarial Attacks

## 1. Introduction

### 1.1 Background

The rapid proliferation of Multimodal Large Language Models (MLLMs) such as GPT-4V, LLaVA, and Gemini has transformed how artificial intelligence systems process and generate content across multiple modalities. These models demonstrate remarkable capabilities in understanding complex relationships between images, text, audio, and other input types, enabling applications ranging from visual question answering to multimodal content generation. However, this increased capability introduces novel safety and security challenges that existing defense mechanisms are ill-equipped to address.

Current safety architectures for MLLMs predominantly rely on modality-specific classifiers that evaluate inputs independently before they enter the model's processing pipeline. Image safety filters screen visual content for explicit or harmful imagery, while text toxicity detectors such as Perspective API evaluate textual inputs for offensive language. This compartmentalized approach to safety assumes that if individual inputs are safe, their combination will also produce safe outputs—an assumption that fundamentally misunderstands how multimodal models process information.

Recent empirical evidence challenges this assumption dramatically. The VLSU benchmark revealed that 34% of multimodal classification failures occur when individually-safe inputs combine to produce harmful outputs, despite each modality being correctly classified in isolation. This phenomenon parallels the McGurk Effect in cognitive science, where combining safe auditory and visual stimuli creates emergent perceptions absent in either input alone. Similarly, the SACRED-Bench evaluation demonstrated a 66% attack success rate for compositional audio attacks on Gemini 2.5 Pro, validating that compositional vulnerabilities represent a significant and exploitable attack surface.

The fundamental issue lies in cross-modal attention mechanisms—the architectural innovation that enables MLLMs to understand relationships between modalities. When visual and textual representations are combined through attention-based fusion, the resulting joint embedding can encode semantic content that exists in neither input independently. This emergent semantics creates a blind spot in current safety architectures: adversaries can craft input pairs that individually pass all safety checks but jointly trigger harmful model outputs.

### 1.2 Research Objectives

This research proposes Cross-Modal Binding Red Teaming (CBRT), a novel adversarial attack methodology designed to systematically exploit emergent semantics in attention-based multimodal fusion. Our primary objectives are:

1. **Develop and validate the CBRT attack methodology** that generates adversarial input pairs where each modality individually passes safety classifiers but their joint semantic embedding is optimized toward harmful targets.

2. **Quantify the compositional vulnerability** of state-of-the-art MLLMs by measuring Compositional Attack Success Rate (C-ASR) across multiple harm categories and model architectures.

3. **Establish the causal mechanism** by which cross-modal binding creates exploitable emergent semantics through systematic ablation studies and mechanistic analysis.

4. **Demonstrate the distinctiveness** of CBRT as an attack surface compared to existing multimodal attack methods, including single-modality jailbreaks and transfer-based attacks.

### 1.3 Research Significance

This research addresses a critical gap in AI safety evaluation. As MLLMs become increasingly deployed in high-stakes applications—healthcare diagnostics, autonomous systems, content moderation—understanding their compositional vulnerabilities becomes paramount. Our work contributes to the field in several ways:

**Theoretical Contribution:** We formalize the concept of compositional adversarial attacks that exploit emergent cross-modal semantics, providing a theoretical framework for understanding how individually-safe inputs can combine to produce harmful outputs.

**Practical Contribution:** By demonstrating that current modality-specific safety filters are fundamentally insufficient, we motivate the development of compositional safety classifiers that evaluate joint semantics rather than individual modalities.

**Methodological Contribution:** We introduce a dual-objective optimization framework that can be adapted for red teaming across different multimodal architectures and harm categories, providing practitioners with tools for comprehensive safety evaluation.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{M}$ denote a multimodal LLM that processes image input $x_v \in \mathcal{X}_v$ and text input $x_t \in \mathcal{X}_t$ to produce output $y = \mathcal{M}(x_v, x_t)$. Let $\mathcal{C}_v: \mathcal{X}_v \rightarrow \{0, 1\}$ and $\mathcal{C}_t: \mathcal{X}_t \rightarrow \{0, 1\}$ denote modality-specific safety classifiers, where 0 indicates "safe" and 1 indicates "unsafe."

The CBRT attack objective is to find perturbations $\delta_v$ and $\delta_t$ such that:

$$\begin{aligned}
&\text{maximize} \quad \mathcal{H}(\mathcal{M}(x_v + \delta_v, x_t + \delta_t)) \\
&\text{subject to} \quad \mathcal{C}_v(x_v + \delta_v) = 0 \\
&\phantom{\text{subject to}} \quad \mathcal{C}_t(x_t + \delta_t) = 0 \\
&\phantom{\text{subject to}} \quad \|\delta_v\|_\infty \leq \epsilon_v \\
&\phantom{\text{subject to}} \quad \|\delta_t\|_\infty \leq \epsilon_t
\end{aligned}$$

where $\mathcal{H}(\cdot)$ measures the harmfulness of the model output, and $\epsilon_v$, $\epsilon_t$ are perturbation budgets ensuring imperceptibility.

### 2.2 Dual-Objective Gradient Optimization

The core of CBRT is a dual-objective optimization procedure that simultaneously: (1) steers the joint cross-modal embedding toward harmful targets, and (2) maintains individual modality safety classification.

**Step 1: Target Embedding Construction**

For each harm category $h \in \{\text{weapon assembly}, \text{dangerous synthesis}, \text{harassment}\}$, we construct target embeddings $e_h^*$ by:

$$e_h^* = \frac{1}{|S_h|} \sum_{(x_v^{(i)}, x_t^{(i)}) \in S_h} f_{\text{joint}}(x_v^{(i)}, x_t^{(i)})$$

where $S_h$ is a seed set of known harmful input pairs and $f_{\text{joint}}$ extracts the joint embedding from the MLLM's cross-modal attention layers.

**Step 2: Dual-Objective Loss Function**

We define the composite loss function:

$$\mathcal{L}(\delta_v, \delta_t) = \underbrace{-\cos(f_{\text{joint}}(x_v + \delta_v, x_t + \delta_t), e_h^*)}_{\mathcal{L}_{\text{harm}}} + \lambda_1 \underbrace{\mathcal{L}_{\text{safe}}^v(\delta_v)}_{\text{image safety}} + \lambda_2 \underbrace{\mathcal{L}_{\text{safe}}^t(\delta_t)}_{\text{text safety}}$$

where:
- $\mathcal{L}_{\text{harm}}$ minimizes cosine distance to the harmful target embedding
- $\mathcal{L}_{\text{safe}}^v(\delta_v) = \max(0, \mathcal{C}_v^{\text{logit}}(x_v + \delta_v) - \tau_v)$ penalizes approaching the unsafe classification boundary
- $\mathcal{L}_{\text{safe}}^t(\delta_t) = \max(0, \mathcal{C}_t^{\text{logit}}(x_t + \delta_t) - \tau_t)$ similarly for text
- $\lambda_1, \lambda_2$ are balancing hyperparameters
- $\tau_v, \tau_t$ are safety margin thresholds

**Step 3: Projected Gradient Descent**

We optimize using Projected Gradient Descent (PGD) with alternating updates:

$$\delta_v^{(k+1)} = \Pi_{\epsilon_v}\left(\delta_v^{(k)} - \alpha_v \cdot \text{sign}\left(\nabla_{\delta_v} \mathcal{L}(\delta_v^{(k)}, \delta_t^{(k)})\right)\right)$$

$$\delta_t^{(k+1)} = \Pi_{\epsilon_t}\left(\delta_t^{(k)} - \alpha_t \cdot \text{sign}\left(\nabla_{\delta_t} \mathcal{L}(\delta_v^{(k+1)}, \delta_t^{(k)})\right)\right)$$

where $\Pi_\epsilon$ projects onto the $\ell_\infty$ ball of radius $\epsilon$, and $\alpha_v$, $\alpha_t$ are step sizes.

### 2.3 Data Collection and Attack Generation

**Seed Dataset Construction:**

We construct seed datasets for each harm category:
- **Weapon Assembly:** 50 image-text pairs depicting weapon components with assembly-related queries
- **Dangerous Synthesis:** 50 pairs showing chemical equipment with synthesis procedure queries
- **Targeted Harassment:** 50 pairs with personal images and harassment-enabling prompts

All seed pairs are verified to produce harmful outputs from undefended models, establishing ground truth for target embedding construction.

**Benign Input Selection:**

For attack generation, we select benign base inputs from:
- **Images:** COCO validation set, filtered to ensure $\mathcal{C}_v(x_v) = 0$
- **Text:** Alpaca instruction dataset, filtered to ensure $\mathcal{C}_t(x_t) = 0$

We generate 30 attack samples per harm category (90 total), satisfying our statistical power requirements.

### 2.4 Experimental Design

**Target Models:**
- LLaVA-1.5-7B (white-box, primary evaluation)
- GPT-4V (black-box, transferability evaluation)
- Gemini-1.5 Pro (black-box, transferability evaluation)

**Safety Classifiers:**
- Image: CLIP-based safety classifier (OpenAI moderation endpoint)
- Text: Perspective API toxicity detector

**Baseline Comparisons:**
1. **Single-modality jailbreak:** GPTFUZZER text-only attacks
2. **Transfer-based attack:** Alignment Curse methodology
3. **Dual-perturbation attack:** VLATTACK (without safety constraints)
4. **Random compositional pairing:** Randomly paired safe inputs (ablation)

**Evaluation Metrics:**

*Primary Metric - Compositional Attack Success Rate (C-ASR):*
$$\text{C-ASR} = \frac{|\{(x_v', x_t') : \mathcal{C}_v(x_v') = 0 \land \mathcal{C}_t(x_t') = 0 \land \mathcal{H}(\mathcal{M}(x_v', x_t')) = 1\}|}{|\text{Total attacks}|}$$

*Secondary Metrics:*
- Standard Attack Success Rate (ASR): Harmful output regardless of input classification
- Individual Safety Preservation Rate: Percentage of attacks maintaining safe classification
- Perturbation Imperceptibility: LPIPS score for images, semantic similarity for text

**Harm Evaluation Protocol:**

Model outputs are evaluated using GPT-4 as a judge with a standardized rubric:
- Score 1-5 for harmfulness (5 = explicit harmful content)
- Binary classification: harmful if score ≥ 4
- Inter-rater reliability verified with human annotators on 10% sample

### 2.5 Statistical Analysis Plan

**Primary Hypothesis Test:**

$H_0$: C-ASR $\leq$ 34% (natural compositional failure baseline)
$H_1$: C-ASR $>$ 34%

Test: One-sample t-test with $\alpha = 0.05$ (one-tailed)
Required effect size: Cohen's $d > 0.5$
Sample size: $n = 90$ (30 per harm category)

**Multiple Testing Correction:**

Bonferroni correction for 3 harm categories: adjusted $\alpha = 0.017$

**Reporting:**

All results reported as: Mean ± Standard Deviation, 95% Confidence Interval, Cohen's $d$, $p$-value

### 2.6 Ablation Studies

To establish the causal mechanism, we conduct three ablation studies:

**Ablation 1: Optimization Necessity**
Compare CBRT against random compositional pairing of safe inputs to verify that dual-objective optimization provides benefit beyond chance combinations.

**Ablation 2: Cross-Modal Attention Analysis**
Visualize attention patterns for successful attacks to confirm that cross-modal binding creates emergent semantic representations distinct from individual modality representations.

**Ablation 3: Constraint Relaxation**
Progressively relax safety constraints ($\lambda_1, \lambda_2 \rightarrow 0$) to measure the trade-off between individual safety preservation and attack success.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence, we anticipate the following outcomes:

**Primary Prediction (P1):** CBRT attacks will achieve C-ASR > 50% on LLaVA-1.5-7B, significantly exceeding the 34% natural compositional failure baseline ($p < 0.05$, Cohen's $d > 0.5$). This prediction is grounded in SACRED-Bench's demonstration of 66% ASR for compositional audio attacks, suggesting that optimization-based compositional attacks can substantially exceed natural failure rates.

**Secondary Prediction (P2):** Greater than 95% of successful CBRT attacks will maintain individual modality safety classification, validating that our dual-objective optimization successfully satisfies both constraints simultaneously.

**Secondary Prediction (P3):** CBRT will demonstrate qualitative distinctiveness from baseline attacks—specifically, CBRT inputs will pass individual safety filters while baseline attack inputs (GPTFUZZER, Alignment Curse) will not, establishing CBRT as a novel attack surface.

**Transferability Prediction:** White-box attacks generated on LLaVA-1.5-7B will transfer to GPT-4V and Gemini-1.5 Pro with reduced but non-trivial success rates (estimated 25-35% C-ASR), demonstrating that compositional vulnerabilities are architectural rather than model-specific.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. C-ASR ≤ 40% (not meaningfully better than natural failures)
2. Less than 80% of successful attacks maintain individually-safe inputs
3. Ablation shows no difference between optimized CBRT and random pairing
4. CBRT C-ASR is not significantly different from baseline attacks

### 3.3 Scientific Impact

This research will advance the field of AI safety in several dimensions:

**Theoretical Understanding:** By formalizing compositional adversarial attacks and demonstrating their effectiveness, we establish that emergent cross-modal semantics represent a fundamental vulnerability in attention-based multimodal fusion. This challenges the implicit assumption underlying current safety architectures that modality-independent safety evaluation is sufficient.

**Benchmark Contribution:** Our attack methodology and evaluation framework can be incorporated into red teaming benchmarks, providing practitioners with tools to assess compositional vulnerabilities in new MLLM deployments.

**Defense Motivation:** Demonstrating that C-ASR significantly exceeds natural compositional failure rates provides strong motivation for developing compositional safety classifiers that evaluate joint semantics. We will release our attack code and evaluation framework to facilitate defense research.

### 3.4 Practical Impact

**Industry Implications:** Organizations deploying MLLMs in production must recognize that modality-specific safety filters provide incomplete protection. Our findings will inform the development of more robust safety architectures that evaluate cross-modal interactions.

**Policy Implications:** As regulatory frameworks for AI safety evolve, our research demonstrates the need for evaluation standards that assess compositional vulnerabilities, not just individual modality safety.

**Responsible Disclosure:** We will follow responsible disclosure practices, notifying affected model providers (OpenAI, Google) of specific vulnerabilities before public release, allowing time for mitigation development.

### 3.5 Limitations and Future Work

**Current Limitations:**
- White-box access required for attack generation limits immediate applicability to closed-source models
- Evaluation focused on three harm categories; broader coverage needed
- Perturbation imperceptibility constraints may limit attack effectiveness in some scenarios

**Future Directions:**
- Extend CBRT to audio-visual and audio-text modality combinations
- Develop black-box variants using query-based optimization
- Design and evaluate compositional safety classifiers as defenses
- Investigate whether similar vulnerabilities exist in other multimodal architectures (e.g., late fusion models)

This research represents a critical step toward understanding and mitigating the compositional vulnerabilities inherent in multimodal AI systems, ultimately contributing to the development of safer and more trustworthy generative AI.