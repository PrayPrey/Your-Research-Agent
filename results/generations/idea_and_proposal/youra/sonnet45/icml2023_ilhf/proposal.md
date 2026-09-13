# Research Proposal: Hierarchical Multimodal Interaction-Grounded Learning for Personalized Assistive Systems

## 1. Title

**Hierarchical Multimodal Interaction-Grounded Learning: Extending Reward Decoding to Natural Implicit Human Feedback for Personalized Assistive Technologies**

## 2. Introduction

### 2.1 Background

Interactive machine learning systems that learn from human feedback have become increasingly prevalent in real-world applications, from recommender systems to robotic assistants. Traditional approaches rely on explicit feedback mechanisms such as scalar rewards, preference rankings, or demonstrations. However, these explicit feedback paradigms impose significant cognitive burden on users and are particularly challenging for individuals with disabilities who may have limited ability to provide structured input through conventional interfaces.

Recent advances in Interaction-Grounded Learning (IGL) have demonstrated that reinforcement learning agents can learn from arbitrary feedback signals without pre-specified reward functions, provided certain identifiability conditions hold. The IGL framework introduced by Xie et al. (NeurIPS 2022) establishes that a reward decoder $\psi(y)$ can learn to map arbitrary feedback vectors $y$ to latent rewards $r^*$ under the conditional independence assumption: $P(y|a,x,r^*) = P(y|r^*)$, where $a$ represents actions and $x$ represents context. This theoretical foundation enables learning from diverse feedback modalities including natural language, physiological signals, and behavioral cues.

Simultaneously, research in human-computer interaction and cognitive neuroscience has revealed that humans naturally communicate intent and preferences through rich multimodal channels. During human-machine interaction, users simultaneously emit implicit signals through eye gaze patterns (fixations, saccades, pupil dilation), speech prosody (tone, pitch, speaking rate), facial expressions, gestures, and postural adjustments. Neuroscience research on multisensory integration demonstrates that the human brain hierarchically processes these modalities through specialized cortical regions (visual cortex for gaze, auditory cortex for speech) before integrating them in multisensory areas (superior colliculus, intraparietal cortex) to form coherent perceptual representations.

Despite these parallel advances, a critical gap exists: current IGL implementations process only single-modality feedback, while multimodal reinforcement learning from human feedback (RLHF) systems require explicit preference labels. This creates a fundamental limitation for assistive technologies serving users who communicate naturally through multiple implicit channels but cannot provide explicit structured feedback. For example, a wheelchair user with limited motor control may express navigation preferences through simultaneous gaze direction (looking toward desired paths), speech tone (calm voice indicating comfort, tense voice indicating concern), and head gestures (nodding approval, shaking disapproval). Existing systems cannot leverage this rich multimodal implicit feedback without imposing additional labeling burden.

### 2.2 Research Objectives

This research proposes to extend the IGL paradigm from single-modality to multimodal feedback spaces through a hierarchical architecture inspired by neuroscience principles of multisensory integration. The primary objectives are:

**Objective 1 (Theoretical Extension):** Establish identifiability conditions for reward decoders processing multimodal implicit feedback vectors $y_{multi} = [y_{eye}, y_{speech}, y_{gesture}]$, proving that the conditional independence assumption extends to high-dimensional heterogeneous feedback spaces when fusion mechanisms preserve reward-relevant information.

**Objective 2 (Architectural Innovation):** Design and implement a hierarchical multimodal IGL architecture combining: (a) modality-specific encoders for eye-tracking, speech prosody, and gesture recognition; (b) learnable temporal pooling to synchronize heterogeneous sampling rates (120Hz eye-tracking, 16kHz speech, 30fps gesture); (c) cross-modal attention fusion that adaptively weights modalities based on task context; and (d) uncertainty-aware reward decoding that quantifies confidence in decoded rewards.

**Objective 3 (Empirical Validation):** Demonstrate that multimodal IGL achieves significantly higher reward decoder accuracy (≥0.15 improvement in Pearson correlation with ground-truth human ratings) and policy success rates (≥10% absolute improvement) compared to single-modality IGL baselines across three assistive technology domains: wheelchair navigation, prosthetic control interfaces, and educational tutoring systems.

**Objective 4 (Mechanistic Understanding):** Validate that cross-modal attention learns context-dependent modality weighting (prioritizing gaze for visual tasks, speech for dialogue tasks, gestures for physical manipulation tasks) and that uncertainty quantification correctly identifies conflicting multimodal signals.

