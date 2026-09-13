# Research Proposal: Adaptive Safety Boundaries for Personalized AI Agents in Sensitive Domains

## 1. Introduction

### Background

The rapid advancement of artificial intelligence has ushered in an era where AI systems are increasingly deployed in sensitive, high-stakes domains such as mental health support, medical consultation, legal advice, and personalized education. Simultaneously, the push toward personalization has intensified, with AI agents learning deeply about individual users to provide tailored experiences that maximize utility and engagement. This dual trajectory—toward both greater personalization and deployment in sensitive applications—creates a fundamental tension that current safety mechanisms are ill-equipped to address.

Traditional AI safety frameworks operate with static boundaries: fixed content filters, predetermined conversation limits, and context-blind intervention rules. While these approaches provide baseline protection, they fail to account for the dynamic nature of personalized interactions. A mental health chatbot that has accumulated extensive knowledge about a user's trauma history, coping mechanisms, and emotional triggers possesses information that enables both superior therapeutic support and potential harm vectors. The same personalization depth that allows the system to provide contextually appropriate interventions also creates risks of reinforcing harmful thought patterns, creating dangerous emotional dependencies, or being exploited by adversarial actors.

Recent research has begun addressing aspects of this challenge. EmoAgent (Qiu et al., 2025) demonstrates that emotionally engaging AI dialogues can lead to psychological deterioration in vulnerable users, while EmoGuard provides monitoring and corrective feedback mechanisms. HAICOSYSTEM (Zhou et al., 2024) offers a comprehensive framework for evaluating AI safety across operational, content, societal, and legal dimensions. The PENGUIN benchmark (Wu et al., 2025) establishes that incorporating personalized user information significantly improves safety scores, suggesting that personalization and safety need not be inherently opposed. AgentGuardian (Abaev et al., 2026) introduces context-aware access control policies that adapt based on learned legitimate behaviors.

However, these approaches address individual facets of the problem without providing an integrated framework that dynamically calibrates safety boundaries based on the interaction between personalization depth, domain sensitivity, and user vulnerability. This gap leaves personalized AI systems in sensitive domains operating with either overly restrictive safety measures that diminish utility or overly permissive boundaries that enable harm.

### Research Objectives

This research proposes **Context-Aware Safety Envelopes (CASE)**, a comprehensive framework for dynamically adjusting AI safety boundaries in personalized applications within sensitive domains. The primary objectives are:

1. To develop a formal model for quantifying the interaction between personalization depth, domain sensitivity, and user vulnerability indicators
2. To design a meta-learned safety controller that continuously calibrates intervention thresholds based on these three factors
3. To create synthetic training environments with annotated risk escalation trajectories for safe controller learning
4. To validate the framework across multiple sensitive domains, demonstrating improved safety outcomes without significant utility degradation

### Significance

This research addresses a critical gap in AI safety that will only widen as personalization technologies advance and AI systems penetrate deeper into sensitive applications. By providing adaptive safety mechanisms that respond to the unique risk profile of each user-context combination, CASE enables the responsible deployment of personalized AI in domains where the benefits are substantial but the risks are significant. The framework has implications for regulatory compliance, user trust, and the broader goal of ensuring AI systems enhance rather than compromise human wellbeing.

## 2. Methodology

### 2.1 Conceptual Framework

CASE operates on the principle that safety boundaries should be treated as dynamic, context-dependent envelopes rather than static thresholds. We formalize this through a three-dimensional risk space:

**Definition 1 (Risk State)**: At any time $t$, the risk state $R_t$ is defined as:

$$R_t = f(P_t, D, V_t)$$

where $P_t \in [0,1]$ represents personalization depth, $D \in [0,1]$ represents domain sensitivity (static for a given application), and $V_t \in [0,1]$ represents user vulnerability indicators.

**Personalization Depth ($P_t$)**: Quantifies the accumulated user-specific information in the system's context. We compute this as:

$$P_t = \sigma\left(\sum_{i=1}^{n} w_i \cdot \text{InfoGain}(u_i, t)\right)$$

where $u_i$ represents distinct user attributes learned, $\text{InfoGain}(u_i, t)$ measures the information accumulated about attribute $i$ by time $t$, $w_i$ weights attributes by their sensitivity, and $\sigma$ is a sigmoid normalization function.

**Domain Sensitivity ($D$)**: A predetermined score reflecting potential harm magnitude, incorporating factors such as irreversibility of outcomes, vulnerability of typical users, and regulatory requirements. For instance, $D_{\text{mental health}} > D_{\text{general assistant}}$.

