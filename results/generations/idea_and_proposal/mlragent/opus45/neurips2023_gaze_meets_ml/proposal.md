# Research Proposal: Gaze-Guided Curriculum Learning for Sample-Efficient Reinforcement Learning

## 1. Introduction

### Background

Reinforcement learning (RL) has achieved remarkable success in solving complex sequential decision-making problems, from mastering Atari games to controlling robotic systems. However, a fundamental limitation persists: sample inefficiency. State-of-the-art RL agents often require millions of environment interactions to learn tasks that humans can master within minutes. This disparity stems largely from the lack of attentional priors—humans naturally know where to look and what visual features matter, while RL agents must discover this from scratch through extensive exploration.

Human eye gaze provides a window into cognitive attention mechanisms that have evolved over millions of years. When humans perform visual tasks, their gaze patterns reveal a hierarchical structure of attention: initially focusing on salient, easily detectable features before progressively attending to subtler, task-relevant details. This natural progression suggests an implicit curriculum embedded in human visual attention. Recent advances in eye-tracking technology have made it feasible to collect large-scale gaze data during task performance, opening opportunities to transfer human attentional knowledge to artificial agents.

The intersection of gaze research and machine learning has gained significant momentum. Work such as "Gaze on the Prize" (Lee et al., 2025) demonstrated that incorporating foveal attention mechanisms can improve sample efficiency by up to 2.4x in manipulation tasks. Similarly, EyeFormer (Jiang et al., 2024) showed that Transformer-guided reinforcement learning can predict personalized scanpaths effectively. These advances suggest that gaze information contains valuable signals for accelerating and improving machine learning systems.

### Research Objectives

This research proposes a novel framework called **Gaze-Guided Curriculum Learning (GGCL)** that leverages human eye-tracking data to construct dynamic curricula for visual reinforcement learning. Our specific objectives are:

1. To develop a methodology for extracting temporal attention patterns from human gaze data during task performance across different skill levels.
2. To design a gaze prediction model that generalizes human attention distributions to novel states not seen during data collection.
3. To create a curriculum learning mechanism that progressively expands the agent's observable state space based on predicted gaze saliency.
4. To validate the framework's effectiveness in improving sample efficiency and policy interpretability on standard visual RL benchmarks.

### Significance

This research addresses a critical gap between human and machine learning capabilities. By explicitly modeling and transferring human attentional curricula, we can create agents that learn more efficiently and produce more interpretable behaviors. The significance extends to practical applications including autonomous driving, robotic manipulation, and medical imaging analysis, where sample efficiency and human-AI alignment are paramount. Furthermore, this work contributes to our understanding of how human cognitive mechanisms can inform artificial intelligence development, fostering deeper integration between neuroscience and machine learning communities.

## 2. Methodology

### 2.1 Overview

The GGCL framework consists of four main components: (1) human gaze data collection and preprocessing, (2) temporal attention pattern extraction and gaze prediction modeling, (3) curriculum mechanism design with progressive state masking and gaze-weighted reward shaping, and (4) integration with visual RL algorithms. Figure 1 (conceptual) illustrates the overall pipeline.

### 2.2 Data Collection and Preprocessing

**Participant Recruitment**: We will recruit 50 human participants with varying experience levels in video game playing to capture diverse attention patterns. Participants will be categorized into novice (0-2 hours of gaming weekly), intermediate (3-10 hours), and expert (>10 hours) groups.

**Eye-Tracking Setup**: We employ the Tobii Pro Spectrum eye tracker (sampling rate: 600 Hz) synchronized with game state recordings. Participants perform tasks in selected Atari environments (Breakout, Pong, Seaquest, Space Invaders) and DeepMind Control Suite tasks (Walker-walk, Cheetah-run, Finger-spin).

**Data Preprocessing**: Raw gaze data undergoes the following preprocessing pipeline:
- Velocity-based fixation detection using the I-VT algorithm with threshold $\theta_v = 30°/s$
- Saccade filtering and blink removal
- Spatial mapping of gaze coordinates to game frame pixels
- Temporal alignment with state-action-reward tuples

For each state $s_t$, we compute a gaze heatmap $G_t \in \mathbb{R}^{H \times W}$ using Gaussian kernel smoothing:

$$G_t(x, y) = \sum_{i=1}^{N_f} \frac{d_i}{\sum_j d_j} \cdot \exp\left(-\frac{(x - x_i)^2 + (y - y_i)^2}{2\sigma^2}\right)$$

where $(x_i, y_i)$ represents the $i$-th fixation location, $d_i$ is fixation duration, and $\sigma$ is the Gaussian kernel bandwidth.

### 2.3 Temporal Attention Pattern Extraction

We analyze how human attention evolves with skill acquisition by segmenting participant performance into skill phases based on cumulative reward percentiles. For participant $p$ at skill phase $k$, we aggregate gaze heatmaps to identify consistent attention patterns:

$$\bar{G}^{(k)}(s) = \frac{1}{|P_k|} \sum_{p \in P_k} G_p(s)$$

We employ Non-negative Matrix Factorization (NMF) to extract attention components:

$$\bar{G}^{(k)} \approx W^{(k)} H^{(k)}$$

where $W^{(k)}$ captures spatial attention bases and $H^{(k)}$ represents activation coefficients. This decomposition reveals which visual regions are consistently prioritized at each skill level.

### 2.4 Gaze Prediction Model

To generalize attention patterns to novel states, we train a **Gaze Prediction Network (GPN)** using a U-Net architecture with attention gates. The network takes a state observation $s_t$ and outputs a predicted gaze saliency map $\hat{G}_t$.

**Architecture**: The encoder consists of four convolutional blocks with ResNet-style skip connections. The decoder uses transposed convolutions with attention-gated skip connections from the encoder. A final sigmoid activation produces the normalized saliency map.

**Training Objective**: We minimize a hybrid loss combining KL divergence and correlation coefficient:

$$\mathcal{L}_{GPN} = \lambda_1 \cdot D_{KL}(G_t \| \hat{G}_t) - \lambda_2 \cdot CC(G_t, \hat{G}_t) + \lambda_3 \cdot \|G_t - \hat{G}_t\|_1$$

where:
$$D_{KL}(G \| \hat{G}) = \sum_{x,y} G(x,y) \log\frac{G(x,y)}{\hat{G}(x,y)}$$

$$CC(G, \hat{G}) = \frac{\text{Cov}(G, \hat{G})}{\sigma_G \cdot \sigma_{\hat{G}}}$$

We set $\lambda_1 = 1.0$, $\lambda_2 = 0.5$, $\lambda_3 = 0.3$ based on preliminary experiments.

### 2.5 Curriculum Mechanism

The curriculum mechanism operates on three interrelated components:

**Progressive State Masking**: We define a masking function $M_\phi: \mathbb{R}^{H \times W} \times [0,1] \rightarrow \{0,1\}^{H \times W}$ that binarizes the gaze saliency map based on curriculum phase $\phi \in [0,1]$:

$$M_\phi(\hat{G}_t)(x,y) = \mathbb{1}\left[\hat{G}_t(x,y) \geq \tau(\phi)\right]$$

where $\tau(\phi) = \tau_{max} \cdot (1 - \phi)$ defines a decreasing threshold. The masked observation is:

$$\tilde{s}_t = s_t \odot M_\phi(\hat{G}_t)$$

**Curriculum Progression**: The phase $\phi$ evolves based on agent performance measured by average episodic return $\bar{R}$ over a window of $K$ episodes:

$$\phi_{n+1} = \min\left(1, \phi_n + \alpha \cdot \frac{\bar{R}_n - \bar{R}_{n-1}}{\bar{R}_{target}}\right)$$

where $\alpha$ is the progression rate and $\bar{R}_{target}$ is the target performance level.

**Gaze-Weighted Reward Shaping**: We introduce auxiliary rewards that encourage human-like exploration:

$$r'_t = r_t + \beta \cdot \text{Sim}(A_t, \hat{G}_t)$$

where $A_t$ represents the agent's attention map (extracted from CNN feature activations via Grad-CAM) and $\text{Sim}(\cdot, \cdot)$ is the normalized scanpath saliency:

$$\text{Sim}(A, G) = \frac{1}{N} \sum_{i=1}^{N} \frac{G(a_i) - \mu_G}{\sigma_G}$$

where $a_i$ are the top-$N$ attended locations in $A_t$.

### 2.6 Integration with Visual RL