### 2.3 Research Significance

This research addresses fundamental challenges at the intersection of interactive machine learning, human-computer interaction, and assistive technologies:

**Scientific Significance:** The work extends IGL theory to multimodal spaces, providing the first formal treatment of reward identifiability from heterogeneous implicit feedback streams. By proving that conditional independence holds for multimodal vectors under appropriate fusion mechanisms, we generalize IGL's applicability to natural human communication scenarios. The hierarchical architecture translates neuroscience principles of multisensory integration into practical deep learning components, creating a bridge between cognitive science and machine learning.

**Methodological Significance:** The proposed cross-modal attention mechanism represents the first application of attention-based fusion to the IGL paradigm, enabling context-adaptive modality weighting. Learnable temporal pooling addresses the critical challenge of synchronizing signals with vastly different sampling rates (120Hz to 16kHz) while preserving reward-critical temporal patterns. Uncertainty-aware reward decoding provides a principled approach to handling conflicting multimodal signals, enabling safe exploration when feedback is ambiguous.

**Practical Significance:** For assistive technology applications, this research enables personalized learning from natural multimodal communication without explicit labeling burden. Specific impact areas include:

- **Wheelchair Navigation Systems:** Learning user preferences from gaze direction (desired paths), speech tone (comfort/concern), and head gestures (approval/disapproval) for individuals with limited motor control.
- **Prosthetic Control Interfaces:** Adapting to residual limb muscle signals, facial expressions, and vocal patterns for amputees, enabling more intuitive control.
- **Educational Software:** Personalizing to student attention (gaze patterns), frustration (speech prosody), and engagement (posture) without interrupting learning flow.

**Societal Significance:** By reducing the feedback burden on users with disabilities, this research advances accessibility and inclusion. The ability to learn from natural implicit signals democratizes access to adaptive AI systems for marginalized populations who cannot easily provide explicit structured feedback. This aligns with ability-based design principles from HCI, enabling AI systems to adapt to diverse human capabilities rather than requiring humans to adapt to rigid machine interfaces.

The expected outcomes include: (1) theoretical framework for multimodal IGL with formal identifiability guarantees; (2) open-source implementation of hierarchical multimodal IGL architecture; (3) empirical validation across three assistive technology domains with N=90 participants; (4) design guidelines for deploying multimodal implicit feedback systems in real-world assistive applications.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Multimodal IGL Formulation

We extend the IGL framework to multimodal feedback spaces. Let $\mathcal{S}$ be the state space, $\mathcal{A}$ the action space, and $\mathcal{M} = \{eye, speech, gesture\}$ the set of feedback modalities. At each timestep $t$, the agent observes state $s_t$, takes action $a_t$, and receives multimodal feedback:

$$y_t^{multi} = [y_t^{eye}, y_t^{speech}, y_t^{gesture}] \in \mathcal{Y}^{eye} \times \mathcal{Y}^{speech} \times \mathcal{Y}^{gesture}$$

where each $y_t^m$ is a high-dimensional vector from modality $m$'s feedback space.

**Extended Conditional Independence Assumption:** We assume that multimodal feedback is conditionally independent of actions and states given the latent reward:

$$P(y_t^{multi} | s_t, a_t, r_t^*) = P(y_t^{multi} | r_t^*)$$

where $r_t^* \in \mathbb{R}$ is the user's internal reward evaluation. This extends IGL's original assumption to multimodal vectors, positing that human implicit feedback reflects internal reward evaluation rather than direct response to state-action pairs.

**Reward Decoder Objective:** The multimodal reward decoder $\psi_\theta: \mathcal{Y}^{multi} \rightarrow \mathbb{R} \times \mathbb{R}^+$ maps fused feedback to reward estimate and uncertainty:

$$(\hat{r}_t, \sigma_t) = \psi_\theta(f_{fusion}(y_t^{multi}))$$

where $f_{fusion}$ is the cross-modal fusion function (detailed in Section 3.2.3). The decoder is trained to maximize correlation with ground-truth human reward ratings while minimizing uncertainty calibration error.

#### 3.1.2 Information-Theoretic Justification

For multimodal fusion to improve over single-modality baselines, the fused representation must preserve reward-relevant information:

$$I(f_{fusion}(y^{multi}); r^*) \geq \max_{m \in \mathcal{M}} I(y^m; r^*)$$

