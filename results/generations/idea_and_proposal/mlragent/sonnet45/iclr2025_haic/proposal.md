# Research Proposal: Measuring and Mitigating Temporal Bias Drift in Longitudinal Human-AI Decision-Making Systems

## 1. Title

**Measuring and Mitigating Temporal Bias Drift in Longitudinal Human-AI Decision-Making Systems: A Framework for Fair and Adaptive Human-AI Coevolution**

## 2. Introduction

### 2.1 Background

The proliferation of AI-assisted decision-making systems across critical societal domains—including healthcare, criminal justice, hiring, and financial services—has created unprecedented opportunities for enhancing human capabilities. However, these systems are increasingly deployed not as static tools but as adaptive agents that continuously learn from human feedback through mechanisms such as Reinforcement Learning from Human Feedback (RLHF), active learning, and online updates. This creates dynamic feedback loops where human decisions inform AI recommendations, which subsequently influence future human decisions, establishing a coevolutionary relationship between humans and AI systems.

Recent empirical evidence suggests that this coevolution can have unintended consequences. Beck et al. (2025) demonstrated that cognitive biases significantly affect how humans evaluate AI-generated suggestions, with task design influencing whether humans critically engage with or passively accept AI outputs. Zhang et al. (2025) revealed that human judgments of AI-generated content systematically drift over time, challenging the assumption of stable evaluation criteria. Most concerningly, these findings suggest that subtle biases—whether originating from human decision-makers or embedded in training data—may not remain static but can amplify, attenuate, or transform through repeated human-AI interactions.

Current approaches to bias detection and mitigation in AI systems predominantly adopt a "snapshot" paradigm, evaluating fairness metrics at discrete time points during development or deployment. This static perspective fails to capture the temporal dynamics inherent in human-AI coevolution, where biases constitute moving targets that evolve through feedback loops. For instance, an AI hiring system might initially exhibit gender parity, but if it learns from decisions made by human recruiters who gradually develop unconscious preferences influenced by AI suggestions, the system could develop amplified gender biases over extended deployment periods—a phenomenon we term "temporal bias drift."

### 2.2 Research Objectives

This research aims to develop a comprehensive framework for understanding, measuring, and mitigating temporal bias drift in longitudinal human-AI decision-making systems. Specifically, we pursue four primary objectives:

1. **Theoretical Framework Development**: Formalize the concept of temporal bias drift through mathematical models that characterize how decision biases evolve across multiple human-AI interaction cycles, distinguishing between amplification, attenuation, oscillation, and emergence patterns.

2. **Longitudinal Bias Metrics**: Design and validate novel time-series metrics that quantify bias trajectories, capturing not only the magnitude of bias at specific time points but also the rate, direction, and stability of bias evolution.

3. **Causal Attribution**: Develop counterfactual analysis techniques to isolate the specific contribution of human-AI coevolution to observed bias trajectories, distinguishing coevolutionary effects from external factors and natural temporal variations.

4. **Adaptive Intervention Mechanisms**: Create dynamic debiasing interventions that detect emerging bias patterns in real-time and introduce corrective signals into the feedback loop while preserving beneficial adaptations and maintaining system utility.

### 2.3 Significance

This research addresses a critical gap at the intersection of AI fairness, human-computer interaction, and long-term AI safety. The significance manifests across multiple dimensions:

**Theoretical Contributions**: By formalizing temporal bias drift within a rigorous mathematical framework, this work extends bias research from static to dynamic settings, providing new conceptual tools for understanding coevolutionary systems.

**Methodological Advances**: The proposed longitudinal bias metrics and counterfactual trajectory analysis techniques offer practical tools for researchers and practitioners to monitor fairness in deployed AI systems over extended periods.

**Societal Impact**: Given the deployment of AI systems in high-stakes domains affecting individual lives and societal structures, understanding and preventing bias amplification through feedback loops has direct implications for justice, equity, and human welfare.

**Alignment with Workshop Themes**: This research directly addresses multiple HAIC 2025 subject areas, including "Socio-Technological Bias, Norms, and Ethics," "Dynamic Feedback Loops in Socially Impactful Domains," and "Bidirectional Learning Beyond Performance Metrics," providing empirical and methodological contributions to the emerging field of human-AI coevolution.

## 3. Methodology

### 3.1 Overall Research Design

The research employs a mixed-methods approach combining theoretical modeling, algorithm development, controlled simulation studies, and real-world case studies. The methodology consists of four interconnected phases:

**Phase 1**: Mathematical formalization and metric development  
**Phase 2**: Counterfactual causal analysis framework  
**Phase 3**: Adaptive debiasing intervention design  
**Phase 4**: Empirical validation through simulations and case studies