We integrate GGCL with two base RL algorithms:

1. **DrQ-v2** (Data-regularized Q-v2): A state-of-the-art model-free algorithm for visual control
2. **Dreamer-v3**: A model-based algorithm with learned world models

The modified training loop proceeds as follows:

```
Algorithm: GGCL Training
Input: Environment E, GPN model, base RL algorithm
Initialize: φ = 0, policy π, replay buffer D
for episode = 1 to N_episodes:
    s_0 = E.reset()
    for t = 0 to T:
        Ĝ_t = GPN(s_t)
        s̃_t = s_t ⊙ M_φ(Ĝ_t)
        a_t = π(s̃_t)
        s_{t+1}, r_t = E.step(a_t)
        r'_t = r_t + β · Sim(Attention(π, s̃_t), Ĝ_t)
        D.store(s̃_t, a_t, r'_t, s̃_{t+1})
    Update π using base RL algorithm with D
    Update φ based on episode return
```

### 2.7 Experimental Design

**Benchmarks**: 
- Atari 100K benchmark: 26 games with 100K environment steps
- DeepMind Control Suite: 6 tasks from easy to hard difficulty
- Meta-World: 10 manipulation tasks for generalization testing

**Baselines**:
1. Vanilla DrQ-v2 and Dreamer-v3 (no gaze guidance)
2. Random curriculum (random masking progression)
3. Saliency-based attention (bottom-up visual saliency)
4. Gaze on the Prize (return-guided attention)
5. Human demonstrations (behavioral cloning + RL)

**Evaluation Metrics**:
- **Sample Efficiency**: Area under the learning curve (AUC) at 100K, 500K, and 1M steps
- **Final Performance**: Mean episodic return over 100 evaluation episodes
- **Attention Alignment**: Pearson correlation between agent attention and human gaze maps
- **Generalization**: Zero-shot transfer performance to unseen task variants
- **Interpretability Score**: Human evaluation of policy explanations (5-point Likert scale)

**Statistical Analysis**: All experiments run with 10 random seeds. We report mean ± standard error and conduct paired t-tests with Bonferroni correction for significance testing ($p < 0.05$).

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results**: We anticipate GGCL will achieve:
- 3-5x improvement in sample efficiency (measured by AUC) compared to vanilla baselines
- 15-25% higher final performance on sparse reward tasks
- Attention alignment correlation > 0.7 with human gaze patterns
- Significant improvement in zero-shot generalization (>20% over baselines)

**Qualitative Results**: 
- Learned policies will demonstrate human-interpretable attention patterns
- Curriculum progression will mirror human skill acquisition stages
- Agent exploration will be more directed and efficient

**Deliverables**:
1. Open-source GGCL framework with pre-trained gaze prediction models
2. Human gaze dataset for RL tasks (estimated 500+ hours of annotated gameplay)
3. Benchmark results and trained model checkpoints
4. Analysis toolkit for attention alignment evaluation

### Broader Impact

**Scientific Impact**: This research advances our understanding of how human attentional mechanisms can be formalized and transferred to artificial agents. It contributes to the growing body of work bridging cognitive science and machine learning, providing new insights into curriculum learning and attention modeling.

**Practical Impact**: Improved sample efficiency has direct implications for real-world RL applications where data collection is expensive or risky, such as autonomous driving, surgical robotics, and industrial automation. The interpretability improvements enable better human oversight and trust in AI systems.

**Ethical Considerations**: We acknowledge that using human gaze data raises privacy concerns. All data collection will follow IRB-approved protocols with informed consent. We will investigate potential biases in attention patterns across demographic groups and develop mitigation strategies. The collected dataset will be anonymized and released with appropriate usage guidelines.

**Future Directions**: This work opens avenues for investigating gaze-guided learning in multi-agent settings, real-time human-AI collaboration, and transfer learning across domains. The framework can be extended to incorporate other physiological signals such as EEG or pupillometry for richer cognitive state inference.

In conclusion, Gaze-Guided Curriculum Learning represents a principled approach to bridging human cognition and artificial intelligence, leveraging the rich information in human visual attention to create more efficient and interpretable learning agents. By grounding machine learning in human cognitive mechanisms, we move toward AI systems that learn and behave in ways more aligned with human expectations and values.