where $I(\cdot; \cdot)$ denotes mutual information. We hypothesize that cross-modal attention fusion satisfies this inequality because:

1. **Weighted Sum Preserves Information:** Attention weights $\alpha_m$ learned end-to-end with reward decoder optimize information preservation.
2. **Complementary Modalities:** Different modalities capture orthogonal aspects of reward (gaze → spatial intent, speech → valence, gesture → action preference).
3. **Redundancy Provides Robustness:** When modalities agree, redundancy reduces noise; when they conflict, uncertainty quantification flags ambiguity.

### 3.2 Hierarchical Multimodal IGL Architecture

The proposed architecture consists of five stages: modality-specific encoding, temporal pooling, cross-modal attention fusion, uncertainty-aware reward decoding, and policy learning.

#### 3.2.1 Modality-Specific Encoders

**Eye-Tracking Encoder ($E_{eye}$):** Processes raw gaze coordinates, fixation durations, saccade velocities, and pupil diameter. We use the pre-trained Gazelle model (fkryan/gazelle, CVPR 2025) fine-tuned on assistive technology datasets:

$$h_t^{eye} = E_{eye}([x_{gaze}, y_{gaze}, d_{fixation}, v_{saccade}, p_{pupil}]_t) \in \mathbb{R}^{d_{eye}}$$

where $d_{eye} = 256$ is the eye feature dimension. Input sampling rate: 120Hz.

**Speech Prosody Encoder ($E_{speech}$):** Extracts prosodic features (pitch, energy, speaking rate, voice quality) using wav2vec2 with prosody-specific fine-tuning:

$$h_t^{speech} = E_{speech}(\text{wav2vec2}(\text{audio}_t)) \in \mathbb{R}^{d_{speech}}$$

where $d_{speech} = 256$. Input sampling rate: 16kHz, processed in 50ms windows.

**Gesture Encoder ($E_{gesture}$):** Processes skeletal keypoints from depth camera using MediaPipe Holistic, followed by temporal convolutional network:

$$h_t^{gesture} = E_{gesture}(\text{MediaPipe}(\text{depth}_t)) \in \mathbb{R}^{d_{gesture}}$$

where $d_{gesture} = 256$. Input sampling rate: 30fps.

#### 3.2.2 Learnable Temporal Pooling

To synchronize heterogeneous sampling rates to a common timebase (30Hz for real-time control), we employ learnable temporal pooling with attention-based aggregation:

$$\tilde{h}_t^m = \sum_{i \in W_t^m} \beta_i^m h_i^m$$

where $W_t^m$ is the temporal window of raw samples from modality $m$ corresponding to timestep $t$, and $\beta_i^m$ are learned attention weights:

$$\beta_i^m = \frac{\exp(w_m^\top h_i^m)}{\sum_{j \in W_t^m} \exp(w_m^\top h_j^m)}$$

with learnable parameters $w_m \in \mathbb{R}^{d_m}$. This allows the model to adaptively weight temporally informative patterns (e.g., prioritizing fixation onsets over stable fixations for eye-tracking).

#### 3.2.3 Cross-Modal Attention Fusion

The synchronized modality features are fused using cross-modal attention:

$$z_t = \sum_{m \in \mathcal{M}} \alpha_t^m \tilde{h}_t^m$$

where attention weights are computed via:

$$\alpha_t^m = \frac{\exp(Q_m^\top \tanh(K_m \tilde{h}_t^m + C_t))}{\sum_{m' \in \mathcal{M}} \exp(Q_{m'}^\top \tanh(K_{m'} \tilde{h}_t^{m'} + C_t))}$$

Here, $Q_m \in \mathbb{R}^{d_k}$, $K_m \in \mathbb{R}^{d_k \times d_m}$ are learnable parameters, and $C_t \in \mathbb{R}^{d_k}$ is a context vector encoding task state (e.g., current robot position, dialogue history). This enables context-dependent modality weighting: visual navigation tasks should learn $\alpha^{eye} > \alpha^{speech}$, while dialogue tasks should learn $\alpha^{speech} > \alpha^{eye}$.

#### 3.2.4 Uncertainty-Aware Reward Decoder

The fused representation $z_t$ is processed by a reward decoder with learned variance:

$$\mu_t = \text{MLP}_\mu(z_t), \quad \log \sigma_t^2 = \text{MLP}_\sigma(z_t)$$

