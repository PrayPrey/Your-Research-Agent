# Research Proposal: POMDP-Based Epistemic State Tracking for Interpretable Theory of Mind in Large Language Models

## 1. Title

**POMDP-Based Epistemic State Tracking for Interpretable Theory of Mind in Large Language Models: A Neuro-Symbolic Framework for Trustworthy Human-AI Collaboration**

## 2. Introduction

### 2.1 Background

Theory of Mind (ToM)—the ability to reason about others' mental states including beliefs, goals, and intentions—is fundamental to human social cognition and effective communication. As artificial intelligence systems increasingly engage in complex human interactions across domains such as education, mental health support, collaborative planning, and customer service, the need for robust computational ToM capabilities has become critical.

Recent advances in Large Language Models (LLMs) have demonstrated impressive performance on ToM benchmarks, with models like GPT-4 achieving approximately 78% accuracy on ToMBench. However, these successes mask fundamental limitations: current LLMs perform ToM reasoning implicitly within opaque neural representations, making their mental state inferences uninterpretable, difficult to verify, and impossible to manually correct. This opacity creates serious barriers for deployment in high-stakes applications where transparency, accountability, and human oversight are essential.

The interpretability challenge is compounded by uncertainty quantification problems. Neural models typically produce overconfident predictions without calibrated probability distributions over mental states, preventing users from assessing inference reliability. Meanwhile, purely symbolic approaches to ToM (e.g., rule-based systems using epistemic logic) offer interpretability but lack the flexibility to handle natural language variation and provide no principled framework for representing uncertainty.

This research addresses a critical gap at the intersection of cognitive science, natural language processing, and human-AI interaction: **How can we build ToM systems that are simultaneously accurate, interpretable, and capable of representing belief uncertainty?** The robotics community has successfully addressed analogous challenges in physical state estimation through Partially Observable Markov Decision Processes (POMDPs), which have provided principled probabilistic frameworks for 30+ years. However, this mature methodology has never been systematically applied to dialogue-based mental state tracking in modern NLP systems.

### 2.2 Research Objectives

This research proposes a novel neuro-symbolic architecture that integrates an explicit **Epistemic State Tracker (EST)** based on POMDP formalism with fine-tuned LLMs. The primary objectives are:

1. **Formalize dialogue-based ToM as a POMDP**: Develop the first rigorous mathematical framework representing mental state inference in conversation as a partially observable stochastic process.

2. **Design and implement the EST module**: Create a particle filter-based belief tracking system that maintains probabilistic distributions over others' mental states (beliefs and goals) conditioned on dialogue observations.

3. **Develop neural observation models**: Train deep learning models to estimate P(utterance|mental_state), bridging symbolic state representations with natural language.

4. **Create EST-conditioned LLM fine-tuning protocols**: Develop systematic methods for teaching LLMs to utilize explicit belief distributions in response generation.

5. **Validate performance gains**: Demonstrate ≥5 percentage point accuracy improvements on established ToM benchmarks compared to baseline LLMs.

6. **Establish interpretability and calibration**: Achieve human interpretability ratings ≥4.0/5.0 and belief calibration with Expected Calibration Error (ECE) ≤0.15.

7. **Ensure computational feasibility**: Maintain computational overhead ≤2× base LLM latency for practical deployment.

### 2.3 Significance

This research makes several significant contributions across theoretical, methodological, and practical dimensions:

**Theoretical Contributions:**
- Provides the first POMDP formalization of dialogue-based Theory of Mind, establishing rigorous mathematical foundations for mental state tracking in conversation
- Bridges cognitive science Bayesian ToM models with production-scale NLP systems (7B+ parameter LLMs)
- Introduces principled uncertainty quantification for mental state inferences through calibrated probability distributions

**Methodological Contributions:**
- Demonstrates successful transfer of robotics POMDP frameworks (30+ years of development) to natural language processing
- Establishes neuro-symbolic architecture combining neural observation models with symbolic particle filter belief tracking
- Develops systematic protocols for EST-conditioned LLM fine-tuning

**Practical Contributions:**
- Enables interpretable and steerable ToM systems with human-readable belief distributions and manual override capabilities
- Provides modular design allowing independent optimization of EST and LLM components
- Creates benchmark-ready evaluation protocols applicable across multiple ToM datasets