**User Vulnerability Indicators ($V_t$)**: Real-time assessment of user susceptibility to harm, computed through:

$$V_t = \alpha V_{t-1} + (1-\alpha) \cdot \text{VulnDetect}(x_t, h_t)$$

where $\text{VulnDetect}$ is a learned function operating on current input $x_t$ and conversation history $h_t$, and $\alpha$ is a smoothing parameter to prevent oscillation.

### 2.2 Safety Envelope Architecture

The CASE framework consists of four interconnected components:

**Component 1: State Estimator Network**

A transformer-based encoder that processes conversation history and user profile to estimate $(P_t, V_t)$:

$$[P_t, V_t] = \text{StateEncoder}(\text{Concat}(h_t, \text{UserProfile}_t))$$

The encoder is trained on annotated conversation trajectories where human experts have labeled personalization accumulation and vulnerability signals.

**Component 2: Risk Aggregation Function**

We model the combined risk using a learned neural aggregator rather than a fixed formula, allowing the system to capture complex interactions:

$$\hat{R}_t = \text{RiskNet}(P_t, D, V_t; \theta_R)$$

where $\text{RiskNet}$ is a multilayer perceptron with parameters $\theta_R$, trained to predict expert-annotated risk levels.

**Component 3: Dynamic Safety Boundary Calculator**

Given the estimated risk $\hat{R}_t$, we compute adaptive safety boundaries across multiple dimensions:

$$B_t^{(k)} = B_{\text{base}}^{(k)} \cdot \exp(-\lambda_k \cdot \hat{R}_t)$$

where $B_t^{(k)}$ is the boundary for safety dimension $k$ (e.g., emotional intensity limits, topic restrictions, response latency requirements), $B_{\text{base}}^{(k)}$ is the baseline boundary for dimension $k$, and $\lambda_k$ is a sensitivity parameter learned per dimension.

**Component 4: Meta-Learned Safety Controller**

The safety controller is trained using constrained reinforcement learning to optimize the trade-off between utility and safety:

$$\max_{\pi} \mathbb{E}\left[\sum_{t=0}^{T} \gamma^t \cdot U(a_t, s_t)\right] \text{ subject to } \mathbb{E}\left[\sum_{t=0}^{T} C(a_t, s_t, B_t)\right] \leq \epsilon$$

where $U(a_t, s_t)$ is the utility function (user satisfaction, task completion), $C(a_t, s_t, B_t)$ is the constraint violation cost, and $\epsilon$ is the maximum allowable safety violation budget.

We employ Constrained Policy Optimization (CPO) with the following Lagrangian formulation:

$$\mathcal{L}(\pi, \mu) = \mathbb{E}_\pi\left[\sum_{t} \gamma^t U(a_t, s_t)\right] - \mu \left(\mathbb{E}_\pi\left[\sum_{t} C(a_t, s_t, B_t)\right] - \epsilon\right)$$

### 2.3 Training Data Generation

Given the scarcity of real-world data with annotated risk trajectories, we develop a synthetic data generation pipeline:

**Step 1: User Persona Generation**
We create diverse user personas spanning vulnerability levels, interaction patterns, and domain-specific characteristics using LLM-based generation with structured prompts and validation.

**Step 2: Trajectory Simulation**
Using a multi-agent simulation environment inspired by HAICOSYSTEM, we generate conversation trajectories where:
- A user agent (parameterized by persona) interacts with an AI assistant
- A risk annotator agent labels each turn with risk escalation indicators
- Trajectories include both natural escalation and adversarial probing scenarios

**Step 3: Expert Validation**
A subset of generated trajectories (approximately 15%) undergoes human expert review to validate annotations and calibrate the automatic annotation system.

### 2.4 Algorithmic Training Procedure

**Algorithm 1: CASE Training**

```
Input: Annotated trajectories T, base AI agent A, domain sensitivity D
Output: Trained CASE controller

1. Pre-train StateEncoder on trajectory data with MSE loss for (P_t, V_t) estimation
2. Pre-train RiskNet on expert-annotated risk labels
3. Initialize policy π randomly
4. For episode = 1 to N:
   a. Sample trajectory τ from T
   b. For each timestep t in τ:
      i. Compute state estimates: [P_t, V_t] = StateEncoder(h_t, profile)
      ii. Compute risk: R_t = RiskNet(P_t, D, V_t)
      iii. Compute boundaries: B_t = BoundaryCalc(R_t)
      iv. Select action a_t ~ π(s_t, B_t)
      v. Execute action, observe reward u_t and constraint cost c_t
   c. Update π using CPO with collected (s, a, u, c, B) tuples
5. Return trained StateEncoder, RiskNet, π
```