$$\hat{r}_t \sim \mathcal{N}(\mu_t, \sigma_t^2)$$

The decoder is trained with negative log-likelihood loss on ground-truth human ratings $r_t^{GT}$:

$$\mathcal{L}_{reward} = -\sum_t \log \mathcal{N}(r_t^{GT}; \mu_t, \sigma_t^2) = \sum_t \left[\frac{(r_t^{GT} - \mu_t)^2}{2\sigma_t^2} + \frac{1}{2}\log \sigma_t^2\right]$$

This encourages the model to output high uncertainty $\sigma_t$ when modalities conflict or feedback is ambiguous.

#### 3.2.5 Policy Learning

The decoded rewards $\hat{r}_t$ are used to train a policy $\pi_\phi(a|s)$ via Proximal Policy Optimization (PPO):

$$\mathcal{L}_{policy} = \mathbb{E}_{\tau \sim \pi_\phi}\left[\sum_t \min\left(r_t(\theta) A_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t\right)\right]$$

where $r_t(\theta) = \frac{\pi_\phi(a_t|s_t)}{\pi_{\phi_{old}}(a_t|s_t)}$ is the probability ratio and $A_t$ is the advantage estimate computed using decoded rewards $\hat{r}_t$.

### 3.3 Data Collection

#### 3.3.1 Participant Recruitment

We will recruit N=90 participants (30 per task domain) through university accessibility centers and assistive technology user groups. Inclusion criteria:
- Age 18-65
- No prior experience with study tasks (to avoid confounding from expertise)
- Ability to provide informed consent
- For assistive technology domains: users with relevant disabilities (wheelchair users for navigation, amputees for prosthetic control)

Exclusion criteria:
- Visual impairments preventing eye-tracking calibration
- Severe speech impairments preventing prosody extraction
- Cognitive impairments affecting ability to provide consistent feedback

#### 3.3.2 Experimental Setup

**Hardware:**
- Eye-tracking: Tobii Pro Spectrum (120Hz binocular tracking)
- Speech recording: Shure SM7B microphone (48kHz sampling)
- Gesture capture: Azure Kinect depth camera (30fps)
- Synchronized data collection via Lab Streaming Layer (LSL) protocol

**Task Domains:**

1. **Wheelchair Navigation (Visual Task):** Participants control simulated wheelchair through indoor environments with obstacles, narrow corridors, and doorways. Success metric: collision-free navigation to goal within time limit.

2. **Prosthetic Control (Physical Task):** Participants control simulated prosthetic arm to grasp and manipulate objects. Success metric: successful object placement within tolerance.

3. **Educational Tutoring (Dialogue Task):** Participants interact with math tutoring system that adapts problem difficulty. Success metric: learning gain on post-test.

#### 3.3.3 Data Collection Protocol

Each participant completes 7 sessions (one per modality condition: eye-only, speech-only, gesture-only, eye+speech, eye+gesture, speech+gesture, all three), counterbalanced using Latin square design. Each session consists of:

1. **Calibration (5 min):** Eye-tracker calibration, speech baseline recording, gesture range-of-motion capture
2. **Training Phase (30 min):** 10,000 interaction steps with IGL exploration (ε-greedy, ε=0.1 decaying to 0.01)
3. **Evaluation Phase (10 min):** 100 test episodes with learned policy (no exploration)
4. **Ground-Truth Labeling (15 min):** Participant reviews 50 randomly sampled trajectories and provides explicit reward ratings (1-7 Likert scale) for reward decoder validation

Total data collection: 90 participants × 7 sessions × 10k steps = 6.3M interaction steps.

### 3.4 Experimental Design

#### 3.4.1 Study Design

**Design Type:** 3 (Task Type: Visual, Dialogue, Physical) × 7 (Modality Condition: 3 single + 3 dual + 1 triple) Mixed Factorial Design

**Between-Subjects Factor:** Task Type (N=30 per task)
**Within-Subjects Factor:** Modality Condition (all participants complete all 7 conditions)

**Counterbalancing:** Latin square order for modality conditions to control for learning effects.

#### 3.4.2 Baseline Comparisons

**Primary Baseline:**
- **Single-Modality IGL Oracle:** For each participant, select best single-modality condition (eye/speech/gesture) based on validation set performance. This represents upper bound of single-modality approaches.