### 3.2 Phase 1: Mathematical Formalization and Longitudinal Bias Metrics

#### 3.2.1 Temporal Bias Drift Model

We formalize human-AI coevolution as a discrete-time dynamical system. Let $t \in \{0, 1, 2, ..., T\}$ represent interaction cycles. At each time step:

- $D_t = \{(x_i, a_i, y_i)\}_{i=1}^{n_t}$ represents decisions made, where $x_i$ are input features, $a_i$ are sensitive attributes (e.g., race, gender), and $y_i$ are decision outcomes
- $\pi_t^{AI}(y|x, a)$ represents the AI system's recommendation policy
- $\pi_t^{H}(y|x, a, r)$ represents the human decision policy, where $r$ is the AI recommendation

The coevolutionary dynamics follow:

$$\pi_{t+1}^{AI} = \mathcal{U}(\pi_t^{AI}, D_t, \theta_t)$$

$$\pi_{t+1}^{H} = \mathcal{A}(\pi_t^{H}, \pi_t^{AI}, E_t)$$

where $\mathcal{U}$ is the AI update mechanism (e.g., gradient descent on human-labeled data), $\theta_t$ are learning hyperparameters, $\mathcal{A}$ represents human adaptation, and $E_t$ captures experiential learning effects.

#### 3.2.2 Bias Trajectory Metrics

We define temporal bias through multiple complementary metrics:

**1. Instantaneous Bias Function**: At each time $t$, we measure bias using demographic parity difference:

$$B_t(a, a') = |\mathbb{E}[\hat{y}_t | A=a] - \mathbb{E}[\hat{y}_t | A=a']|$$

where $\hat{y}_t$ represents the actual decision outcome and $A$ is the sensitive attribute.

**2. Bias Velocity**: The rate of bias change:

$$V_t = \frac{B_t - B_{t-1}}{\Delta t}$$

**3. Bias Acceleration**: The rate of change in bias velocity:

$$\mathcal{A}_t = \frac{V_t - V_{t-1}}{\Delta t}$$

**4. Cumulative Bias Drift**: Total bias accumulation:

$$\text{CBD}(T) = \int_0^T |B_t - B_0| \, dt \approx \sum_{t=1}^T |B_t - B_0|$$

**5. Temporal Bias Patterns**: We classify trajectories into four categories:
- **Amplification**: $V_t > 0$ consistently and $B_T > \tau \cdot B_0$ for threshold $\tau > 1$
- **Attenuation**: $V_t < 0$ consistently and $B_T < B_0 / \tau$
- **Oscillation**: $V_t$ changes sign frequently with $\text{Var}(B_t)$ exceeding threshold
- **Emergence**: $B_0 < \epsilon$ (negligible initial bias) but $B_T > \tau$ (significant final bias)

#### 3.2.3 Intersectional Temporal Analysis

We extend these metrics to capture intersectional bias drift across multiple protected attributes simultaneously. For attributes $A_1, A_2, ..., A_k$, we define:

$$B_t^{\text{int}}(\mathbf{a}, \mathbf{a}') = |\mathbb{E}[\hat{y}_t | \mathbf{A}=\mathbf{a}] - \mathbb{E}[\hat{y}_t | \mathbf{A}=\mathbf{a}']|$$

where $\mathbf{A} = (A_1, ..., A_k)$ represents intersectional identities.

### 3.3 Phase 2: Counterfactual Trajectory Analysis

To isolate the causal contribution of human-AI coevolution to bias drift, we develop a counterfactual framework based on potential outcomes.

#### 3.3.1 Causal Estimand

Define the treatment as presence of AI recommendations. The causal effect of AI intervention on bias trajectory is:

$$\Delta B_t = B_t^{(\text{AI})} - B_t^{(\text{noAI})}$$

where $B_t^{(\text{AI})}$ is the observed bias with AI and $B_t^{(\text{noAI})}$ is the counterfactual bias trajectory without AI influence.

#### 3.3.2 Estimation Strategy

Since we cannot observe both potential outcomes simultaneously, we employ three complementary approaches:

**1. Synthetic Control Method**: For time-series data, construct synthetic counterfactuals by:
- Identifying comparison units (decision contexts) without AI intervention
- Creating weighted combinations that match pre-intervention bias trajectories
- Estimating $\hat{B}_t^{(\text{noAI})}$ through the synthetic control

**2. Interrupted Time Series Analysis**: Model the bias trajectory using segmented regression:

$$B_t = \beta_0 + \beta_1 t + \beta_2 I(t \geq t_0) + \beta_3 (t - t_0) I(t \geq t_0) + \epsilon_t$$

where $t_0$ is the AI intervention time, $\beta_2$ captures immediate level change, and $\beta_3$ captures slope change.