The broader impact extends to critical application domains:
- **Education**: Tutoring systems that transparently track student knowledge states
- **Mental Health**: Support systems with interpretable reasoning about patient beliefs
- **Collaborative AI**: Assistants that explain their understanding of user goals
- **Human-AI Alignment**: Systems whose mental models can be inspected and corrected

By addressing the fundamental tension between neural flexibility and symbolic interpretability, this research advances the workshop's core themes of leveraging ToM for machine learning applications, promoting human-AI collaboration, and ensuring positive social impact through transparent, trustworthy AI systems.

## 3. Methodology

### 3.1 POMDP Formalization of Dialogue-Based ToM

We formalize Theory of Mind reasoning in dialogue as a Partially Observable Markov Decision Process defined by the tuple $\langle S, A, T, O, Z, R \rangle$:

**State Space ($S$):** The mental state of the target agent at turn $t$ is represented as:
$$s_t = \langle B_t, G_t \rangle$$

where $B_t = \{p_1, p_2, ..., p_n\}$ is a set of propositional beliefs (e.g., "user believes the meeting is at 3pm", "user knows the document location") and $G_t = \{g_1, g_2, ..., g_m\}$ is a set of goals (e.g., "user wants to reschedule", "user seeks information about X").

**Action Space ($A$):** Dialogue utterances produced by either the target agent or the AI system.

**Transition Model ($T$):** $P(s_{t+1}|s_t, a_t)$ represents how mental states evolve given actions. We model this as:
$$P(s_{t+1}|s_t, a_t) = P(B_{t+1}|B_t, a_t) \cdot P(G_{t+1}|G_t, a_t)$$

assuming conditional independence between belief and goal updates.

**Observation Space ($O$):** Natural language utterances from the dialogue.

**Observation Model ($Z$):** $P(o_t|s_t)$ represents the likelihood of observing utterance $o_t$ given mental state $s_t$. This is learned via neural networks (detailed in Section 3.3).

**Reward Function ($R$):** For ToM inference tasks, we define reward based on accuracy of mental state prediction and dialogue task success.

The key challenge is maintaining a **belief state** $b_t$ over mental states:
$$b_t(s) = P(s_t = s | o_{1:t}, a_{1:t-1})$$