**Secondary Baselines:**
- **Explicit Multimodal RLHF (OpenRLHF-M):** Train Bradley-Terry reward model on pairwise trajectory preferences, then use PPO with learned reward model. Requires participants to provide explicit preference labels.
- **Early Fusion Multimodal IGL:** Concatenate all modality features before reward decoder (no attention mechanism).
- **Fixed Temporal Pooling:** Use fixed downsampling (average pooling) instead of learnable temporal pooling.

#### 3.4.3 Evaluation Metrics

**Primary Metrics:**

1. **Reward Decoder Accuracy:** Pearson correlation $r$ between decoded rewards $\hat{r}_t$ and ground-truth human ratings $r_t^{GT}$ on held-out test trajectories:
$$\text{Accuracy} = \text{Corr}(\{\hat{r}_t\}, \{r_t^{GT}\})$$

2. **Policy Success Rate:** Task-specific success metrics averaged over 100 test episodes:
$$\text{Success Rate} = \frac{1}{100}\sum_{i=1}^{100} \mathbb{1}[\text{episode}_i \text{ succeeds}]$$

**Secondary Metrics:**

3. **Cross-Modal Attention Weights:** Average attention weights $\bar{\alpha}^m = \frac{1}{T}\sum_t \alpha_t^m$ over last 1000 training steps, analyzed per task type.

4. **Uncertainty Calibration:** Expected Calibration Error (ECE) measuring alignment between predicted uncertainty $\sigma_t$ and actual decoder error $|r_t^{GT} - \mu_t|$:
$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{T} |\text{avg}_{t \in B_b}(\sigma_t) - \text{avg}_{t \in B_b}(|r_t^{GT} - \mu_t|)|$$
where $B_b$ are bins of predictions sorted by uncertainty.

5. **Data Efficiency:** Reward decoder accuracy as function of training interactions (learning curves).

6. **Inference Time:** Average time (ms) to process multimodal feedback and decode reward per timestep.

### 3.5 Statistical Analysis Plan

#### 3.5.1 Primary Hypothesis Tests

**H1 (Reward Decoder Accuracy Gain):**
- **Null Hypothesis:** $\mu_{multi} = \mu_{best\_single}$ (no difference in reward decoder accuracy)
- **Test:** Paired t-test comparing multimodal accuracy vs. best single-modality accuracy per participant
- **Significance Level:** $\alpha = 0.05$ (two-tailed)
- **Effect Size:** Cohen's $d$ (expected $d \geq 0.5$ for medium effect)
- **Success Criterion:** $\Delta r \geq 0.15$ with $p < 0.05$

**H2 (Context-Dependent Attention):**
- **Null Hypothesis:** $\alpha_{dominant} \leq 0.33$ (uniform attention, no modality prioritization)
- **Test:** One-sample t-test per task type testing $H_1: \alpha_{dominant} > 0.5$
- **Bonferroni Correction:** $\alpha = 0.05/3 = 0.0167$ (3 task types)
- **Bootstrap Confidence Intervals:** 95% CI around mean attention weights

**H3 (Uncertainty with Conflict):**
- **Null Hypothesis:** $\sigma_{conflict} = \sigma_{agreement}$ (no uncertainty difference)
- **Test:** Mann-Whitney U test (non-parametric, uncertainty may be skewed)
- **Significance Level:** $\alpha = 0.01$
- **Operational Definition:** Conflict = $|\psi_{eye}(y^{eye}) - \psi_{speech}(y^{speech})| \geq 0.5$, Agreement = $< 0.2$

**H4 (Policy Performance):**
- **Null Hypothesis:** $\pi_{multi\_success} = \pi_{single\_success}$ (no policy improvement)
- **Test:** Repeated measures ANOVA (4 conditions: 3 single-modality + 1 multimodal) with Tukey HSD post-hoc
- **Significance Level:** $\alpha = 0.05$
- **Effect Size:** Partial $\eta^2$ (expected $\eta^2 \geq 0.06$ for medium effect)

#### 3.5.2 Secondary Analyses

**Ablation Study:** Compare 5 architectural variants via one-way ANOVA:
1. Full model (cross-modal attention + learnable pooling + uncertainty)
2. No attention (early fusion)
3. No learnable pooling (fixed downsampling)
4. No uncertainty (point estimate only)
5. Late fusion (separate reward decoders per modality, averaged)

**Modality Interaction:** Test if eye+speech fusion advantage over eye+gesture depends on task type (2-way interaction effect: modality pair × task type).

