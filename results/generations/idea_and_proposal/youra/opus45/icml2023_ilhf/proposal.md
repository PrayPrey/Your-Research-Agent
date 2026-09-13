# Research Proposal: Homeostatic Interaction-Grounded Learning for Non-Stationary Implicit Human Feedback

## 1. Introduction

### 1.1 Background

Interactive machine learning systems that learn from end-users are becoming increasingly prevalent across domains including assistive robotics, adaptive interfaces, personalized education, and healthcare applications. Traditional approaches to interactive learning rely on explicit human feedback in the form of scalar rewards, preference rankings, or demonstrations. However, humans naturally communicate through a rich repertoire of implicit signals—eye gaze patterns, facial expressions, electroencephalographic (EEG) responses, gestures, and physiological markers—that convey evaluative information without requiring deliberate annotation effort.

Interaction-Grounded Learning (IGL) has emerged as a promising paradigm for leveraging such implicit feedback signals. Unlike standard reinforcement learning that assumes access to a well-defined reward function, IGL operates under the assumption that the agent receives only implicit feedback signals whose relationship to the underlying reward is initially unknown. The agent must simultaneously learn to decode the feedback-reward mapping while optimizing its policy—a challenging chicken-and-egg problem that requires careful algorithmic design.

A critical limitation of existing IGL methods is their assumption of stationarity: the mapping between implicit feedback signals and underlying human preferences is presumed to remain constant throughout interaction. This assumption fundamentally conflicts with the reality of human-machine interaction. Human preferences naturally evolve due to learning effects, fatigue, changing goals, mood variations, and contextual factors. When a user's internal reward function drifts, the previously learned decoder becomes misaligned, causing the agent's policy to optimize for outdated preferences. This misalignment can lead to catastrophic performance degradation, user frustration, and ultimately system abandonment.

### 1.2 Research Objectives

This research proposes **Homeostatic Interaction-Grounded Learning (H-IGL)**, a principled framework for maintaining effective policy performance under non-stationary implicit human feedback. Our primary objectives are:

1. **Develop a drift detection mechanism** using Bayesian Online Change-Point Detection (BOCPD) that monitors the implicit feedback distribution to identify preference shifts with controlled false-positive rates (<5%).

2. **Design a homeostatic regulation system** that modulates decoder adaptation rates, balancing stability during stationary periods with plasticity during detected preference shifts.

3. **Integrate knowledge preservation** through Elastic Weight Consolidation (EWC) to prevent catastrophic forgetting of previously learned preference structures during re-grounding.

4. **Validate the framework** through comprehensive experiments with synthetic drift injection on multimodal implicit feedback signals (EEG error-related potentials, eye gaze, facial expressions).

### 1.3 Research Significance

This research addresses a fundamental gap at the intersection of interactive machine learning, human-computer interaction, and cognitive science. The significance is threefold:

**Theoretical Contribution:** H-IGL extends the IGL framework to non-stationary settings, establishing theoretical foundations for when and how adaptation should occur. This advances our understanding of the minimal assumptions required for learning from arbitrary implicit feedback signals.

**Practical Impact:** Robust handling of preference drift enables deployment of implicit feedback systems in real-world settings where user preferences naturally evolve. This is critical for assistive technologies, personalized learning systems, and adaptive interfaces serving diverse user populations.

**Interdisciplinary Bridge:** By integrating concepts from Bayesian statistics (change-point detection), neuroscience (homeostatic regulation), and continual learning (elastic weight consolidation), this work demonstrates how insights from multiple disciplines can address challenges in interactive learning.

## 2. Methodology

### 2.1 Problem Formulation

We formalize the non-stationary IGL setting as follows. At each timestep $t$, the agent observes context $x_t \in \mathcal{X}$, takes action $a_t \in \mathcal{A}$, and receives implicit feedback signal $f_t \in \mathcal{F}$. The human's latent reward $r_t \in \{0, 1\}$ is never directly observed. The feedback-reward relationship is governed by a time-varying conditional distribution:

$$P_t(f | x, a, r) = P_{\theta_t}(f | r)$$

