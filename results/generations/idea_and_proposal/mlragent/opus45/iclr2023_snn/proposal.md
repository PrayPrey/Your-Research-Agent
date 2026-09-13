# Research Proposal: Dynamic Sparsity Scheduling for Sustainable Reinforcement Learning

## 1. Introduction

### Background

Deep reinforcement learning (DRL) has emerged as a powerful paradigm for solving complex sequential decision-making problems, achieving remarkable success in domains ranging from game playing to robotic manipulation and autonomous driving. However, this success comes at a substantial computational cost. Training state-of-the-art RL agents often requires millions to billions of environment interactions, consuming enormous amounts of energy and computational resources. For instance, training a single agent for Atari games can require days of GPU computation, while more complex domains like robotic control or multi-agent systems demand even greater resources. This computational intensity raises serious concerns about the sustainability and environmental impact of RL research and deployment.

The machine learning community has increasingly recognized the importance of developing sustainable and efficient training methods. Network sparsity—reducing the number of active parameters through pruning or sparse training—has demonstrated significant promise in supervised learning settings, achieving substantial compression ratios while maintaining model performance. However, the application of sparsity techniques to reinforcement learning remains largely underexplored, primarily due to the unique challenges posed by RL's learning dynamics.

Unlike supervised learning, where the data distribution remains fixed, RL exhibits inherently non-stationary learning dynamics. As the agent's policy improves, the distribution of visited states and collected experiences shifts continuously. Early training phases require the network to maintain sufficient capacity for exploring diverse behavioral strategies, while later phases benefit from focused, refined representations. This temporal heterogeneity in learning requirements makes static pruning approaches—which fix network structure throughout training—fundamentally mismatched to RL's needs.

Recent research has begun illuminating the relationship between sparsity and RL. Studies have revealed that RL fine-tuning naturally induces parameter update sparsity, with only 5-30% of parameters receiving significant updates (Mukherjee et al., 2025; Balashov, 2025). Furthermore, research by Ma et al. (2025) demonstrates that static network sparsity can unlock scaling potential in DRL by mitigating optimization challenges like plasticity loss. These findings suggest that RL models may inherently benefit from sparse structures, yet current methods fail to exploit this insight dynamically across training phases.

### Research Objectives

This research proposes **Adaptive Density Reinforcement Learning (ADRL)**, a novel framework that dynamically adjusts network sparsity throughout RL training based on automatic learning phase detection. Our primary objectives are:

1. To develop a principled method for detecting distinct learning phases in RL training (exploration, refinement, and convergence) using observable training statistics.

2. To design an adaptive sparsity scheduling mechanism that modulates network density according to the detected learning phase, enabling aggressive compression during convergence while maintaining capacity during exploration.

3. To introduce a reversible pruning mechanism using soft masks that allows temporary restoration of pruned connections when the agent encounters novel states or distribution shifts.

4. To empirically validate ADRL across diverse RL benchmarks, demonstrating significant computational savings while maintaining competitive performance.

### Significance

This research addresses a critical gap at the intersection of sustainable machine learning and reinforcement learning. By developing phase-aware dynamic sparsity methods tailored to RL's unique characteristics, we aim to reduce the computational footprint of RL training by 3-5× without sacrificing task performance. This contribution directly supports the deployment of RL in resource-constrained settings such as edge robotics and embedded autonomous systems, where both computational efficiency and learning capability are paramount. Furthermore, our work provides practical guidelines for green RL deployment, contributing to the broader goal of environmentally sustainable AI development.

## 2. Methodology

### 2.1 Overview of the ADRL Framework

The ADRL framework consists of three interconnected components: (1) a Phase Detection Module that monitors training dynamics to identify learning phases, (2) a Sparsity Scheduling Controller that adjusts target sparsity levels based on detected phases, and (3) a Reversible Pruning Mechanism that implements soft masks enabling dynamic capacity adjustment. These components operate alongside any standard RL algorithm (e.g., PPO, SAC, DQN), providing a modular and algorithm-agnostic approach to sustainable RL training.

### 2.2 Phase Detection Module

We model RL training as progressing through three distinct phases, each with characteristic signatures in training statistics:

**Phase 1 - Exploration:** High policy entropy, high reward variance, large gradient magnitudes with high variance. The agent is discovering the state space and requires maximum representational capacity.

**Phase 2 - Refinement:** Decreasing policy entropy, stabilizing reward variance, consistent gradient directions. The agent is refining its policy and benefits from focused representations.

