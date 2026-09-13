# Research Proposal: Learning Grounded Reward Functions from Multimodal Implicit Feedback with Unknown Semantics

## 1. Introduction

### Background

Interactive learning systems are increasingly deployed in real-world applications, from personalized assistive robots to adaptive educational interfaces. These systems fundamentally rely on human feedback to align their behavior with user intentions and preferences. Traditionally, such systems require explicit feedback mechanisms—numerical ratings, binary rewards, or carefully structured demonstrations—that place significant cognitive burden on users and often feel unnatural in everyday interactions.

Humans, however, communicate intent through a rich tapestry of implicit signals that arise naturally during interaction. Facial expressions convey satisfaction or frustration, gaze patterns reveal attention and interest, speech prosody indicates approval or confusion, and gestures provide contextual emphasis. These signals are produced effortlessly and continuously, offering a potentially unlimited source of feedback information. Yet, leveraging these implicit signals presents fundamental challenges: their semantics are often ambiguous, context-dependent, and vary significantly across individuals. A furrowed brow might indicate concentration for one user but frustration for another; a particular vocal inflection might signal encouragement in one cultural context but skepticism in another.

Recent advances have demonstrated the feasibility of learning from specific implicit signals. Kim et al. (2025) showed that EEG-derived error-related potentials can provide effective reward signals for robot control, while the NEURO-LOOP framework (Santaniello et al., 2025) established that fNIRS brain signals can be mapped to agent performance. However, these approaches typically focus on single modalities with relatively well-understood neural correlates. The broader challenge of learning from arbitrary multimodal implicit feedback—where the semantic grounding must be discovered rather than assumed—remains largely unexplored.

### Research Objectives

This research proposes **Implicit Feedback Grounding Networks (IFG-Net)**, a novel framework that addresses the fundamental question: *How can learning agents autonomously discover the semantic grounding of multimodal implicit feedback signals and leverage them for reward inference without predefined mappings?*

Our specific objectives are:

1. **Develop a self-supervised grounding mechanism** that learns to map multimodal implicit feedback signals to latent reward representations without requiring explicit reward labels.

2. **Design an uncertainty-aware active learning component** that strategically queries users when the grounding model encounters ambiguous or novel feedback patterns.

3. **Create a personalization framework** that adapts the learned grounding to individual users' communication styles while maintaining sample efficiency.

4. **Validate the framework** through comprehensive experiments in simulated and real-world interactive tasks, demonstrating improved task performance and user experience compared to explicit feedback baselines.

### Significance

This research addresses several critical gaps identified in the literature on interactive learning from human feedback. The "Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback" survey (2023) highlights the need for methods that can handle diverse and ambiguous feedback forms. Our work directly tackles this by proposing a principled approach to semantic grounding discovery.

Furthermore, this research has significant implications for accessibility and inclusive design. By enabling systems to learn from natural human signals rather than requiring users to adapt to artificial feedback mechanisms, we can create more accessible interfaces for users with diverse abilities, aligning with the HCI community's goals for ability-based design at scale.

## 2. Methodology

### 2.1 Problem Formulation

We formalize the interactive learning problem as a Partially Observable Markov Decision Process (POMDP) augmented with implicit feedback signals. At each timestep $t$, the agent observes the environment state $s_t$, takes action $a_t$, and receives multimodal implicit feedback $\mathbf{f}_t = \{f_t^{(1)}, f_t^{(2)}, ..., f_t^{(M)}\}$ from $M$ modalities (e.g., facial expressions, gaze, speech prosody). The true reward $r_t$ is unknown to the agent and must be inferred from $\mathbf{f}_t$.

The key challenge is that the mapping $g: \mathbf{f}_t \rightarrow r_t$ is initially unknown, potentially non-stationary, and user-specific. Our goal is to jointly learn:

1. A grounding function $G_\phi(\mathbf{f}_t, c_t) \rightarrow \hat{r}_t$ that maps implicit feedback to inferred rewards given context $c_t$
2. A policy $\pi_\theta(a_t | s_t)$ that maximizes cumulative inferred rewards

### 2.2 Multimodal Feature Extraction

For each modality $m$, we employ modality-specific encoders $E^{(m)}$ to extract feature representations:

