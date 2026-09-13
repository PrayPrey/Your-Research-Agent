# Research Proposal: Learning-Progress-Gated Adaptive Reward Integration for Open-Ended Skill Discovery

## 1. Introduction

### 1.1 Background

The quest to understand how humans develop broad and flexible repertoires of knowledge and skills has long fascinated researchers across cognitive science, developmental psychology, and artificial intelligence. Humans exhibit remarkable abilities to explore their environments, discover novel skills, and adapt their learning strategies based on internal progress signals—all without explicit external supervision. This capacity for autonomous, open-ended learning represents a fundamental challenge for artificial intelligence systems.

Intrinsically motivated learning, also known as curiosity-driven learning, offers a promising computational framework for addressing this challenge. Drawing inspiration from the innate drive of humans and animals to seek "interesting" situations for their own sake, intrinsic motivations (IM) have evolved to support exploratory behaviors essential for efficient learning. When implemented in artificial agents, these mechanisms enable autonomous exploration of complex environments without relying on predefined learning signals.

Recent years have witnessed significant advances in intrinsically motivated reinforcement learning, with two dominant paradigms emerging. **Prediction-based methods**, exemplified by Random Network Distillation (RND), generate intrinsic rewards based on prediction errors of a randomly initialized neural network. These methods excel at achieving broad state coverage by rewarding visits to novel, unpredictable states. **Competence-based methods**, such as Diversity Is All You Need (DIAYN), focus on discovering diverse, distinguishable skills by maximizing the mutual information between skills and visited states. These approaches produce structured behavioral repertoires but may overlook novel states that don't contribute to skill differentiation.

Despite their individual successes, current intrinsically motivated agents face a fundamental limitation: the optimal balance between exploration (state coverage) and skill discovery shifts dynamically throughout the learning process. Early training phases benefit from novelty-seeking behaviors to map the environment's structure, while later stages require focused skill refinement to develop competent behaviors. Fixed combinations of intrinsic reward signals fail to capture this temporal dynamic, limiting agents' ability to develop the broad, flexible skill repertoires essential for open-ended learning.

### 1.2 Research Objectives

This research proposes **Learning-Progress-Gated Adaptive Reward Integration (LP-GARI)**, a novel framework that dynamically combines prediction-based and competence-based intrinsic rewards using a learned gating mechanism informed by learning progress signals. Our primary objectives are:

1. **Develop an adaptive reward integration mechanism** that automatically balances exploration and skill discovery based on the agent's current learning state.

2. **Validate the causal mechanism** by which learning progress signals inform optimal gating decisions throughout training.

3. **Demonstrate superior performance** in combined state coverage and skill diversity metrics compared to single-paradigm methods and fixed-weight combinations.

4. **Establish improved downstream task adaptation** through more effective reward-free pre-training.

### 1.3 Research Significance

This research addresses a critical gap in intrinsically motivated open-ended learning (IMOL) by providing a principled approach to reward integration that respects the temporal dynamics of learning. The significance of this work extends across multiple dimensions:

**Scientific Contribution:** LP-GARI provides a testable computational model of how learning progress signals can guide the allocation of exploratory resources, offering insights into the mechanisms underlying flexible, autonomous learning in both artificial and biological systems.

**Practical Impact:** By improving reward-free pre-training efficiency, LP-GARI advances the development of autonomous agents capable of learning in realistic open-ended environments without human intervention—a key concern for deploying AI systems in the real world.

**Methodological Advancement:** The proposed framework establishes a new paradigm for combining heterogeneous intrinsic motivation signals, with potential applications beyond the specific RND-DIAYN combination explored here.

## 2. Methodology

### 2.1 Problem Formulation