where $\theta_t$ represents the preference parameters at time $t$. We assume the IGL conditional independence property holds locally: $P(f | x, a, r) = P(f | r)$ between change-points. Preference drift manifests as discrete change-points $\{t_1, t_2, ..., t_K\}$ where $\theta_{t_k^-} \neq \theta_{t_k^+}$.

The agent maintains a decoder $D_\phi: \mathcal{F} \rightarrow [0, 1]$ that estimates $\hat{r}_t = D_\phi(f_t)$, and a policy $\pi_\psi: \mathcal{X} \rightarrow \Delta(\mathcal{A})$ that maximizes expected decoded reward. The objective is to maintain high cumulative reward despite preference drift:

$$\max_{\phi, \psi} \mathbb{E}\left[\sum_{t=1}^{T} r_t \cdot \mathbb{1}[\pi_\psi(x_t) = a_t^*]\right]$$

where $a_t^*$ is the optimal action under the current (unknown) preference structure.

### 2.2 H-IGL Framework Architecture

The H-IGL framework consists of three integrated components operating in a closed loop:

#### 2.2.1 Bayesian Online Change-Point Detection (BOCPD)

We employ BOCPD to monitor the distribution of decoded rewards for evidence of preference drift. Let $r_{1:t} = \{\hat{r}_1, ..., \hat{r}_t\}$ denote the sequence of decoded rewards. BOCPD maintains a posterior distribution over the run length $\ell_t$, representing the number of timesteps since the last change-point:

$$P(\ell_t | r_{1:t}) \propto \sum_{\ell_{t-1}} P(r_t | \ell_{t-1}, r_{(\ell_{t-1})}) \cdot P(\ell_t | \ell_{t-1}) \cdot P(\ell_{t-1} | r_{1:t-1})$$

The predictive distribution $P(r_t | \ell_{t-1}, r_{(\ell_{t-1})})$ is computed using a conjugate Beta-Bernoulli model:

$$P(r_t = 1 | \ell_{t-1}) = \frac{\alpha + \sum_{i=t-\ell_{t-1}}^{t-1} \hat{r}_i}{\alpha + \beta + \ell_{t-1}}$$

where $\alpha, \beta$ are prior hyperparameters. The change-point probability is:

$$P(\text{change-point at } t) = P(\ell_t = 0 | r_{1:t})$$

To control false positives, we require sustained evidence over $K$ consecutive timesteps:

$$\text{Detect drift at } t \iff \prod_{i=t-K+1}^{t} P(\ell_i = 0 | r_{1:i}) > \tau^K$$

where $\tau \in [0.5, 0.99]$ is the detection threshold and $K = 10$ provides the sustained evidence window.

#### 2.2.2 Homeostatic Regulation

Inspired by biological homeostatic mechanisms that maintain neural stability, we introduce a homeostatic regulator that controls decoder adaptation rates. The regulator maintains a set-point $\bar{\phi}$ representing the "expected" decoder parameters under stable preferences:

$$\bar{\phi}_{t+1} = \tau_h \cdot \bar{\phi}_t + (1 - \tau_h) \cdot \phi_t$$

where $\tau_h \in [0.9, 0.999]$ is the homeostatic time constant. The deviation from set-point is:

$$\delta_t = \|\phi_t - \bar{\phi}_t\|_2$$

The adaptation rate $\eta_t$ is modulated based on BOCPD detection and homeostatic deviation:

$$\eta_t = \eta_{\text{base}} \cdot \begin{cases} \gamma_{\text{stable}} & \text{if no drift detected and } \delta_t < \delta_{\text{thresh}} \\ \gamma_{\text{plastic}} & \text{if drift detected} \\ \gamma_{\text{restore}} \cdot (1 + \delta_t / \delta_{\text{thresh}}) & \text{otherwise} \end{cases}$$

where $\gamma_{\text{stable}} < 1 < \gamma_{\text{restore}} < \gamma_{\text{plastic}}$ control the stability-plasticity trade-off.

#### 2.2.3 Elastic Weight Consolidation (EWC)