**3. Agent-Based Simulation**: Develop computational models where we can directly manipulate AI presence:
- Implement cognitive models of human decision-making with and without AI recommendations
- Simulate thousands of trajectories under both conditions
- Estimate causal effects through direct comparison

### 3.4 Phase 3: Adaptive Debiasing Interventions

#### 3.4.1 Real-Time Bias Detection

Implement a monitoring system using sequential change-point detection:

$$\text{CUSUM}_t = \max(0, \text{CUSUM}_{t-1} + (B_t - B_{\text{target}} - \delta))$$

where an alarm triggers when $\text{CUSUM}_t > h$ for threshold $h$.

#### 3.4.2 Dynamic Recalibration Mechanism

When bias drift is detected, we introduce corrective interventions through three strategies:

**1. Preference Regularization**: Augment the AI learning objective with a temporal consistency term:

$$\mathcal{L}_t = \mathcal{L}_{\text{task}}(D_t) + \lambda_{\text{fair}} \mathcal{L}_{\text{fairness}}(D_t) + \lambda_{\text{drift}} \|\pi_t^{AI} - \pi_{\text{anchor}}^{AI}\|^2$$

where $\pi_{\text{anchor}}^{AI}$ represents a debiased reference policy.

**2. Counterfactual Data Augmentation**: Inject synthetic balanced examples into training data:
- Generate counterfactual instances by modifying sensitive attributes
- Ensure equal positive outcome rates across groups in augmented data
- Weight augmented examples proportionally to detected drift magnitude

**3. Human-in-the-Loop Feedback**: When significant drift is detected:
- Present decision-makers with bias analytics and trend visualizations
- Prompt reflection on decision patterns through structured feedback
- Provide calibrated examples highlighting potential biased decisions

#### 3.4.3 Multi-Objective Optimization

The debiasing intervention must balance fairness improvement against maintaining decision quality and preserving beneficial human learning. We formulate this as:

$$\min_{\theta} \mathbb{E}[-(U_t + \alpha F_t + \beta L_t)]$$

where:
- $U_t$ is utility (decision accuracy)
- $F_t$ is fairness (inverse of bias metrics)
- $L_t$ is human learning (improvement in human unaided performance)
- $\alpha, \beta$ are weighting hyperparameters

### 3.5 Phase 4: Empirical Validation

#### 3.5.1 Controlled Simulation Studies

**Design**: Develop agent-based simulations modeling three decision contexts:
1. **Hiring decisions**: 1000 simulated applicants per cycle, 50 cycles
2. **Loan approvals**: 2000 applications per cycle, 40 cycles
3. **Medical diagnoses**: 500 cases per cycle, 60 cycles

**Human Decision Models**: Implement bounded-rational agents with:
- Cognitive biases (confirmation bias, anchoring effect)
- Learning mechanisms (reinforcement, social learning)
- Individual variation in AI reliance

**AI Update Mechanisms**: Test multiple learning paradigms:
- Supervised learning with human labels
- Preference learning from implicit feedback
- Hybrid approaches

**Experimental Manipulations**:
- Initial bias levels: {none, low, moderate, high}
- AI update frequency: {every cycle, every 5 cycles, every 10 cycles}
- Human feedback quality: {noisy, moderate, high-quality}
- Intervention timing: {early detection, late detection, no intervention}

#### 3.5.2 Real-World Case Studies

**Domain 1: Content Moderation**
- Partner with social media platform (or use public datasets like Jigsaw)
- Track moderator decisions and AI recommendations over 6-month period
- 100+ human moderators, 10,000+ moderation decisions per week
- Sensitive attributes: political viewpoint, user demographics

**Domain 2: Clinical Decision Support**
- Collaborate with healthcare institution implementing AI diagnostic assistance
- Analyze diagnostic decisions for imaging interpretation (e.g., radiology)
- 50+ clinicians, 200+ cases per week, 3-month study
- Sensitive attributes: patient race, insurance status, socioeconomic indicators

**Data Collection**:
- Decision logs: timestamps, features, AI recommendations, human decisions, outcomes
- Surveys: AI trust, perceived usefulness, decision confidence (weekly)
- Qualitative interviews: decision-making processes, AI influence (monthly)

#### 3.5.3 Evaluation Metrics

**Primary Outcomes**:
1. **Bias Trajectory Characterization**: Proportion of trajectories showing amplification vs. attenuation vs. stability
2. **Intervention Effectiveness**: $\Delta\text{CBD} = \text{CBD}_{\text{control}} - \text{CBD}_{\text{intervention}}$
3. **Utility Preservation**: $\Delta\text{Acc} = \text{Accuracy}_{\text{intervention}} - \text{Accuracy}_{\text{control}}$