**Phase 3 - Convergence:** Low policy entropy, low reward variance, diminishing gradient magnitudes. The agent has converged to a near-optimal policy and tolerates aggressive compression.

We define a phase indicator vector $\phi_t \in \mathbb{R}^4$ computed at each training iteration $t$:

$$\phi_t = \left[ H(\pi_t), \sigma^2(R_t), \|\nabla_\theta \mathcal{L}_t\|_2, \text{Var}(\nabla_\theta \mathcal{L}_t) \right]$$

where $H(\pi_t)$ is the policy entropy, $\sigma^2(R_t)$ is the episodic reward variance computed over a rolling window, $\|\nabla_\theta \mathcal{L}_t\|_2$ is the gradient norm, and $\text{Var}(\nabla_\theta \mathcal{L}_t)$ captures gradient variance across parameters.

The Phase Detection Module employs a lightweight meta-controller implemented as a small neural network $f_\psi: \mathbb{R}^{4 \times W} \rightarrow \{1, 2, 3\}$ that takes the last $W$ phase indicator vectors and outputs a phase classification:

$$p_t = f_\psi(\phi_{t-W+1:t})$$

The meta-controller is trained online using a self-supervised objective based on change-point detection in the smoothed phase indicators.

### 2.3 Sparsity Scheduling Controller

Based on the detected phase $p_t$, the Sparsity Scheduling Controller determines a target sparsity ratio $s_t \in [0, 1]$, where $s_t = 0$ indicates a fully dense network and $s_t = 1$ indicates complete sparsity. We define phase-specific target sparsities:

$$s^{(1)} = 0.3, \quad s^{(2)} = 0.6, \quad s^{(3)} = 0.9$$

To ensure smooth transitions and training stability, the actual sparsity level follows an exponential moving average:

$$s_t = \alpha \cdot s^{(p_t)} + (1 - \alpha) \cdot s_{t-1}$$

where $\alpha \in (0, 1)$ controls the transition speed. We additionally impose rate constraints to prevent abrupt capacity changes:

$$|s_t - s_{t-1}| \leq \delta_{\max}$$

where $\delta_{\max}$ is a hyperparameter controlling maximum per-iteration sparsity change.

### 2.4 Reversible Pruning with Soft Masks

Unlike hard pruning methods that permanently remove connections, ADRL employs soft masks that allow reversible capacity adjustment. For each layer $l$ with weights $W^{(l)} \in \mathbb{R}^{m \times n}$, we maintain a continuous mask matrix $M^{(l)} \in [0, 1]^{m \times n}$. The effective weights are computed as:

$$\tilde{W}^{(l)} = W^{(l)} \odot M^{(l)}$$

where $\odot$ denotes element-wise multiplication.

The mask values are determined by learned importance scores $I^{(l)} \in \mathbb{R}^{m \times n}$, updated based on gradient magnitude accumulated over training:

$$I^{(l)}_t = \beta \cdot I^{(l)}_{t-1} + (1 - \beta) \cdot \left| \frac{\partial \mathcal{L}_t}{\partial W^{(l)}} \right|$$

Given the target sparsity $s_t$, we compute a threshold $\tau_t$ such that the proportion of parameters with importance below $\tau_t$ equals $s_t$. The mask is then computed using a temperature-controlled sigmoid:

$$M^{(l)}_{ij} = \sigma\left( \frac{I^{(l)}_{ij} - \tau_t}{T} \right)$$

where $T$ is a temperature parameter controlling mask sharpness.

**Novelty Detection and Mask Restoration:** When the agent encounters novel states (detected via high prediction uncertainty or significant TD-error spikes), the masks can be temporarily relaxed to restore capacity:

$$\tilde{M}^{(l)} = M^{(l)} + \gamma \cdot \mathbb{1}[\text{novelty detected}] \cdot (1 - M^{(l)})$$

where $\gamma \in [0, 1]$ controls restoration magnitude.

### 2.5 Complete ADRL Algorithm

The complete ADRL training procedure is summarized in Algorithm 1:

**Algorithm 1: Adaptive Density Reinforcement Learning (ADRL)**