To preserve knowledge of previous preference structures during re-grounding, we apply EWC regularization. After each detected change-point, we compute the Fisher information matrix $F$ for the decoder parameters:

$$F_{ij} = \mathbb{E}\left[\frac{\partial \log P(f | \phi)}{\partial \phi_i} \cdot \frac{\partial \log P(f | \phi)}{\partial \phi_j}\right]$$

The decoder update incorporates EWC regularization:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{IGL}}(\phi) + \frac{\lambda}{2} \sum_i F_i (\phi_i - \phi_i^*)^2$$

where $\phi^*$ represents the decoder parameters at the previous change-point and $\lambda \in [100, 10000]$ controls regularization strength.

### 2.3 Complete Algorithm

**Algorithm 1: Homeostatic Interaction-Grounded Learning (H-IGL)**

```
Input: Initial decoder φ₀, policy ψ₀, BOCPD threshold τ, window K, 
       homeostatic constant τ_h, EWC weight λ
Initialize: Set-point φ̄₀ ← φ₀, run-length posterior P(ℓ₀), Fisher F ← 0

For t = 1, 2, ..., T:
    1. Observe context x_t, take action a_t ~ π_ψ(x_t)
    2. Receive implicit feedback f_t
    3. Decode reward: r̂_t ← D_φ(f_t)
    
    4. BOCPD Update:
       - Update run-length posterior P(ℓ_t | r̂_{1:t})
       - Compute change-point probability P(ℓ_t = 0)
       - If sustained detection (K consecutive): drift_detected ← True
    
    5. Homeostatic Regulation:
       - Update set-point: φ̄_t ← τ_h · φ̄_{t-1} + (1-τ_h) · φ_{t-1}
       - Compute deviation: δ_t ← ||φ_t - φ̄_t||₂
       - Set adaptation rate η_t based on drift_detected and δ_t
    
    6. Decoder Update:
       - If drift_detected: Store φ* ← φ_t, Update Fisher F
       - Compute IGL loss: L_IGL(φ)
       - Compute EWC loss: L_EWC = (λ/2) Σᵢ Fᵢ(φᵢ - φᵢ*)²
       - Update: φ_{t+1} ← φ_t - η_t · ∇(L_IGL + L_EWC)
    
    7. Policy Update:
       - Update policy ψ using decoded rewards r̂_{1:t}

Return: Final decoder φ_T, policy ψ_T
```

### 2.4 Experimental Design

#### 2.4.1 Data Collection and Simulation

We conduct experiments using three implicit feedback modalities:

1. **EEG Error-Related Potentials (ErrPs):** Simulated based on the RLIHF framework, where ErrP signals indicate perceived errors in agent behavior. We model ErrPs as Gaussian distributions with modality-specific parameters that shift during preference drift.

2. **Eye Gaze Patterns:** Simulated fixation durations and saccade patterns indicating attention and interest. Preference drift manifests as changes in gaze-reward correlations.

3. **Facial Expressions:** Simulated valence scores from facial action units. Drift is modeled as threshold shifts in expression-reward mappings.

**Synthetic Drift Injection:** We inject two types of preference drift:
- **Abrupt drift:** Step change in feedback-reward mapping at specified episodes
- **Gradual drift:** Linear interpolation between preference structures at 0.1% change per episode

#### 2.4.2 Experimental Conditions

We evaluate H-IGL against four baseline conditions:

1. **Standard IGL:** No drift detection or adaptation mechanisms
2. **Sliding-Window IGL:** Decoder trained only on recent W=100 episodes
3. **Context-Reset IGL:** Periodic decoder reinitialization every 100 episodes
4. **H-IGL Ablations:**
   - H-IGL w/o BOCPD (random adaptation timing)
   - H-IGL w/o Homeostatic (fixed adaptation rate)
   - H-IGL w/o EWC (no knowledge preservation)