$$\mathbf{z}_t^{(m)} = E^{(m)}(f_t^{(m)})$$

For facial expressions, we use a pre-trained action unit detection model followed by a temporal convolutional network to capture micro-expression dynamics. For gaze patterns, we extract fixation sequences and saccade characteristics, encoding them with a recurrent neural network. For speech prosody, we use a wav2vec-based encoder that captures pitch contours, energy patterns, and temporal dynamics.

The multimodal features are fused using a cross-modal attention mechanism:

$$\mathbf{z}_t^{fused} = \text{CrossAttention}(\mathbf{z}_t^{(1)}, ..., \mathbf{z}_t^{(M)})$$

where the attention mechanism learns to weight modalities based on their informativeness in the current context.

### 2.3 Self-Supervised Contrastive Grounding

The core innovation of IFG-Net is learning reward grounding without explicit labels through a contrastive learning objective. Our key insight is that implicit feedback signals following successful task outcomes should be more similar to each other than to signals following failures, even when the agent initially cannot distinguish success from failure.

We maintain an experience buffer $\mathcal{B}$ of interaction episodes. For each episode $\tau_i$, we have access to the trajectory of states, actions, and implicit feedback signals: $\tau_i = \{(s_t^{(i)}, a_t^{(i)}, \mathbf{f}_t^{(i)})\}_{t=1}^{T_i}$.

**Temporal Consistency Objective**: Within an episode, implicit feedback signals should exhibit temporal consistency—if the user is satisfied, their signals should remain positive; if frustrated, the frustration should persist. We define:

$$\mathcal{L}_{temporal} = -\sum_{i} \sum_{t=1}^{T_i-1} \log \frac{\exp(\text{sim}(\mathbf{z}_t^{(i)}, \mathbf{z}_{t+1}^{(i)})/\tau)}{\sum_{j \neq i} \exp(\text{sim}(\mathbf{z}_t^{(i)}, \mathbf{z}_t^{(j)})/\tau)}$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity and $\tau$ is a temperature parameter.

**Outcome-Based Clustering**: We hypothesize that episode-level outcomes induce structure in the feedback space. Using weak supervision from task completion signals (which don't require explicit rewards), we encourage clustering:

$$\mathcal{L}_{cluster} = -\sum_{(i,j) \in \mathcal{P}^+} \log \frac{\exp(\text{sim}(\bar{\mathbf{z}}^{(i)}, \bar{\mathbf{z}}^{(j)})/\tau)}{\sum_k \exp(\text{sim}(\bar{\mathbf{z}}^{(i)}, \bar{\mathbf{z}}^{(k)})/\tau)}$$

where $\bar{\mathbf{z}}^{(i)}$ is the mean embedding for episode $i$, and $\mathcal{P}^+$ contains pairs of episodes with similar outcomes (both completed or both abandoned).

**Reward Prediction Head**: The grounding function $G_\phi$ maps the fused embedding to a scalar reward estimate:

$$\hat{r}_t = G_\phi(\mathbf{z}_t^{fused}, c_t) = \text{MLP}([\mathbf{z}_t^{fused}; \mathbf{h}_t^{context}])$$

where $\mathbf{h}_t^{context}$ is a context vector encoding recent interaction history through an LSTM.

### 2.4 Uncertainty-Aware Active Querying

When the grounding model encounters ambiguous feedback patterns, we employ active queries to resolve uncertainty. We estimate epistemic uncertainty using Monte Carlo dropout:

$$U(\mathbf{f}_t) = \text{Var}_{k=1}^K[G_\phi^{(k)}(\mathbf{f}_t)]$$

where $G_\phi^{(k)}$ denotes the $k$-th forward pass with dropout. When $U(\mathbf{f}_t) > \gamma$ (a threshold), the system generates a natural language query:

$$q_t = \text{QueryGenerator}(\mathbf{z}_t^{fused}, s_t, a_t)$$

The query generator is trained to produce contextually appropriate questions such as "I noticed you seemed uncertain—was this action helpful?" User responses are incorporated as supervised labels to refine the grounding function.

### 2.5 Personalization via Meta-Learning

To adapt to individual users efficiently, we employ a Model-Agnostic Meta-Learning (MAML) approach. The grounding model parameters $\phi$ are trained such that they can be quickly adapted to new users with minimal interaction:

$$\phi^* = \arg\min_\phi \sum_{u=1}^U \mathcal{L}_{ground}(\phi - \alpha \nabla_\phi \mathcal{L}_{ground}^{(u)}(\phi))$$

where $\mathcal{L}_{ground}^{(u)}$ is the grounding loss on user $u$'s data and $\alpha$ is the inner-loop learning rate. This enables the model to capture shared structure across users while maintaining the flexibility to personalize rapidly.

### 2.6 Policy Learning

Given the learned grounding function, we train the policy using Proximal Policy Optimization (PPO) with the inferred rewards:

$$\mathcal{L}_{policy} = \mathbb{E}_t\left[\min\left(\frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)} \hat{A}_t, \text{clip}(\cdot, 1-\epsilon, 1+\epsilon) \hat{A}_t\right)\right]$$

