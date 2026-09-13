# Research Proposal: Regulatory Suppression Architecture: Immune-Inspired Continuous Modulation for Context-Aware LLM Safety

## 1. Introduction

### 1.1 Background

The rapid advancement of foundation models, particularly large language models (LLMs), has revolutionized natural language processing and enabled unprecedented capabilities in text generation, reasoning, and task completion. However, these powerful capabilities come with significant risks: LLMs can generate harmful content, perpetuate societal biases, and potentially enable malicious applications. Addressing these safety concerns while preserving model utility has become one of the most pressing challenges in AI research.

Current approaches to LLM safety intervention fall into two broad categories, each with fundamental limitations. The first category comprises binary safety mechanisms, exemplified by SafeSwitch (Han et al., 2025), which monitor internal model states and activate safety interventions when harmful intent is detected. While effective at blocking harmful content (achieving approximately 80% reduction), these binary approaches suffer from excessive over-refusal rates—SafeSwitch reports approximately 48% over-refusal on benign prompts, severely degrading user experience and model utility. The second category includes static steering methods, such as Category-wise Safety Steering (Bhattacharjee et al., 2024), which apply predetermined intervention strengths regardless of context. These methods lack the adaptability needed to distinguish between genuinely harmful requests and benign edge cases that superficially resemble harmful content.

This fundamental tradeoff between safety and utility mirrors a challenge elegantly solved by biological immune systems through regulatory T-cells (Tregs). In immunology, Tregs provide context-dependent suppression of immune responses, preventing autoimmune reactions (analogous to over-refusal) while maintaining the ability to respond to genuine threats. This biological mechanism achieves fine-grained, continuous modulation rather than binary activation, enabling the immune system to calibrate responses based on contextual signals.

### 1.2 Research Objectives

This research proposes the Regulatory Suppression Architecture (RSA), a novel framework that bridges the gap between binary safety switches and static steering methods by introducing learned, continuous, context-aware safety modulation. Our primary objectives are:

1. **Develop a Regulatory Head mechanism** that outputs continuous suppression strength $s(\text{context}) \in [0,1]$ to modulate pre-computed safety steering vectors during inference.

2. **Design a constrained reinforcement learning framework** that trains the Regulatory Head without requiring explicit safety labels, optimizing for both low harmful content rates and reduced over-refusal.

3. **Validate the hypothesis** that continuous modulation enables context-aware calibration that distinguishes true threats from benign edge cases, achieving over-refusal rates below 35% while maintaining harmful content blocking at or below 20%.

4. **Demonstrate practical deployability** with minimal parameter overhead (<6%) and computational efficiency suitable for real-world applications.

### 1.3 Significance

This research addresses a critical gap in foundation model safety by proposing a principled approach to the safety-utility tradeoff. The significance extends across multiple dimensions:

**Scientific Contribution:** RSA provides a novel theoretical framework connecting biological immune regulation principles to machine learning safety mechanisms, potentially opening new research directions in bio-inspired AI safety.

**Practical Impact:** By reducing over-refusal while maintaining safety, RSA enables more usable and trustworthy AI systems, directly addressing deployment barriers for safety-critical applications.

**Methodological Advancement:** The constrained RL training approach without explicit safety labels addresses the "data mirage" problem where ground-truth safety labels are expensive, subjective, and potentially biased.

**Workshop Relevance:** This work directly addresses the MINT workshop's focus on interventions, activation engineering, and parameter-efficient methods for improving foundation model controllability.

## 2. Methodology

### 2.1 Architecture Overview

The Regulatory Suppression Architecture operates through a four-step causal mechanism during inference:

**Step 1 - Context Extraction:** Extract safety-relevant context from intermediate LLM representations at layer $L$:
$$h_L = \text{LLM}_{\text{layers } 1:L}(x)$$
where $x$ is the input prompt and $h_L \in \mathbb{R}^d$ is the hidden state at layer $L$.

**Step 2 - Regulatory Processing:** Process the context embedding through the Regulatory Head to compute suppression strength:
$$s(\text{context}) = \sigma(W_2 \cdot \text{ReLU}(W_1 \cdot h_L + b_1) + b_2)$$
where $W_1 \in \mathbb{R}^{d_h \times d}$, $W_2 \in \mathbb{R}^{1 \times d_h}$, $d_h$ is the hidden dimension, and $\sigma$ is the sigmoid function ensuring $s \in [0,1]$.

**Step 3 - Modulation:** Scale the pre-computed safety steering vector by the suppression strength:
$$v_{\text{calibrated}} = (1 - s(\text{context})) \cdot v_{\text{safety}}$$
where $v_{\text{safety}} \in \mathbb{R}^d$ is the pre-computed safety steering vector. Note that $s=0$ applies full safety intervention while $s=1$ applies no intervention.