### 2.5 Experimental Design

**Domains**: We evaluate CASE across three sensitive application domains:
1. Mental health support chatbots
2. Medical information assistants
3. Financial advisory systems

**Baselines**:
- Static Safety Baseline: Fixed thresholds regardless of context
- EmoGuard-style Monitoring: Reactive intervention without adaptive boundaries
- AgentGuardian-style Access Control: Context-aware but not personalization-aware
- RAISE Framework: Planning-based personalized safety

**Evaluation Metrics**:

*Safety Metrics*:
- **Harm Incidence Rate (HIR)**: Percentage of interactions flagged as harmful by expert evaluators
- **Risk Escalation Prevention (REP)**: Proportion of potential escalation trajectories successfully mitigated
- **Vulnerability Exploitation Rate (VER)**: Success rate of adversarial probes exploiting personalization

*Utility Metrics*:
- **User Satisfaction Score (USS)**: Likert-scale ratings from simulated and real users
- **Task Completion Rate (TCR)**: Percentage of user goals successfully addressed
- **Personalization Quality Index (PQI)**: Measured relevance and tailoring of responses

*Efficiency Metrics*:
- **False Intervention Rate (FIR)**: Unnecessary safety interventions that reduce utility
- **Latency Overhead (LO)**: Additional response time introduced by CASE

**Experimental Protocol**:
1. **Simulation Experiments**: 10,000 synthetic conversations per domain with varying user personas and adversarial conditions
2. **Red Team Evaluation**: Expert adversarial testers attempt to exploit personalization for harmful outcomes
3. **Human User Study**: IRB-approved study with 200 participants interacting with mental health support chatbot (with appropriate safeguards and debriefing)

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following quantitative outcomes based on preliminary analysis and related work:

1. **Safety Improvement**: 40-60% reduction in Harm Incidence Rate compared to static safety baselines, with particularly strong improvements (>50%) in high-vulnerability user segments

2. **Maintained Utility**: Less than 10% degradation in User Satisfaction Scores compared to unconstrained personalized systems, significantly outperforming static safety approaches which typically show 25-35% utility degradation

3. **Adaptive Calibration**: Demonstrated correlation (ρ > 0.7) between CASE boundary adjustments and expert-assessed risk levels, validating the context-awareness of the system

4. **Adversarial Robustness**: At least 70% reduction in successful vulnerability exploitation attempts compared to systems without adaptive boundaries

### Theoretical Contributions

1. **Formal Framework**: The first comprehensive formalization of the personalization-safety trade-off as a dynamic, multi-dimensional optimization problem

2. **Risk Aggregation Model**: Novel methodology for combining personalization depth, domain sensitivity, and vulnerability indicators into actionable risk estimates

3. **Constrained Meta-Learning**: Extension of safe reinforcement learning to the meta-level control of AI safety boundaries

### Practical Impact

1. **Deployment Guidelines**: Concrete recommendations for implementing adaptive safety in production personalized AI systems

2. **Regulatory Alignment**: Framework compatible with emerging AI regulations (EU AI Act, FDA guidance on AI medical devices) that require risk-proportionate safety measures

3. **Open Resources**: Release of synthetic training data generation pipeline, benchmark scenarios, and evaluation toolkit to accelerate community research

### Broader Impact

This research contributes to the responsible advancement of personalized AI by demonstrating that deep personalization and robust safety need not be mutually exclusive. By enabling dynamic safety calibration, CASE allows AI systems to provide maximum benefit to users while maintaining appropriate protections—protections that strengthen precisely when users are most vulnerable. This paradigm shift from static to adaptive safety is essential as AI systems become more deeply integrated into sensitive aspects of human life.

The framework also addresses equity concerns: static safety boundaries often disadvantage users who would benefit most from personalization (e.g., those with complex mental health needs) by applying overly restrictive limits uniformly. CASE's adaptive approach enables appropriate access while maintaining protection, promoting more equitable AI deployment.

Finally, by providing transparent, interpretable safety boundary adjustments, CASE supports the broader goal of trustworthy AI, enabling users, developers, and regulators to understand why certain safety measures are applied in specific contexts.