**Learning Curves:** Mixed-effects model with fixed effects (time, modality condition) and random effects (participant) to test if multimodal IGL converges faster.

#### 3.5.3 Control for Confounds

- **Order Effects:** Latin square counterbalancing + test for order effects via mixed-effects model
- **Task Difficulty:** Normalize success rates within task type before cross-task comparison
- **Participant Variability:** Within-subject design + random effects in mixed models
- **Encoder Quality:** Use identical pre-trained encoders across all conditions (frozen weights)

#### 3.5.4 Data Validation

- **Manipulation Check:** Verify encoder outputs differ across modalities (correlation matrix should show $r < 0.5$ between modalities)
- **Attention Check:** Remove participants with flat attention weights ($\alpha_i \approx 0.33$ for all $i$) indicating inattention
- **Outlier Detection:** Winsorize reward decoder accuracy at 5th/95th percentile

### 3.6 Implementation Details

**Software Stack:**
- PyTorch 2.0 for neural network implementation
- Stable-Baselines3 for PPO policy learning
- Hugging Face Transformers for pre-trained encoders (wav2vec2, Gazelle)
- MediaPipe for gesture recognition
- Lab Streaming Layer (LSL) for multimodal data synchronization

**Hyperparameters:**
- Encoder dimensions: $d_{eye} = d_{speech} = d_{gesture} = 256$
- Fusion dimension: $d_k = 128$
- Reward decoder: 3-layer MLP [256, 128, 64] with ReLU activations
- Learning rate: $3 \times 10^{-4}$ (Adam optimizer)
- Batch size: 256 trajectories
- PPO clip ratio: $\epsilon = 0.2$
- Discount factor: $\gamma = 0.99$
- Temporal pooling window: 1 second (120 eye samples, 800 speech frames, 30 gesture frames)

**Computational Resources:**
- Training: 4× NVIDIA A100 GPUs (40GB VRAM each)
- Estimated training time: 48 hours per participant session
- Total compute: 90 participants × 7 sessions × 48 hours = 30,240 GPU-hours

**Code Release:**
All code, pre-trained models, and preprocessed datasets will be released under MIT license on GitHub with comprehensive documentation and reproducibility scripts.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Theoretical Contributions

**Outcome 1: Multimodal IGL Identifiability Theorem**
We expect to prove that the conditional independence assumption $P(y^{multi}|a,x,r^*) = P(y^{multi}|r^*)$ holds for multimodal feedback vectors when fusion mechanisms satisfy information preservation constraints. Specifically, we will establish sufficient conditions on cross-modal attention fusion such that:

$$I(f_{fusion}(y^{multi}); r^*) \geq \max_{m \in \mathcal{M}} I(y^m; r^*)$$

This extends IGL's theoretical foundation from single-modality to multimodal spaces, providing formal guarantees for reward decoder identifiability.

**Outcome 2: Context-Dependent Modality Weighting Theory**
We expect to demonstrate that cross-modal attention learns task-specific modality prioritization aligned with human multisensory integration principles. Predicted attention patterns:
- Visual tasks (navigation): $\alpha^{eye} > 0.5$, $\alpha^{eye} > \alpha^{speech} + \alpha^{gesture}$
- Dialogue tasks (tutoring): $\alpha^{speech} > 0.5$, $\alpha^{speech} > \alpha^{eye} + \alpha^{gesture}$
- Physical tasks (manipulation): $\alpha^{gesture} > 0.5$, $\alpha^{gesture} > \alpha^{eye} + \alpha^{speech}$

This provides theoretical justification for adaptive fusion over fixed weighting schemes.

#### 4.1.2 Empirical Contributions

**Outcome 3: Reward Decoder Accuracy Improvement**
Based on preliminary simulations and related work in multimodal RLHF, we predict:
- Multimodal IGL reward decoder accuracy: $r = 0.78 \pm 0.05$ (Pearson correlation with ground-truth)
- Best single-modality IGL accuracy: $r = 0.63 \pm 0.07$
- **Improvement: $\Delta r = 0.15$** (23.8% relative gain), $p < 0.001$, Cohen's $d = 0.82$ (large effect)

This represents a medium-to-large effect size, translating to substantially better alignment between decoded rewards and user preferences.