**Step 4 - Integration:** Integrate the calibrated intervention with base model outputs:
$$h'_L = h_L + \alpha \cdot v_{\text{calibrated}}$$
where $\alpha$ is a scaling hyperparameter. The modified hidden state $h'_L$ is then processed through remaining layers to generate the final response.

### 2.2 Safety Steering Vector Computation

Following Category-wise Safety Steering (Bhattacharjee et al., 2024), we pre-compute safety steering vectors using contrastive pairs:
$$v_{\text{safety}} = \frac{1}{N} \sum_{i=1}^{N} (h_L^{\text{safe}_i} - h_L^{\text{harmful}_i})$$
where $h_L^{\text{safe}_i}$ and $h_L^{\text{harmful}_i}$ are hidden states for matched safe and harmful prompt pairs. We compute category-specific vectors for different harm types (toxicity, violence, misinformation, etc.) and select the appropriate vector based on initial content classification.

### 2.3 Constrained Reinforcement Learning Training

The Regulatory Head is trained using constrained reinforcement learning to optimize the safety-utility tradeoff without explicit safety labels.

**State Space:** The state $s_t$ at timestep $t$ consists of the context embedding $h_L$ and any conversation history encoding.

**Action Space:** The action $a_t = s(\text{context}) \in [0,1]$ is the continuous suppression strength.

**Reward Function:** We define a composite reward:
$$R(s_t, a_t) = R_{\text{utility}}(s_t, a_t) - \lambda_1 \cdot R_{\text{harm}}(s_t, a_t) - \lambda_2 \cdot R_{\text{refusal}}(s_t, a_t)$$

where:
- $R_{\text{utility}}$ measures response quality using a learned reward model
- $R_{\text{harm}}$ is the output of a safety classifier (e.g., LlamaGuard) indicating harmful content probability
- $R_{\text{refusal}}$ penalizes unnecessary refusals on benign prompts
- $\lambda_1, \lambda_2$ are balancing hyperparameters

**Constrained Optimization:** We formulate the training as a constrained Markov Decision Process:
$$\max_{\theta} \mathbb{E}_{\pi_\theta}[R_{\text{utility}}]$$
$$\text{subject to: } \mathbb{E}_{\pi_\theta}[R_{\text{harm}}] \leq \epsilon_{\text{harm}}$$
$$\mathbb{E}_{\pi_\theta}[R_{\text{refusal}}] \leq \epsilon_{\text{refusal}}$$

where $\theta$ are the Regulatory Head parameters, $\epsilon_{\text{harm}} = 0.20$ and $\epsilon_{\text{refusal}} = 0.35$ are constraint thresholds.

**Algorithm:** We employ Constrained Policy Optimization (CPO) with the following update rule:
$$\theta_{k+1} = \arg\max_{\theta} \mathcal{L}(\theta, \theta_k) - \sum_i \nu_i \cdot g_i(\theta)$$
where $\mathcal{L}$ is the surrogate objective, $g_i$ are constraint violation terms, and $\nu_i$ are Lagrange multipliers updated via dual gradient ascent.

### 2.4 Data Collection and Datasets

**Training Data:**
- **Harmful prompts:** ToxicChat (10K samples), AdvBench (500 samples), HarmBench (400 samples)
- **Benign prompts:** Alpaca (52K samples), ShareGPT (50K samples)
- **Ambiguous/edge cases:** OR-Bench subset (10K samples) for calibration learning

**Evaluation Data:**
- **Over-refusal evaluation:** OR-Bench (80K prompts across 10 refusal categories)
- **Safety evaluation:** ToxicChat test set, SafetyBench, HarmBench
- **Utility evaluation:** MT-Bench, AlpacaEval

**Data Preprocessing:**
1. Filter duplicates and near-duplicates using MinHash
2. Balance harmful/benign ratio to 1:5 for training stability
3. Stratify by harm category for category-specific evaluation

### 2.5 Experimental Design

**Base Models:** Llama-3-8B-Instruct and Mistral-7B-Instruct-v0.2

**Baselines:**
1. **Base LLM:** Unmodified pretrained model
2. **SafeSwitch:** Binary safety activation based on internal state monitoring
3. **Category-wise Steering:** Static steering with fixed intervention strength
4. **Llama Guard:** External safety classifier with rejection

**Ablation Studies:**
1. **Layer selection:** Evaluate $L \in \{8, 12, 16, 20, 24\}$ for context extraction
2. **Regulatory Head architecture:** Compare MLP depths (1, 2, 3 layers) and hidden dimensions
3. **Training objective:** Compare constrained RL vs. supervised learning with pseudo-labels
4. **Modulation function:** Compare linear scaling vs. learned non-linear modulation