We consider reward-free pre-training (RFPT) in continuous-state Markov Decision Processes (MDPs) defined by the tuple $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, \gamma)$, where $\mathcal{S}$ is the continuous state space, $\mathcal{A}$ is the action space, $P(s'|s,a)$ is the transition dynamics, and $\gamma$ is the discount factor. During pre-training, no extrinsic reward is provided; the agent must rely entirely on intrinsic motivation signals.

### 2.2 LP-GARI Framework

#### 2.2.1 Component Intrinsic Rewards

**RND Intrinsic Reward:** Following Burda et al. (2019), we maintain a fixed randomly initialized target network $f_{\theta}$ and a predictor network $\hat{f}_{\phi}$. The RND intrinsic reward is:

$$r_{\text{RND}}(s) = \|\hat{f}_{\phi}(s) - f_{\theta}(s)\|^2$$

**DIAYN Intrinsic Reward:** Following Eysenbach et al. (2019), we sample skills $z \sim p(z)$ from a fixed prior and train a discriminator $q_{\psi}(z|s)$ to infer skills from states. The DIAYN intrinsic reward is:

$$r_{\text{DIAYN}}(s, z) = \log q_{\psi}(z|s) - \log p(z)$$

**Reward Normalization:** Both rewards are normalized using running statistics with a window of 1000 steps:

$$\tilde{r}(s) = \frac{r(s) - \mu_r}{\sigma_r + \epsilon}$$

where $\mu_r$ and $\sigma_r$ are the running mean and standard deviation, and $\epsilon = 10^{-8}$ prevents division by zero.

#### 2.2.2 Learning Progress Signals

We define three learning progress signals computed at each episode $t$:

**World Model Improvement ($\Delta_{\text{MSE}}$):** The change in world model prediction error:

$$\Delta_{\text{MSE}}(t) = \text{MSE}(t-1) - \text{MSE}(t)$$

normalized to $[-1, 1]$ using a running window.

**Skill Discriminator Accuracy Change ($\Delta_{\text{acc}}$):** The change in skill classification accuracy:

$$\Delta_{\text{acc}}(t) = \text{acc}(t) - \text{acc}(t-1)$$

**State Coverage Rate ($\rho_{\text{cov}}$):** The proportion of newly visited state clusters:

$$\rho_{\text{cov}}(t) = \frac{|\mathcal{C}_{\text{new}}(t)|}{|\mathcal{C}_{\text{total}}|}$$

where $\mathcal{C}_{\text{new}}(t)$ represents newly visited clusters and $\mathcal{C}_{\text{total}}$ is the total number of clusters (k=1000 via k-means).

#### 2.2.3 Adaptive Gating Mechanism

The gating network $g_{\omega}$ is a 2-layer MLP with 64 hidden units that receives the concatenated learning progress signals and outputs an adaptive weight:

$$\alpha(t) = \sigma\left(g_{\omega}\left([\Delta_{\text{MSE}}(t), \Delta_{\text{acc}}(t), \rho_{\text{cov}}(t)]\right)\right)$$

where $\sigma$ is the sigmoid function ensuring $\alpha(t) \in [0, 1]$.

The combined intrinsic reward is:

$$r_{\text{total}}(s, z, t) = \alpha(t) \cdot \tilde{r}_{\text{RND}}(s) + (1 - \alpha(t)) \cdot \tilde{r}_{\text{DIAYN}}(s, z)$$

#### 2.2.4 Gating Network Training

The gating network is trained via a self-supervised objective that maximizes the combined exploration-skill metric over a sliding window:

$$\mathcal{L}_{\text{gate}} = -\mathbb{E}_{t}\left[\lambda_1 \cdot \text{Coverage}(t:t+W) + \lambda_2 \cdot \text{Diversity}(t:t+W)\right]$$

where $W$ is the window size (default: 10 episodes) and $\lambda_1 = \lambda_2 = 0.5$ balance the objectives.

### 2.3 Complete Algorithm

**Algorithm 1: LP-GARI Training**

```
Initialize: Policy π_θ, RND networks (f_θ, f̂_φ), DIAYN discriminator q_ψ
Initialize: Gating network g_ω, replay buffer D, k-means clusters C
Initialize: Running statistics for reward normalization

For episode t = 1 to T:
    1. Sample skill z ~ p(z)
    2. Compute learning progress signals: Δ_MSE(t), Δ_acc(t), ρ_cov(t)
    3. Compute gating weight: α(t) = σ(g_ω([Δ_MSE(t), Δ_acc(t), ρ_cov(t)]))
    
    For step h = 1 to H:
        4. Select action a ~ π_θ(·|s, z)
        5. Execute action, observe s'
        6. Compute r_RND(s') and r_DIAYN(s', z)
        7. Normalize rewards: r̃_RND, r̃_DIAYN
        8. Compute combined reward: r_total = α(t)·r̃_RND + (1-α(t))·r̃_DIAYN
        9. Store (s, a, r_total, s', z) in D
        10. Update state coverage clusters C
    
    11. Update policy π_θ using SAC with rewards from D
    12. Update RND predictor f̂_φ
    13. Update DIAYN discriminator q_ψ
    14. Update gating network g_ω using L_gate
    
Return: Pre-trained policy π_θ
```

### 2.4 Experimental Design

#### 2.4.1 Environments

We evaluate LP-GARI on four MuJoCo continuous control environments of increasing complexity:

1. **HalfCheetah-v4:** 17-dimensional state space, 6-dimensional action space
2. **Ant-v4:** 27-dimensional state space, 8-dimensional action space
3. **Humanoid-v4:** 376-dimensional state space, 17-dimensional action space
4. **AntMaze-Large-v2:** Navigation task with sparse rewards

#### 2.4.2 Baselines

We compare LP-GARI against five baselines:

1. **RND-only:** Pure prediction-based exploration
2. **DIAYN-only:** Pure competence-based skill discovery
3. **Fixed-α (0.5):** Equal weighting of RND and DIAYN
4. **Fixed-α (optimal):** Best fixed weight found via grid search
5. **CIM:** Constrained Intrinsic Motivation (Zheng et al., 2024)

#### 2.4.3 Evaluation Metrics

**Primary Metrics:**

1. **State Coverage:** Percentage of k-means clusters (k=1000) visited during pre-training:
$$\text{Coverage} = \frac{|\{c \in \mathcal{C} : \exists s \in \mathcal{D}, s \in c\}|}{|\mathcal{C}|}$$

2. **Skill Diversity:** Discriminator accuracy as a proxy for mutual information $I(s;z)$:
$$\text{Diversity} = \mathbb{E}_{s,z}[\mathbf{1}[\arg\max_{z'} q_{\psi}(z'|s) = z]]$$

3. **Combined Score:** Weighted average of normalized metrics:
$$\text{Combined} = 0.5 \cdot \frac{\text{Coverage}}{\text{Coverage}_{\max}} + 0.5 \cdot \text{Diversity}$$

**Secondary Metrics:**

4. **Fine-tuning Efficiency:** Sample complexity to reach 90% of asymptotic task performance
5. **Gating Dynamics:** Correlation between $\alpha(t)$ and learning progress signals

#### 2.4.4 Experimental Protocol

**Pre-training Phase:**
- Duration: 2 million environment steps
- Number of skills: 50
- Policy architecture: 2-layer MLP (256 hidden units)
- Optimizer: Adam with learning rate $3 \times 10^{-4}$
- Random seeds: 20 independent runs per condition

**Fine-tuning Phase:**
- Downstream tasks: 5 goal-reaching tasks per environment
- Fine-tuning budget: 500,000 steps
- Evaluation: Average return over 100 episodes

#### 2.4.5 Statistical Analysis

- **Primary comparison:** Paired t-test with Bonferroni correction for 4 baseline comparisons
- **Significance level:** $\alpha = 0.05$ (two-tailed)
- **Effect size:** Cohen's d with 95% confidence intervals
- **Sample size justification:** n=20 provides 80% power to detect medium effect sizes (d=0.6)

### 2.5 Ablation Studies

To validate the causal mechanism, we conduct the following ablations:

1. **Random Gating:** Replace learned $\alpha(t)$ with uniform random sampling
2. **Single Signal:** Use only one learning progress signal at a time
3. **Frozen Gating:** Fix $\alpha$ after initial learning period
4. **Network Depth:** Compare 1, 2, and 3-layer gating networks

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence from related work, we anticipate the following outcomes:

**Primary Prediction (P1):** LP-GARI will achieve a combined exploration-skill score exceeding:
- RND-only by ≥15% (expected: 18-22%)
- DIAYN-only by ≥15% (expected: 16-20%)
- Fixed-weight (α=0.5) by ≥8% (expected: 10-12%)
- CIM by ≥5% (expected: 6-8%)

**Mechanism Prediction (P2):** The learned gating weights will exhibit systematic temporal dynamics:
- Early training (0-500K steps): $\alpha(t) > 0.6$ (favoring RND exploration)
- Mid training (500K-1.5M steps): $\alpha(t) \approx 0.4-0.6$ (balanced)
- Late training (1.5M-2M steps): $\alpha(t) < 0.4$ (favoring DIAYN skill refinement)
- Correlation with learning progress: $r > 0.3$

**Transfer Prediction (P3):** Fine-tuning efficiency improvements:
- 1.5-2x faster adaptation compared to RND pre-training
- 1.5-2x faster adaptation compared to DIAYN pre-training
- Consistent improvements across at least 3/5 downstream tasks

### 3.2 Potential Challenges and Mitigations

1. **Reward Scale Mismatch:** If normalization fails, one reward may dominate. Mitigation: Test multiple normalization windows and adaptive scaling.

2. **Gating Instability:** The gating network may oscillate. Mitigation: Add temporal smoothing and entropy regularization.

3. **Computational Overhead:** Maintaining both RND and DIAYN increases cost. Mitigation: Efficient implementation with shared representations.

### 3.3 Scientific Impact

This research contributes to the theoretical understanding of intrinsically motivated learning by:

1. **Formalizing the exploration-exploitation temporal dynamics** in open-ended learning settings
2. **Providing empirical evidence** for the role of learning progress signals in guiding adaptive behavior
3. **Establishing a new paradigm** for heterogeneous reward integration in reinforcement learning

### 3.4 Practical Impact

LP-GARI advances the development of autonomous learning systems by:

1. **Improving sample efficiency** in reward-free pre-training, reducing computational costs
2. **Enabling more flexible skill repertoires** that transfer better to downstream tasks
3. **Providing a modular framework** that can incorporate additional intrinsic motivation signals

### 3.5 Broader Implications

The success of LP-GARI would support the broader vision of intrinsically motivated open-ended learning (IMOL) by demonstrating that:

1. **Adaptive meta-learning of exploration strategies** is both feasible and beneficial
2. **Learning progress signals** provide sufficient information for autonomous curriculum design
3. **Integration of complementary learning paradigms** outperforms specialized approaches

This work opens avenues for future research on multi-objective intrinsic motivation, hierarchical skill discovery, and lifelong learning systems that continuously adapt their exploration strategies to their current knowledge state.

### 3.6 Limitations and Future Directions

We acknowledge several limitations that suggest directions for future work:

1. **Environment scope:** Testing is limited to MuJoCo; extension to visual observations and real robotics is needed
2. **Gating architecture:** The fixed MLP may be suboptimal; attention-based or recurrent architectures could improve performance
3. **Reward components:** Only RND and DIAYN are combined; incorporating additional signals (e.g., empowerment, information gain) may further improve results

Future work will address these limitations and explore the application of LP-GARI to more complex, realistic open-ended learning scenarios.