**Outcome 4: Policy Performance Improvement**
We predict that improved reward decoder accuracy will translate to higher task success rates:
- Multimodal IGL policy success rate: $85\% \pm 5\%$
- Best single-modality IGL policy: $75\% \pm 6\%$
- **Improvement: $\Delta success = 10\%$** absolute, $p < 0.01$, partial $\eta^2 = 0.12$ (medium effect)

This demonstrates practical value: 1 in 10 additional tasks completed successfully.

**Outcome 5: Uncertainty Calibration Validation**
We expect uncertainty estimates to correctly identify conflicting multimodal signals:
- Expected Calibration Error (ECE): $< 0.05$ (well-calibrated)
- Uncertainty in conflict scenarios: $\sigma_{conflict} = 0.42 \pm 0.08$
- Uncertainty in agreement scenarios: $\sigma_{agreement} = 0.18 \pm 0.05$
- **Difference: $\Delta\sigma = 0.24$**, $p < 0.001$ (Mann-Whitney U test)

This enables safe exploration: when modalities conflict, high uncertainty signals "don't trust this reward."

#### 4.1.3 Methodological Contributions

**Outcome 6: Open-Source Multimodal IGL Framework**
We will release a production-ready implementation including:
- Pre-trained modality encoders (eye, speech, gesture)
- Learnable temporal pooling module
- Cross-modal attention fusion layer
- Uncertainty-aware reward decoder
- Integration with Stable-Baselines3 for policy learning
- Comprehensive documentation and tutorials

Expected impact: Enable researchers to apply multimodal IGL to new domains without reimplementing core components.

**Outcome 7: Benchmark Datasets**
We will release three multimodal implicit feedback datasets:
- Wheelchair navigation: 900k interaction steps (30 participants × 30k steps)
- Prosthetic control: 900k interaction steps
- Educational tutoring: 900k interaction steps

Each dataset includes synchronized eye-tracking, speech, gesture, and ground-truth reward labels. This addresses the current lack of public multimodal implicit feedback benchmarks.

### 4.2 Scientific Impact

#### 4.2.1 Advancing Interactive Machine Learning Theory

This research bridges three previously disconnected areas:

1. **IGL Theory → Multimodal Extension:** Extends reward identifiability guarantees from single-modality to multimodal feedback spaces, establishing theoretical foundations for learning from natural human communication.

2. **Neuroscience → Deep Learning Translation:** Translates multisensory integration principles (hierarchical processing, context-dependent weighting) into practical architectures, demonstrating how cognitive science can inform ML design.

3. **RLHF → Implicit Feedback:** Shows that multimodal RLHF benefits (richer signal, robustness) can be achieved without explicit preference labeling, reducing human annotation burden.

Expected citations: 50-100 within 3 years based on citation patterns of foundational IGL paper (NeurIPS 2022) and multimodal RLHF work.

#### 4.2.2 Enabling New Research Directions

**Direction 1: Non-Stationary Multimodal IGL**
Our architecture provides foundation for addressing temporal preference drift (Gap 2 from workshop topics). Future work can add online reward decoder updating to handle changing user preferences over time.

**Direction 2: Modality-Specific Reward Decomposition**
Cross-modal attention weights reveal which modalities contribute to reward evaluation. This enables interpretable reward models: "User dislikes this action because gaze shows avoidance (α_eye=0.7) despite neutral speech tone (α_speech=0.2)."

**Direction 3: Transfer Learning Across Users**
Pre-trained encoders + attention mechanism enable few-shot personalization: train on average user (pre-training), fine-tune attention weights for specific user (personalization). This addresses workshop question on pre-training vs. interactive learning balance.

### 4.3 Practical Impact

#### 4.3.1 Assistive Technology Applications

**Impact Area 1: Wheelchair Navigation Systems**
- **Current Limitation:** Joystick control requires fine motor skills; voice commands require explicit instruction
- **Multimodal IGL Solution:** Learn from gaze (desired direction) + speech tone (comfort) + head gestures (approval) without explicit commands
- **Expected Benefit:** 30% reduction in navigation errors, 40% reduction in user cognitive load (measured via NASA-TLX)
- **Deployment Timeline:** Clinical trials within 18 months post-publication

**Impact Area 2: Prosthetic Control Interfaces**
- **Current Limitation:** EMG-based control requires extensive training; lacks intuitive feedback
- **Multimodal IGL Solution:** Combine residual limb signals + facial expressions (frustration) + vocal cues (effort) for adaptive control
- **Expected Benefit:** 25% faster task completion, 50% reduction in training time for new users
- **Deployment Timeline:** Partnership with prosthetic manufacturers for prototype integration