#### 2.4.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Recovery Rate | Cumulative reward ratio vs. stationary baseline within 100 episodes post-drift | >80% |
| Adaptation Latency | Episodes from drift to 80% performance recovery | <100 episodes |
| False Positive Rate | Proportion of detections when no true drift occurred | <5% |
| Knowledge Retention | Performance on pre-drift evaluation set after adaptation | >70% |
| Cumulative Reward | Total reward over 500-episode deployment | Maximize |

#### 2.4.4 Statistical Analysis

All experiments use $n = 20$ independent runs with different random seeds. We report:
- Mean and 95% confidence intervals for all metrics
- Paired t-tests comparing H-IGL to each baseline ($\alpha = 0.05$, one-tailed)
- Effect sizes using Cohen's d
- Ablation analysis isolating each component's contribution

### 2.5 Hyperparameter Selection

We conduct Bayesian optimization over the following hyperparameter ranges:

| Parameter | Range | Selection Criterion |
|-----------|-------|---------------------|
| BOCPD threshold $\tau$ | [0.5, 0.99] | Minimize detection latency subject to FPR < 5% |
| Sustained window $K$ | {5, 10, 15} | Trade-off between latency and false positives |
| Homeostatic constant $\tau_h$ | [0.9, 0.999] | Stability of set-point tracking |
| EWC weight $\lambda$ | [100, 10000] | Balance between plasticity and retention |

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** Under preference drift conditions, H-IGL will recover >80% of baseline IGL performance within 100 episodes, while standard IGL degrades to <50% without recovery. We expect this advantage to be statistically significant ($p < 0.05$) with large effect size (Cohen's $d > 0.8$).

**Secondary Predictions:**
- **P2:** H-IGL false positive rate will remain <5% under stationary conditions
- **P3:** H-IGL will achieve >15% higher cumulative reward than sliding-window and context-reset baselines under drift scenarios

**Ablation Expectations:**
- Removing BOCPD will cause delayed or missed adaptation, reducing recovery rate by >20%
- Removing homeostatic regulation will cause unstable adaptation, increasing variance by >50%
- Removing EWC will cause catastrophic forgetting, reducing knowledge retention by >30%

### 3.2 Theoretical Contributions

This research establishes theoretical foundations for non-stationary IGL:

1. **Drift Detectability Conditions:** We characterize the minimum distributional shift magnitude detectable by BOCPD given the implicit feedback noise level.

2. **Stability-Plasticity Trade-off:** We formalize the relationship between homeostatic parameters and adaptation dynamics, providing guidance for parameter selection.

3. **Knowledge Preservation Bounds:** We derive bounds on performance degradation during re-grounding as a function of EWC regularization strength.

### 3.3 Practical Impact

**Assistive Technologies:** H-IGL enables brain-computer interfaces and assistive robots to maintain effectiveness as users' abilities and preferences evolve over time, critical for long-term deployment.

**Personalized Learning:** Educational systems can adapt to students' changing knowledge states and learning preferences without requiring explicit re-calibration.

**Adaptive Interfaces:** User interfaces can continuously optimize for individual users whose interaction patterns naturally evolve, supporting ability-based design at scale.

### 3.4 Broader Impact

This research contributes to the workshop's core questions by:

1. Demonstrating how to learn from implicit feedback signals whose meanings may change over time
2. Providing principled mechanisms for accounting for non-stationary human preferences
3. Establishing minimal assumptions for learning from arbitrary feedback in non-stationary settings
4. Bridging HCI design principles with adaptive ML systems for diverse user populations

### 3.5 Limitations and Future Directions

**Known Limitations:**
- Requires ~100 episodes for homeostatic calibration, limiting applicability to very short interactions
- BOCPD memory scales $O(T)$; sliding window approximations needed for long deployments
- Current formulation assumes single-user settings; multi-user extension requires identity conditioning

**Future Directions:**
- Extension to multi-user settings with user-specific preference tracking
- Integration with large language model feedback for richer implicit signals
- Theoretical analysis of sample complexity under non-stationarity
- Real-world validation with human participants in assistive robotics applications

This research represents a significant step toward robust interactive learning systems that can maintain alignment with evolving human preferences, enabling deployment in real-world settings where user needs naturally change over time.