where $\hat{A}_t$ is computed using inferred rewards $\hat{r}_t$ from the grounding function.

### 2.7 Experimental Design

**Environments**: We evaluate IFG-Net in three domains:
1. **Simulated Assistive Robot**: A robotic arm helping users with object manipulation tasks
2. **Educational Tutoring System**: An adaptive tutoring interface that adjusts explanations based on student feedback
3. **Collaborative Game**: A cooperative game where agents must coordinate with human players

**Data Collection**: We recruit 100 participants (ensuring demographic diversity) to interact with our systems. We collect synchronized multimodal data: facial video (30fps), eye-tracking (120Hz), and audio. Participants provide post-hoc preference labels for validation but not training.

**Baselines**:
- Explicit reward baseline (users provide numerical ratings)
- Single-modality implicit feedback (facial expressions only)
- Pre-defined sentiment mapping (using off-the-shelf emotion recognition)
- Random policy baseline

**Evaluation Metrics**:
- **Task Performance**: Success rate, completion time, error rate
- **Grounding Accuracy**: Correlation between inferred and post-hoc labeled rewards
- **User Experience**: NASA-TLX workload assessment, System Usability Scale
- **Sample Efficiency**: Performance as a function of interaction episodes
- **Personalization Speed**: Adaptation performance after $k$ interactions with a new user

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Autonomous Semantic Discovery**: We expect IFG-Net to successfully discover meaningful grounding for implicit feedback signals, achieving correlation coefficients of $r > 0.7$ between inferred and true rewards without any explicit reward labels during training.

2. **Superior Task Performance**: We anticipate that policies trained with IFG-Net inferred rewards will achieve task success rates within 10% of policies trained with explicit dense rewards, while significantly outperforming random and pre-defined mapping baselines.

3. **Enhanced User Experience**: By eliminating the need for explicit feedback, we expect significant reductions in cognitive workload (20-30% reduction on NASA-TLX) and improved subjective satisfaction scores.

4. **Efficient Personalization**: The meta-learning component should enable effective personalization to new users within 5-10 interaction episodes, compared to 50+ episodes for non-meta-learning approaches.

5. **Robust Multimodal Fusion**: We expect the cross-modal attention mechanism to learn meaningful modality weighting, with ablation studies revealing synergistic benefits from multimodal integration.

### Broader Impact

This research has far-reaching implications across multiple domains:

**Accessibility**: By learning from natural human signals, IFG-Net can enable adaptive interfaces for users who cannot easily provide explicit feedback, including individuals with motor impairments or cognitive differences.

**Scalable Personalization**: The framework provides a foundation for truly personalized AI assistants that learn each user's unique communication style without requiring extensive explicit training.

**Naturalistic Human-Robot Interaction**: Robots equipped with IFG-Net can engage in more natural social interactions, reading implicit cues that humans use when interacting with each other.

**Scientific Understanding**: The learned grounding models may provide insights into how humans naturally communicate reward and preference signals, contributing to cognitive science research.

The framework also raises important ethical considerations regarding privacy (continuous monitoring of facial expressions and gaze) and consent, which we will address through transparent data practices and user control mechanisms. We commit to releasing our code, models, and anonymized datasets to enable reproducibility and further research in this critical area.