1. Initialize policy network $\pi_\theta$, value network $V_\omega$, importance scores $I^{(l)}$, masks $M^{(l)} = 1$
2. Initialize phase detection meta-controller $f_\psi$, sparsity $s_0 = s^{(1)}$
3. **For** each training iteration $t = 1, 2, \ldots, T$:
   - Collect experience using current policy with masked weights $\tilde{W}$
   - Compute phase indicators $\phi_t$
   - Detect learning phase: $p_t = f_\psi(\phi_{t-W+1:t})$
   - Update target sparsity: $s_t = \text{clip}(\alpha \cdot s^{(p_t)} + (1-\alpha) \cdot s_{t-1}, s_{t-1} - \delta_{\max}, s_{t-1} + \delta_{\max})$
   - Update importance scores: $I^{(l)}_t = \beta \cdot I^{(l)}_{t-1} + (1-\beta) \cdot |\nabla_{W^{(l)}} \mathcal{L}_t|$
   - Compute threshold $\tau_t$ from $s_t$ and importance distribution
   - Update masks: $M^{(l)} = \sigma((I^{(l)}_t - \tau_t)/T)$
   - **If** novelty detected: apply mask restoration
   - Perform RL update (PPO/SAC/DQN) on masked network
4. **Return** final sparse policy $\pi_{\theta, M}$

### 2.6 Experimental Design

**Benchmarks:** We evaluate ADRL on three benchmark suites covering diverse RL domains:
- *Discrete Control:* Atari games (Pong, Breakout, Seaquest, BeamRider)
- *Continuous Control:* MuJoCo tasks (HalfCheetah, Walker2d, Ant, Humanoid)
- *Sample-Efficient RL:* DeepMind Control Suite with limited interactions

**Baselines:** We compare against:
- Dense baselines (PPO, SAC) without any sparsification
- Static pruning at various sparsity levels (30%, 60%, 90%)
- Gradual Magnitude Pruning (GMP) applied to RL
- Sparse Evolutionary Training (SET) adapted for RL
- RigL (dynamic sparse training)

**Evaluation Metrics:**
- *Performance:* Final episode return, normalized score
- *Efficiency:* Training FLOPs, wall-clock time, GPU memory usage
- *Compression:* Achieved sparsity ratio, effective parameter count
- *Sustainability:* Estimated energy consumption (kWh), carbon footprint (kg CO₂)

**Ablation Studies:** We conduct ablations on:
- Phase detection accuracy and sensitivity to hyperparameters
- Impact of soft vs. hard masking
- Reversible pruning effectiveness under distribution shift
- Sparsity schedule sensitivity ($s^{(1)}, s^{(2)}, s^{(3)}$ values)

**Statistical Rigor:** All experiments are repeated across 10 random seeds. We report mean performance with 95% confidence intervals and conduct statistical significance tests (Welch's t-test) for comparisons.

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following quantitative outcomes from our experimental evaluation:

1. **Computational Efficiency:** ADRL is expected to achieve a 3-5× reduction in training FLOPs compared to dense baselines while maintaining performance within 5% of dense network returns. We project wall-clock speedups of 2-3× on standard GPU hardware.

2. **Adaptive Compression:** The framework should demonstrate intelligent sparsity scheduling, achieving average sparsities of approximately 30% during exploration phases, 60% during refinement, and up to 90% during convergence, with smooth transitions between phases.

3. **Robustness:** The reversible pruning mechanism is expected to improve robustness to distribution shifts, with agents recovering performance 30-50% faster than statically pruned networks when encountering novel states.

4. **Phase Detection Accuracy:** The meta-controller should achieve >85% accuracy in phase classification, validated against ground-truth phase labels derived from reward curve analysis.

### Broader Impact

**Sustainability in Machine Learning:** By demonstrating that RL training can be made significantly more efficient through intelligent sparsity scheduling, this research contributes directly to sustainable AI development. Reduced computational requirements translate to lower energy consumption and carbon emissions, supporting broader environmental goals.

**Enabling Edge Deployment:** ADRL's efficiency gains facilitate RL deployment in resource-constrained environments such as mobile robots, IoT devices, and embedded systems where computational budgets are limited but adaptive learning remains desirable.

**Theoretical Insights:** Our work provides empirical evidence for the hypothesis that RL learning dynamics exhibit phase-structured behavior amenable to compression, potentially informing theoretical analyses of RL optimization landscapes.

**Practical Guidelines:** We will release comprehensive guidelines for practitioners, including hyperparameter recommendations, phase detection tuning procedures, and best practices for applying dynamic sparsity to new RL domains.

**Open-Source Contribution:** All code, trained models, and experimental logs will be released publicly to promote reproducibility and enable the community to build upon our work.

In conclusion, ADRL represents a principled approach to reconciling the computational demands of reinforcement learning with sustainability imperatives, offering both practical efficiency gains and foundational insights into the relationship between network capacity and RL learning dynamics.