**Hyperparameters:**
- Learning rate: $\{1e-5, 3e-5, 1e-4\}$
- Hidden dimension $d_h$: $\{256, 512, 1024\}$
- Scaling factor $\alpha$: $\{0.5, 1.0, 2.0\}$
- Constraint thresholds: $\epsilon_{\text{harm}} = 0.20$, $\epsilon_{\text{refusal}} = 0.35$

### 2.6 Evaluation Metrics

**Primary Metrics:**

1. **Over-Refusal Rate (ORR):**
$$\text{ORR} = \frac{\text{Number of benign prompts refused}}{\text{Total benign prompts}} \times 100\%$$
Target: < 35%

2. **Harmful Content Rate (HCR):**
$$\text{HCR} = \frac{\text{Number of harmful prompts not blocked}}{\text{Total harmful prompts}} \times 100\%$$
Target: ≤ 20%

3. **Suppression Calibration:**
Spearman correlation $\rho$ between $s(\text{context})$ and human-judged safety relevance scores.
Target: $\rho > 0.6$

**Secondary Metrics:**

4. **Response Utility:** MT-Bench score (1-10 scale), Target: ≥ 7.0

5. **Parameter Overhead:**
$$\text{Overhead} = \frac{|\theta_{\text{Regulatory}}|}{|\theta_{\text{LLM}}|} \times 100\%$$
Target: < 6%

6. **Inference Latency:** Additional time per token generation

### 2.7 Statistical Analysis

**Sample Size Justification:** With $n = 1000$ prompts per condition, power analysis indicates 80% power to detect effect size $d = 0.25$ at $\alpha = 0.05$.

**Statistical Tests:**
- McNemar's test for comparing over-refusal and harmful content rates between RSA and baselines
- Spearman correlation for calibration analysis
- Paired t-test for utility comparison
- Bonferroni correction for multiple comparisons ($\alpha' = 0.0125$)

**Falsification Criteria:**
The hypothesis is falsified if:
1. Over-refusal rate ≥ 45% (no improvement over SafeSwitch)
2. Harmful content rate > 25% (safety regression)
3. Calibration $\rho < 0.3$ (mechanism failure)
4. MT-Bench score < 6.0 (utility collapse)

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** RSA will achieve over-refusal rate < 35% on OR-Bench while maintaining harmful content rate ≤ 20% on ToxicChat, representing a >25% relative improvement in over-refusal compared to SafeSwitch (48%) without safety degradation.

**Secondary Predictions:**
- **P2:** Suppression strength $s(\text{context})$ will correlate with human-judged safety relevance with Spearman $\rho > 0.6$, demonstrating meaningful context-aware calibration.
- **P3:** MT-Bench utility scores will remain ≥ 7.0/10, preserving response quality.
- **P4:** Parameter overhead will be ≤ 6%, enabling practical deployment.

### 3.2 Scientific Impact

This research contributes to multiple areas of foundation model research:

**Interpretability:** The learned suppression strength provides an interpretable signal indicating the model's assessment of safety relevance, enabling analysis of what contextual features drive safety decisions.

**Mechanistic Understanding:** By decomposing safety intervention into explicit steps (context extraction, regulatory processing, modulation, integration), RSA provides a framework for understanding how safety mechanisms interact with base model computations.

**Bio-inspired AI Safety:** The successful application of immune system principles to LLM safety opens new research directions exploring other biological regulatory mechanisms for AI alignment.

### 3.3 Practical Impact

**Deployment Readiness:** The minimal parameter overhead and inference-time operation make RSA suitable for production deployment without significant infrastructure changes.

**User Experience:** Reduced over-refusal directly improves user experience, addressing a major barrier to adoption of safety-enhanced models.

**Customizability:** The continuous modulation framework enables fine-grained control over safety-utility tradeoffs for different deployment contexts (e.g., stricter settings for child-facing applications, more permissive for research tools).

### 3.4 Limitations and Future Work

**Current Limitations:**
- Constrained RL training may be sensitive to hyperparameter choices
- Robustness to adversarial attacks requires separate evaluation
- Generalization to out-of-distribution harm categories needs validation

**Future Directions:**
1. Extension to multi-modal foundation models
2. Integration with certified robustness guarantees
3. Exploration of hierarchical regulatory mechanisms for complex safety taxonomies
4. Application to other alignment challenges beyond harmful content (e.g., truthfulness, privacy)

### 3.5 Resource Requirements

**Computational:** 4-8 A100 GPU-hours for training, standard inference hardware for evaluation
**Data:** Approximately 50K training prompts, 100K evaluation prompts
**Timeline:** 3-4 weeks for full experimental validation

In conclusion, the Regulatory Suppression Architecture offers a principled, bio-inspired approach to the fundamental safety-utility tradeoff in foundation models. By learning continuous, context-aware modulation rather than binary activation, RSA promises to significantly improve the practical deployability of safe AI systems while advancing our understanding of how to build controllable foundation models.