**Impact Area 3: Educational Software**
- **Current Limitation:** One-size-fits-all difficulty progression; no real-time adaptation to student state
- **Multimodal IGL Solution:** Adapt problem difficulty based on gaze patterns (attention) + speech prosody (frustration) + posture (engagement)
- **Expected Benefit:** 15% improvement in learning outcomes (pre/post-test gains), 20% increase in engagement time
- **Deployment Timeline:** Integration with existing educational platforms (Khan Academy, Coursera)

#### 4.3.2 Broader Societal Impact

**Accessibility & Inclusion:**
By enabling AI systems to learn from natural multimodal communication, this research reduces barriers for users with disabilities who cannot provide explicit structured feedback. Estimated impact: 50 million wheelchair users, 2 million amputees, 100 million students with learning differences globally.

**Ability-Based Design at Scale:**
The architecture embodies ability-based design principles: adapt system to user capabilities rather than requiring user to adapt to system. This addresses workshop question on deploying ability-based design at scale through ML.

**Privacy-Preserving Personalization:**
Multimodal implicit feedback enables personalization without collecting explicit preference labels (which may reveal sensitive information). Uncertainty quantification provides transparency: users can see when system is uncertain about their preferences.

### 4.4 Limitations & Future Work

**Limitation 1: Computational Cost**
Multimodal IGL requires 3-5× more compute than single-modality IGL due to multiple encoders and attention fusion. Future work: model compression, efficient attention mechanisms, edge deployment optimization.

**Limitation 2: Privacy Concerns**
Eye-tracking and speech recording raise privacy issues. Future work: federated learning for on-device training, differential privacy for reward decoder, secure multiparty computation for sensitive applications.

**Limitation 3: Non-Stationarity Not Addressed**
Current architecture assumes stationary reward functions. Future work: online reward decoder updating, meta-learning for rapid adaptation, explicit modeling of preference drift.

**Limitation 4: Limited Modality Coverage**
We focus on eye/speech/gesture; other modalities (EEG, heart rate, facial expressions) may provide additional signal. Future work: extend to physiological signals, test modality combinations beyond three.

### 4.5 Timeline & Milestones

**Months 1-6: Architecture Development & Simulation**
- Implement hierarchical multimodal IGL architecture
- Validate on synthetic datasets with known ground-truth rewards
- Ablation studies on architectural components
- **Milestone:** Working prototype with ECE < 0.1 on synthetic data

**Months 7-12: Pilot Studies**
- Recruit N=15 pilot participants (5 per task domain)
- Collect preliminary multimodal feedback data
- Refine data collection protocol based on pilot feedback
- **Milestone:** Pilot data demonstrating Δr ≥ 0.10 improvement

**Months 13-24: Full-Scale Experiments**
- Recruit N=90 participants for main study
- Collect 6.3M interaction steps across 3 task domains
- Train multimodal IGL models and baselines
- **Milestone:** Complete data collection and model training

**Months 25-30: Analysis & Dissemination**
- Statistical analysis of primary/secondary hypotheses
- Prepare open-source code release and benchmark datasets
- Write publications (1 theory paper, 1 systems paper, 1 applications paper)
- **Milestone:** NeurIPS/ICML submission, code/data release

**Months 31-36: Deployment & Clinical Trials**
- Partner with assistive technology manufacturers
- Deploy wheelchair navigation system in clinical setting
- Collect real-world usage data and user feedback
- **Milestone:** Clinical trial results demonstrating real-world efficacy

### 4.6 Success Criteria

This research will be considered successful if:

1. **Theoretical Success:** Multimodal IGL identifiability theorem proven and published in top-tier ML venue (NeurIPS, ICML, ICLR)
2. **Empirical Success:** Primary hypothesis (Δr ≥ 0.15) validated with p < 0.05 across all three task domains
3. **Practical Success:** At least one assistive technology application deployed in real-world setting with positive user feedback
4. **Community Success:** Open-source framework adopted by ≥5 research groups within 2 years (measured via GitHub stars, citations, derivative works)
5. **Societal Success:** Demonstrated improvement in quality of life for users with disabilities (measured via standardized accessibility questionnaires)

By achieving these outcomes, this research will establish multimodal IGL as a foundational paradigm for building personalized assistive systems that learn from natural human communication, advancing both the science of interactive machine learning and the practice of accessible AI.