This belief distribution is updated recursively via Bayes' rule:
$$b_{t+1}(s') \propto P(o_{t+1}|s') \sum_{s} P(s'|s, a_t) b_t(s)$$

### 3.2 Epistemic State Tracker Architecture

The EST module implements particle filtering to approximate the belief distribution $b_t(s)$ using $N$ weighted particles:

$$b_t(s) \approx \sum_{i=1}^{N} w_t^{(i)} \delta_{s_t^{(i)}}(s)$$

where $s_t^{(i)}$ is the $i$-th particle state and $w_t^{(i)}$ is its normalized weight.

**Algorithm 1: Particle Filter Update**

```
Input: Previous belief b_{t-1}, action a_t, observation o_{t+1}
Output: Updated belief b_t

1. // Prediction step
2. For i = 1 to N:
3.   Sample s_t^{(i)} ~ P(s_t | s_{t-1}^{(i)}, a_t)
4.
5. // Update step  
6. For i = 1 to N:
7.   w_t^{(i)} = P(o_{t+1} | s_t^{(i)})  // From observation model
8.
9. // Normalization
10. w_t^{(i)} = w_t^{(i)} / sum_j(w_t^{(j)})
11.
12. // Resampling (if ESS < threshold)
13. If ESS < 0.5 * N:
14.   Resample particles proportional to weights
15.   Reset weights to 1/N
16.
17. Return {(s_t^{(i)}, w_t^{(i)})}_{i=1}^N
```

The **Effective Sample Size (ESS)** is computed as:
$$ESS = \frac{1}{\sum_{i=1}^{N} (w_t^{(i)})^2}$$

We use $N = 500$ particles based on preliminary experiments showing diminishing returns beyond this threshold.

**Belief Summarization:** For LLM conditioning, we extract:
- **Most likely state**: $\hat{s}_t = \arg\max_s b_t(s)$
- **Marginal probabilities**: $P(p_j \in B_t) = \sum_{s: p_j \in s.B} b_t(s)$ for each proposition
- **Entropy**: $H(b_t) = -\sum_s b_t(s) \log b_t(s)$ as uncertainty measure

### 3.3 Neural Observation Model

The observation model $P(o_t|s_t)$ is learned using a variational approach. We parameterize it as:

$$P_\theta(o_t|s_t) = \text{Softmax}(f_\theta(s_t, o_t))$$

where $f_\theta$ is a neural network with parameters $\theta$.

**Architecture:** We employ a cross-encoder design:
1. **State Encoder**: Encode mental state $s_t$ as text: "Beliefs: [p1, p2, ...]. Goals: [g1, g2, ...]"
2. **Joint Encoding**: Pass concatenated [state_text, utterance] through RoBERTa-large
3. **Scoring Head**: Binary classification head outputting compatibility score

**Training Objective:** Given dataset $\mathcal{D} = \{(s_j, o_j^+, \{o_j^-\})\}$ with positive utterances $o^+$ and negative samples $o^-$:

$$\mathcal{L}(\theta) = -\sum_{j} \left[\log P_\theta(o_j^+|s_j) + \sum_{k} \log(1 - P_\theta(o_j^{-(k)}|s_j))\right]$$

**Data Collection:** We create training data through:
1. **Annotation**: Hire annotators to label mental states in existing dialogue datasets (DailyDialog, Persuasion for Good)
2. **Synthetic Generation**: Use GPT-4 to generate utterances conditioned on specified mental states
3. **Negative Sampling**: Sample utterances from different mental states as negatives

Target: 50,000 annotated (state, utterance) pairs with 5 negative samples each.

### 3.4 EST-Conditioned LLM Fine-tuning

We fine-tune a 7B parameter LLM (LLaMA-2-7B or Mistral-7B) to generate responses conditioned on EST outputs.

**Input Format:**
```
[CONTEXT] {dialogue_history}
[MENTAL_STATE] 
  Beliefs (confidence):
    - p1 (0.85)
    - p2 (0.62)
  Goals (confidence):
    - g1 (0.91)
  Uncertainty: {entropy_value}
[INSTRUCTION] Generate appropriate response.
```

**Training Data Construction:**
1. Run EST on training dialogues to generate belief trajectories
2. Create (context, EST_output, ground_truth_response) triples
3. Augment with counterfactual EST states to teach reliance on beliefs

**Fine-tuning Procedure:**
- **Base Model**: LLaMA-2-7B-Chat or Mistral-7B-Instruct
- **Method**: LoRA (Low-Rank Adaptation) with rank=16, α=32
- **Dataset Size**: 10,000 dialogues (≈80,000 turns)
- **Hyperparameters**: 
  - Learning rate: 2e-4 with cosine schedule
  - Batch size: 32 (gradient accumulation)
  - Epochs: 3
  - Max sequence length: 2048 tokens

**Loss Function:**
$$\mathcal{L}_{\text{LLM}} = \mathcal{L}_{\text{CE}} + \lambda \mathcal{L}_{\text{belief}}$$

where $\mathcal{L}_{\text{CE}}$ is standard cross-entropy and $\mathcal{L}_{\text{belief}}$ is an auxiliary loss encouraging attention to belief states:

$$\mathcal{L}_{\text{belief}} = -\sum_i \alpha_i \log P(\text{belief}_i | \text{context})$$

with $\alpha_i$ being attention weights on belief tokens.

### 3.5 Experimental Design

#### 3.5.1 Datasets and Benchmarks

**Primary Evaluation:**
- **ToMBench** (Chen et al., 2024): 2,860 samples covering 31 ToM abilities
- **FANToM** (Kim et al., 2023): Complex multi-turn scenarios
- **OpenToM**: Classic false-belief tasks

**Training Data:**
- **DailyDialog**: 13,000 multi-turn conversations
- **Persuasion for Good**: 1,017 persuasion dialogues
- **Synthetic Data**: 5,000 GPT-4 generated dialogues with mental state annotations

#### 3.5.2 Experimental Conditions

**Within-subjects factorial design (2×3):**
- **Factor 1 - EST Status**: EST-on vs. EST-off (baseline LLM)
- **Factor 2 - Particle Count**: 100, 500, 1000 particles

**Sample Size:** $n = 30$ scenarios per condition (total 180 scenarios), selected to achieve statistical power of 0.80 for detecting Cohen's $d = 0.5$ at $\alpha = 0.05$.

**Baseline Comparisons:**
1. **Pure LLM**: GPT-4, Claude 3.5, LLaMA-2-70B (zero-shot and few-shot)
2. **SymbolicToM** (Sclar et al., 2023): Rule-based epistemic reasoning
3. **AutoToM** (Gandhi et al., 2024): Bayesian inverse planning
4. **Agentic-ToM** (Sarangi et al., 2025): Function-guided prompting

#### 3.5.3 Evaluation Metrics

**Primary Metrics:**

1. **Accuracy**: Percentage of correct mental state predictions
   $$\text{Accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{s}_i = s_i^*]$$

2. **Expected Calibration Error (ECE)**: Measure of probability calibration
   $$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$
   where $B_m$ are bins of predictions grouped by confidence.

3. **Interpretability Score**: Human ratings (1-5 scale) on:
   - Clarity of mental state representations
   - Ease of understanding system reasoning
   - Ability to identify errors in reasoning
   
   Collected from $n = 30$ annotators per condition via Likert scale questionnaires.

4. **Computational Overhead**: 
   $$\text{Overhead} = \frac{\text{Latency}_{\text{EST-on}}}{\text{Latency}_{\text{baseline}}}$$

**Secondary Metrics:**

5. **F1 Score**: For individual belief and goal detection
6. **Effective Sample Size (ESS)**: Particle filter health metric
7. **Belief Entropy**: Uncertainty quantification over dialogue turns
8. **Human Preference**: Pairwise comparisons of system responses (30 annotators, 100 pairs)

#### 3.5.4 Statistical Analysis

**Hypothesis Testing:**

- **P1 (Primary)**: Paired t-test comparing EST-on vs. EST-off accuracy
  - $H_0$: $\mu_{\text{EST-on}} - \mu_{\text{EST-off}} \leq 0$
  - $H_1$: $\mu_{\text{EST-on}} - \mu_{\text{EST-off}} > 5\%$
  - Significance level: $\alpha = 0.05$

- **P2 (Particle Count)**: Repeated measures ANOVA across particle counts (100, 500, 1000)
  - Post-hoc: Tukey HSD for pairwise comparisons

- **P3 (Fine-tuning Effect)**: Paired t-test comparing fine-tuned vs. zero-shot with EST

- **P4 (Interpretability)**: Mann-Whitney U test (non-parametric) comparing interpretability ratings

- **P6 (Calibration)**: Bootstrap confidence intervals (1000 samples) for ECE

**Falsification Criteria:**
The hypothesis is considered refuted if:
1. P1 fails to show significant improvement ($p \geq 0.05$), OR
2. Computational overhead exceeds 3.0×, OR
3. Observation model training fails to converge (validation accuracy < 70%)

#### 3.5.5 Implementation Details

**Software Stack:**
- **Particle Filter**: Custom Python implementation with NumPy/JAX for GPU acceleration
- **Observation Model**: PyTorch with HuggingFace Transformers
- **LLM Fine-tuning**: HuggingFace PEFT library for LoRA
- **Evaluation**: Custom framework integrating existing benchmark code

**Hardware Requirements:**
- Training: 4× NVIDIA A100 (40GB) GPUs
- Inference: 1× NVIDIA A100 or 2× RTX 4090

**Reproducibility:**
- All code released under MIT license on GitHub
- Random seeds fixed across experiments
- Detailed hyperparameter logs with Weights & Biases
- Annotated datasets released (subject to privacy constraints)

### 3.6 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

1. **EST Component Ablation**:
   - Remove particle filter (use point estimates only)
   - Remove observation model (use rule-based state updates)
   - Remove belief summarization (provide raw particle distributions)

2. **LLM Conditioning Ablation**:
   - Provide EST output but don't fine-tune (zero-shot)
   - Fine-tune without EST augmentation
   - Vary EST information granularity (full beliefs vs. summaries)

3. **Architectural Variations**:
   - Alternative observation models (BERT, GPT-2, T5)
   - Different particle counts (50, 100, 500, 1000, 2000)
   - Resampling strategies (multinomial, systematic, residual)

Each ablation uses $n = 20$ scenarios with paired statistical tests against the full model.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

Based on our hypothesis and preliminary theoretical analysis, we anticipate the following quantitative outcomes:

**Performance Improvements:**
- **Primary (P1)**: EST-augmented system achieves **≥5 percentage points** higher accuracy than baseline LLM on ToMBench (e.g., 83% vs. 78%), with statistical significance $p < 0.05$
- **P2**: Particle count analysis reveals diminishing returns: 100→500 particles yields **≥3% gain**, while 500→1000 yields **≤1% gain**
- **P3**: Fine-tuned LLM with EST shows **≥10% higher accuracy** than zero-shot EST usage, demonstrating learned utilization of belief states

**Interpretability & Calibration:**
- **P4**: Human annotators rate EST interpretability at **≥4.0/5.0** compared to **≤2.0/5.0** for pure LLM approaches
- **P6**: Belief calibration achieves **ECE ≤ 0.15**, significantly better than typical neural model overconfidence (ECE ≈ 0.3-0.4)
- Qualitative analysis reveals human users can successfully identify and correct erroneous belief states in **≥80%** of cases

**Computational Feasibility:**
- **P5**: End-to-end latency overhead remains **≤2.0× baseline LLM**, enabling practical deployment
- GPU-accelerated particle filtering processes 500 particles in **<100ms** per turn
- Memory footprint increases by **≤500MB** for EST module

**Observation Model Performance:**
- Training converges to **≥70% validation accuracy** on mental state-utterance compatibility
- Cross-domain transfer (training on DailyDialog, testing on Persuasion for Good) maintains **≥65% accuracy**
- Effective Sample Size (ESS) remains **≥50%** of particle count after 20 dialogue turns

### 4.2 Scientific Impact

**Theoretical Contributions:**

This research establishes the first rigorous mathematical framework connecting POMDP-based belief tracking with neural language models for Theory of Mind. The formalization provides:

1. **Unified Framework**: Bridges 30+ years of robotics research on state estimation with modern NLP, creating cross-pollination opportunities
2. **Cognitive Grounding**: Connects computational models to Bayesian ToM theories from cognitive science (Baker et al., 2009; Rabinowitz et al., 2018)
3. **Uncertainty Quantification Theory**: Establishes principled foundations for representing epistemic uncertainty in mental state inference

The work opens new research directions:
- Extension to higher-order ToM (recursive beliefs: "I believe you believe...")
- Integration with affective ToM (emotion recognition)
- Multi-agent belief tracking with joint state spaces
- Active information gathering strategies for belief refinement

**Methodological Contributions:**

The neuro-symbolic architecture demonstrates:

1. **Modularity**: Independent optimization of symbolic reasoning (particle filter) and neural components (observation model, LLM) enables rapid iteration
2. **Transferability**: POMDP framework can be adapted to other NLP tasks requiring latent state tracking (e.g., user intent modeling, knowledge state tracking in education)
3. **Benchmark Protocol**: Comprehensive evaluation methodology applicable across ToM datasets, establishing standards for future research

Expected publications:
- 1 flagship paper at top-tier NLP venue (ACL, EMNLP, NAACL)
- 1 workshop paper at ToM 2025 workshop
- 1 cognitive science journal article (Cognitive Science, Topics in Cognitive Science)
- Open-source codebase with 500+ GitHub stars (projected)

### 4.3 Practical Impact

**Application Domains:**

1. **Education Technology**:
   - Intelligent tutoring systems that transparently track student knowledge states
   - Teachers can inspect and correct system beliefs about student understanding
   - Enables personalized interventions based on interpretable mental models
   - **Impact**: Improved learning outcomes through better-calibrated pedagogical decisions

2. **Mental Health Support**:
   - Conversational agents that explain their understanding of patient beliefs and goals
   - Clinicians can verify system interpretations before providing recommendations
   - Uncertainty quantification prevents overconfident suggestions in ambiguous situations
   - **Impact**: Safer deployment in high-stakes therapeutic contexts

3. **Collaborative AI Assistants**:
   - Project management tools that track team member goals and knowledge
   - Users can view and correct assistant's mental models of collaborators
   - Enables proactive assistance based on inferred needs
   - **Impact**: Enhanced productivity through better human-AI coordination

4. **Customer Service**:
   - Support chatbots that maintain interpretable models of customer issues and goals
   - Human agents can review belief states during escalations
   - Calibrated uncertainty triggers appropriate human handoffs
   - **Impact**: Improved customer satisfaction and reduced escalation costs

**Societal Impact:**

This research directly addresses critical challenges in trustworthy AI:

1. **Transparency**: Human-readable belief distributions enable users to understand AI reasoning, supporting informed consent and accountability

2. **Controllability**: Manual override capabilities allow users to correct erroneous beliefs, preventing cascading errors in high-stakes decisions

3. **Fairness**: Explicit mental state representations can be audited for biases (e.g., differential belief updating across demographic groups)

4. **Safety**: Calibrated uncertainty prevents overconfident actions when mental state inference is ambiguous

5. **Human Autonomy**: Interpretable systems empower users to make informed decisions about accepting AI suggestions

**Alignment with Workshop Themes:**

- **Leveraging ToM for ML Applications**: Demonstrates concrete improvements in NLP task performance through explicit ToM modeling
- **ToM for HCI/Human-AI Collaboration**: Enables new interaction paradigms based on transparent mental models
- **Social Impacts of ToM**: Addresses ethical deployment through interpretability and controllability
- **Cognitive Science Perspectives**: Grounds computational approach in Bayesian cognitive theories

### 4.4 Limitations and Future Work

**Known Limitations:**

1. **Scope**: Current approach focuses on first-order ToM in text-based English dialogue; extensions needed for:
   - Higher-order recursive beliefs
   - Multimodal inputs (vision, speech prosody)
   - Low-resource languages
   - Deceptive communication scenarios

2. **Scalability**: Particle filtering computational cost grows with state space complexity; future work should explore:
   - Variational inference alternatives
   - Hierarchical state representations
   - Amortized inference via neural networks

3. **Evaluation**: Benchmark datasets may not fully capture real-world ToM complexity; need:
   - Longitudinal studies in deployment settings
   - Diverse cultural contexts
   - Adversarial robustness testing

**Future Research Directions:**

1. **Theoretical Extensions**:
   - Formal analysis of POMDP approximation quality
   - Sample complexity bounds for observation model learning
   - Integration with game-theoretic models of strategic communication

2. **Methodological Innovations**:
   - End-to-end differentiable particle filtering
   - Active learning for efficient mental state annotation
   - Transfer learning across dialogue domains

3. **Application Expansions**:
   - Robotics integration for embodied ToM
   - Multi-party conversation tracking
   - Long-term relationship modeling (weeks/months)

### 4.5 Dissemination and Open Science

**Commitment to Reproducibility:**

- **Code Release**: Full implementation on GitHub with MIT license within 1 month of publication
- **Data Sharing**: Annotated datasets released (subject to privacy/licensing constraints)
- **Model Checkpoints**: Fine-tuned models on HuggingFace Hub
- **Documentation**: Comprehensive tutorials and API documentation
- **Experiment Tracking**: Public Weights & Biases project with all hyperparameters

**Community Engagement:**

- Workshop presentation at ToM 2025
- Tutorial at major NLP conference (ACL/EMNLP)
- Blog posts and video explanations for broader audiences
- Collaboration invitations for extension to new domains

**Expected Timeline:**

- **Months 1-3**: Observation model development and training
- **Months 4-6**: EST implementation and integration
- **Months 7-9**: LLM fine-tuning and initial experiments
- **Months 10-12**: Comprehensive evaluation and ablations
- **Months 13-15**: Paper writing and revision
- **Month 16**: Workshop presentation and code release

This research represents a significant step toward trustworthy AI systems that can reason about human mental states in transparent, controllable, and probabilistically-grounded ways. By bridging robotics, cognitive science, and modern NLP, we aim to establish new foundations for human-AI collaboration in high-stakes domains where interpretability and reliability are paramount.