**Secondary Outcomes**:
1. Human learning: performance on AI-free test cases
2. Calibration: alignment between confidence and accuracy
3. Explainability: human understanding of AI reasoning

**Statistical Analysis**:
- Mixed-effects models accounting for individual variation
- Difference-in-differences estimation for causal effects
- Bayesian hierarchical models for uncertainty quantification
- Multiple testing correction (Benjamini-Hochberg) for metric families

## 4. Expected Outcomes & Impact

### 4.1 Theoretical Contributions

This research will produce the first comprehensive mathematical framework for temporal bias drift in human-AI coevolutionary systems. Expected theoretical advances include:

1. **Formalization of Coevolutionary Dynamics**: A rigorous mathematical characterization of how biases propagate and transform through feedback loops, establishing taxonomies of drift patterns (amplification, attenuation, oscillation, emergence) with formal definitions and predictive models.

2. **Causal Inference Framework**: Novel counterfactual reasoning techniques specifically designed for longitudinal human-AI interaction data, addressing unique challenges like time-varying confounding and reciprocal causation absent in traditional causal inference settings.

3. **Normative Principles**: Theoretical guidelines for "acceptable" bias evolution, distinguishing harmful drift from beneficial adaptations (e.g., systems learning to be more fair over time), informing ethical frameworks for long-term AI deployment.

### 4.2 Methodological Innovations

The research will deliver practical tools and techniques for measuring and managing temporal bias:

1. **Open-Source Software Package**: A Python library implementing all proposed longitudinal bias metrics, counterfactual analysis tools, and adaptive intervention mechanisms, facilitating adoption by researchers and practitioners.

2. **Validated Measurement Instruments**: Empirically validated metrics demonstrating reliability (test-retest consistency), construct validity (correlation with human fairness judgments), and sensitivity (ability to detect meaningful bias changes).

3. **Deployment Protocols**: Practical guidelines for implementing bias monitoring in production AI systems, including recommended measurement frequencies, alarm thresholds, and intervention triggers calibrated to specific domains.

### 4.3 Empirical Insights

Through simulation studies and real-world case studies, this research will provide evidence-based answers to critical questions:

1. **Prevalence and Magnitude**: How common is temporal bias drift in real-world human-AI systems? What magnitudes of drift occur over typical deployment periods?

2. **Risk Factors**: Which system characteristics (update frequency, feedback quality, initial bias levels) predict harmful drift patterns?

3. **Intervention Efficacy**: How effective are different debiasing strategies? What are the trade-offs between fairness improvement and utility preservation?

4. **Domain Specificity**: How do drift patterns differ across decision contexts (hiring vs. healthcare vs. content moderation)?

### 4.4 Practical Impact

The research outcomes will directly inform practice in multiple ways:

1. **Regulatory Compliance**: As AI regulations increasingly require ongoing bias monitoring (e.g., EU AI Act), this framework provides concrete implementation methods for compliance.

2. **System Design**: Findings will inform architectural choices in AI system design, such as optimal update frequencies and feedback mechanisms that minimize harmful drift.

3. **Organizational Policies**: Results will guide organizations deploying AI systems on when and how to intervene, balancing automation benefits with fairness risks.

### 4.5 Broader Societal Impact

Beyond immediate technical contributions, this research addresses fundamental challenges in human-AI coevolution:

1. **Long-Term AI Safety**: By demonstrating that fairness is not a one-time property but requires continuous maintenance, this work contributes to emerging paradigms of dynamic AI safety.

2. **Democratic AI Governance**: The framework enables transparency and accountability in AI systems affecting societal outcomes, empowering stakeholders to demand fairness over extended deployment periods.

3. **Equitable Technology Design**: By making temporal bias visible and measurable, this research provides tools for ensuring AI systems do not inadvertently amplify existing societal inequities through feedback loops.

4. **Interdisciplinary Bridge**: This work connects computer science, cognitive psychology, sociology, and ethics, fostering the interdisciplinary collaboration essential for responsible AI development—directly aligned with HAIC 2025's mission.

### 4.6 Future Research Directions

Expected outcomes will open multiple avenues for future investigation:

1. **Multi-Agent Coevolution**: Extending the framework to settings with multiple interacting AI systems and diverse human populations
2. **Positive Feedback Design**: Leveraging coevolution beneficially to create AI systems that actively promote fairness over time
3. **Transfer Learning**: Understanding how bias drift patterns transfer across domains and contexts
4. **Individual Differences**: Investigating how human cognitive traits and AI literacy moderate coevolutionary dynamics

This research will establish temporal bias drift as a fundamental consideration in AI system design and evaluation, shifting the paradigm from static fairness assessments to dynamic coevolutionary monitoring, ultimately contributing to more equitable and trustworthy human-AI partnerships in critical societal domains.