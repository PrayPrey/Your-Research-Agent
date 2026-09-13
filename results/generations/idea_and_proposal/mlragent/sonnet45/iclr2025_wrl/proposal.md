# Research Proposal: Curriculum Learning through Failure Mode Mining for Robust Household Robot Manipulation

## 1. Title

**Adaptive Curriculum Learning via Automated Failure Mode Discovery and Synthesis for Robust Household Robot Manipulation**

## 2. Introduction

### 2.1 Background

The deployment of robots in household environments represents one of the most challenging frontiers in robotics and artificial intelligence. Unlike structured industrial settings, homes present unstructured, dynamic environments with high variability in object properties, lighting conditions, spatial configurations, and task requirements. While recent advances in robot learning have demonstrated impressive performance on specific manipulation tasks, these systems often fail when encountering edge cases and rare scenarios that were not adequately represented in training data.

The fundamental challenge lies in the long-tail distribution of household scenarios. A robot may successfully complete thousands of manipulation tasks—picking up cups, opening drawers, or placing dishes—only to fail catastrophically when encountering a slightly wet surface, an unexpectedly lightweight object, or unusual clutter configuration. These rare but critical failure modes are difficult to anticipate during system design and expensive to capture through exhaustive real-world data collection. Current approaches typically rely on either: (1) massive datasets that attempt to cover all possible scenarios, requiring prohibitive amounts of real-world interaction data, or (2) extensive domain randomization in simulation that may introduce irrelevant variations while missing critical failure modes.

### 2.2 Research Objectives

This research proposes a systematic framework for discovering, synthesizing, and learning from failure modes to develop robust household manipulation policies. Our primary objectives are:

1. **Develop automated failure mode discovery methods** that efficiently identify critical scenarios where current policies exhibit unreliable behavior through a combination of uncertainty quantification and anomaly detection in both simulated and limited real-world deployments.

2. **Create adversarial scenario generation techniques** that synthesize diverse, challenging variations of discovered failure modes using generative models guided by real failure statistics and physical constraints.

3. **Design adaptive curriculum learning strategies** that dynamically construct training sequences balancing successful task completion with targeted exposure to failure modes, progressively building robust policies.

4. **Establish sim-to-real validation protocols** that ensure failure modes discovered in simulation transfer meaningfully to real-world settings with minimal real-world data requirements.

5. **Demonstrate significant improvements in robot robustness** on household manipulation tasks while maintaining high data efficiency compared to baseline approaches.

### 2.3 Significance

This research addresses a critical bottleneck in deploying robots for household assistance. By systematically discovering and learning from failure modes rather than relying on exhaustive data collection or blind domain randomization, our approach promises to:

- **Dramatically reduce real-world data requirements** for training robust manipulation policies, making household robot development more accessible and cost-effective.
- **Improve safety and reliability** by explicitly targeting rare but critical failure scenarios that could lead to damage or unsafe behaviors.
- **Accelerate the development cycle** for household robots by providing automated tools for identifying and addressing robustness gaps.
- **Contribute generalizable methods** applicable beyond household manipulation to other domains requiring robust operation in long-tail distributions.

The proposed framework aligns perfectly with the Robot Learning Workshop's theme of achieving human-level robotic abilities, as humans naturally learn from failures and edge cases to develop robust skills for everyday activities.

## 3. Methodology

### 3.1 Overall Framework Architecture

Our methodology consists of four interconnected components operating in a closed-loop system: (1) Failure Mode Mining, (2) Adversarial Scenario Generation, (3) Adaptive Curriculum Construction, and (4) Policy Learning with Sim-to-Real Transfer. These components iteratively refine the robot's capabilities through progressive exposure to discovered failure modes.

### 3.2 Failure Mode Mining

#### 3.2.1 Uncertainty-Based Failure Detection

We employ ensemble-based uncertainty estimation to identify scenarios where the policy exhibits high epistemic uncertainty. Given a policy network $\pi_\theta(a|s)$, we train an ensemble of $N$ policies $\{\pi_{\theta_1}, ..., \pi_{\theta_N}\}$ and compute the action disagreement:

$$U_{ensemble}(s) = \frac{1}{N}\sum_{i=1}^{N} D_{KL}(\pi_{\theta_i}(a|s) || \bar{\pi}(a|s))$$

where $\bar{\pi}(a|s) = \frac{1}{N}\sum_{i=1}^{N}\pi_{\theta_i}(a|s)$ is the average policy. Scenarios with $U_{ensemble}(s) > \tau_u$ are flagged as high-uncertainty failure candidates.

#### 3.2.2 Outcome-Based Failure Detection

We define task-specific success metrics $M(s, a, s')$ evaluating whether a state transition achieves desired outcomes. For manipulation tasks, this includes:

- **Grasp stability**: $M_{grasp} = \mathbb{1}[\text{force}_{\text{gripper}} \in [\text{force}_{\text{min}}, \text{force}_{\text{max}}]]$
- **Object displacement**: $M_{place} = \mathbb{1}[\|p_{\text{object}} - p_{\text{goal}}\| < \epsilon]$
- **Collision avoidance**: $M_{collision} = \mathbb{1}[\text{contact}_{\text{unexpected}} = 0]$

A trajectory $\tau = (s_0, a_0, ..., s_T)$ is classified as a failure if the final success rate $S(\tau) = \sum_{t} M(s_t, a_t, s_{t+1}) / T < \tau_s$.

#### 3.2.3 Anomaly Detection in State-Action Space

We train a variational autoencoder (VAE) on successful trajectories to model the distribution of nominal behavior. The reconstruction error serves as an anomaly score:

$$\mathcal{A}(s, a) = \|[(s, a)] - \text{VAE}_\phi(s, a)\|^2 + D_{KL}(q_\phi(z|s,a) || p(z))$$

State-action pairs with $\mathcal{A}(s, a) > \tau_a$ represent distributional anomalies indicative of potential failure modes.

#### 3.2.4 Failure Mode Clustering and Characterization

Detected failure instances are embedded using a learned feature extractor $f_\psi: (s, a, s') \rightarrow \mathbb{R}^d$ and clustered using DBSCAN to identify distinct failure mode categories. Each cluster $C_k$ represents a coherent failure mode characterized by:

- **Triggering conditions**: Common state features preceding failure
- **Failure signature**: Characteristic policy behaviors during failure
- **Physical parameters**: Object properties, environmental conditions

### 3.3 Adversarial Scenario Generation

#### 3.3.1 Conditional Generative Model

For each identified failure mode cluster $C_k$, we train a conditional variational autoencoder (CVAE) to generate variations:

$$p_\xi(s_{\text{new}}|C_k) = \int p_\xi(s_{\text{new}}|z, C_k)p(z)dz$$

The CVAE is trained to maximize:

$$\mathcal{L}_{\text{CVAE}} = \mathbb{E}_{s \sim C_k}[\log p_\xi(s|z, C_k)] - D_{KL}(q_\xi(z|s, C_k) || p(z))$$

#### 3.3.2 Physics-Guided Domain Randomization

Generated scenarios are constrained by physical plausibility using a discriminator $D_\omega$ trained to distinguish between real and generated scenarios:

$$\mathcal{L}_{\text{GAN}} = \mathbb{E}_{s \sim p_{\text{real}}}[\log D_\omega(s)] + \mathbb{E}_{s \sim p_\xi}[\log(1 - D_\omega(s))]$$

We further impose physical constraints on randomization parameters:
- Object mass: $m \in [0.05, 5.0]$ kg sampled from failure mode statistics
- Friction coefficients: $\mu \sim \mathcal{N}(\mu_k, \sigma_k)$ learned from cluster $C_k$
- Lighting and texture variations guided by image-based failure examples

#### 3.3.3 Difficulty Progression Modeling

We train a difficulty predictor $R_\gamma: s \rightarrow [0, 1]$ estimating the probability of policy failure for a given scenario using a gradient-boosted tree on features including:
- Uncertainty metrics from the ensemble
- Object property deviations from training distribution
- Workspace clutter density

This enables controlled generation of scenarios at specific difficulty levels.

### 3.4 Adaptive Curriculum Construction

#### 3.4.1 Curriculum Scheduling Strategy

We formulate curriculum learning as a multi-armed bandit problem where each arm corresponds to a difficulty level or failure mode category. The curriculum policy $\pi_C$ selects the next training scenario distribution based on:

$$\pi_C = \arg\max_{\text{difficulty} \in \mathcal{D}} \text{UCB}(\text{difficulty}) = \bar{r}_{\text{difficulty}} + \beta\sqrt{\frac{\log N}{n_{\text{difficulty}}}}$$

where $\bar{r}_{\text{difficulty}}$ is the average learning progress (measured as success rate improvement) for scenarios at that difficulty level, and $n_{\text{difficulty}}$ is the number of times it has been selected.

#### 3.4.2 Learning Progress Estimation

Learning progress for a scenario distribution is computed as:

$$LP(C_k, t) = \frac{1}{|\mathcal{B}|}\sum_{s \sim C_k} [S_t(s) - S_{t-\Delta t}(s)]$$

where $S_t(s)$ is the current success rate on scenarios from cluster $C_k$ and $\mathcal{B}$ is a buffer of recent scenarios.

#### 3.4.3 Curriculum Mixture Distribution

At training iteration $t$, scenarios are sampled from a mixture distribution:

$$p_{\text{train}}(s) = \alpha_t p_{\text{nominal}}(s) + \sum_{k} \beta_k(t) p_{\text{failure}_k}(s) + \gamma_t p_{\text{adversarial}}(s)$$

where:
- $p_{\text{nominal}}$ represents standard task scenarios
- $p_{\text{failure}_k}$ samples from discovered failure mode cluster $k$
- $p_{\text{adversarial}}$ samples from generated adversarial scenarios
- Weights $\{\alpha_t, \beta_k(t), \gamma_t\}$ are updated based on learning progress

### 3.5 Policy Learning

#### 3.5.1 Base Policy Architecture

We employ a transformer-based policy architecture processing multimodal observations:

$$\pi_\theta(a|s) = \text{Transformer}([h_{\text{vision}}, h_{\text{proprio}}, h_{\text{force}}])$$

where:
- $h_{\text{vision}} = \text{ResNet}(o_{\text{rgb}}, o_{\text{depth}})$ encodes visual observations
- $h_{\text{proprio}}$ encodes joint positions and velocities
- $h_{\text{force}}$ encodes force-torque sensor readings

#### 3.5.2 Training Objective

The policy is trained using Proximal Policy Optimization (PPO) with an augmented reward incorporating robustness metrics:

$$\mathcal{L}_{\text{policy}} = \mathbb{E}_{\tau}[r_{\text{task}} + \lambda_r r_{\text{robustness}} - \lambda_e H(\pi_\theta)]$$

where:
- $r_{\text{task}}$ is the task-specific reward (e.g., successful grasp, accurate placement)
- $r_{\text{robustness}} = -\alpha \cdot U_{ensemble}(s) - \beta \cdot \mathcal{A}(s,a)$ penalizes uncertain/anomalous behaviors
- $H(\pi_\theta)$ is the policy entropy for exploration

### 3.6 Sim-to-Real Transfer and Validation

#### 3.6.1 Failure Mode Transfer Validation

We establish a real-world test suite containing instances from each discovered failure mode cluster. For each cluster $C_k$, we collect $n_{\text{real}} = 50$ real-world examples and measure:

$$\text{Transfer-Gap}(C_k) = |S_{\text{sim}}(C_k) - S_{\text{real}}(C_k)|$$

Failure modes with Transfer-Gap $> 0.3$ are prioritized for additional domain randomization or real-world data collection.

#### 3.6.2 Progressive Real-World Deployment

We employ a staged deployment strategy:
1. **Stage 1**: Evaluate on real-world nominal scenarios (100 trials)
2. **Stage 2**: Evaluate on manually curated failure mode examples (50 trials per mode)
3. **Stage 3**: Deploy with human supervision collecting natural failures (200 hours)
4. **Stage 4**: Incorporate discovered real-world failures into next training iteration

#### 3.6.3 Domain Adaptation

For identified sim-to-real gaps, we apply domain adaptation using a small amount of real-world data:

$$\mathcal{L}_{\text{adapt}} = \mathcal{L}_{\text{policy}}^{\text{real}} + \lambda_{DA}\sum_{l}\|f_l^{\text{sim}} - f_l^{\text{real}}\|^2$$

where $f_l$ represents intermediate feature representations and the domain alignment term encourages similar representations across domains.

### 3.7 Experimental Design

#### 3.7.1 Simulation Environment

We implement our approach in Isaac Gym with household manipulation tasks:
- **Task 1**: Multi-object pick-and-place with varying object properties (50 objects, mass range 0.05-2kg, friction 0.2-0.8)
- **Task 2**: Drawer opening with various resistance levels and handle types (15 variations)
- **Task 3**: Dishwasher loading requiring precise placement under constraints (plates, cups, utensils)

#### 3.7.2 Real-World Platform

Real-world experiments use:
- **Robot**: Franka Emika Panda with WSG-50 gripper
- **Sensors**: Wrist-mounted RGB-D camera (Intel RealSense D435), F/T sensor (ATI Nano17)
- **Objects**: YCB object set plus 20 common household items

#### 3.7.3 Baseline Comparisons

We compare against:
1. **Standard RL**: PPO without curriculum or failure mining
2. **Random Domain Randomization**: Uniform randomization of parameters
3. **Manual Curriculum**: Expert-designed progression of difficulty
4. **Uniform Failure Sampling**: Equal sampling from all discovered failure modes without adaptive weighting
5. **DAGGER**: Interactive data collection without explicit failure mode modeling

#### 3.7.4 Evaluation Metrics

**Primary Metrics**:
- **Overall Success Rate**: Percentage of successful task completions across all scenarios
- **Failure Mode Coverage**: Percentage of identified failure modes with success rate $> 0.8$
- **Robustness Score**: Average success rate on out-of-distribution test scenarios

**Secondary Metrics**:
- **Sample Efficiency**: Number of environment interactions to reach target performance
- **Real-World Data Requirements**: Number of real-world interactions needed for successful deployment
- **Adaptation Speed**: Iterations required to recover from newly discovered failure modes

**Evaluation Protocol**:
For each method, we conduct:
- 10,000 simulated evaluation episodes across difficulty levels
- 500 real-world trials (100 nominal + 400 failure mode instances)
- Statistical significance testing using bootstrap confidence intervals

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Improvements**: We anticipate our approach will achieve:
- **30-50% improvement** in overall success rate on household manipulation tasks compared to standard RL, particularly on long-tail scenarios
- **3-5x reduction** in real-world data requirements compared to methods requiring exhaustive real-world collection
- **20-30% better robustness** on out-of-distribution test scenarios compared to random domain randomization
- **Faster convergence** with 40-60% fewer training iterations to reach target performance levels

**Qualitative Outcomes**:
- **Automated failure discovery system** capable of identifying 15-20 distinct failure mode categories per task without human annotation
- **Transferable failure modes**: At least 70% of simulated failure modes demonstrate meaningful transfer to real-world settings
- **Interpretable failure characterization**: Clear clustering and feature attribution for each failure mode enabling targeted intervention
- **Scalable curriculum framework**: Demonstrated applicability across multiple manipulation tasks with minimal task-specific tuning

**Deliverables**:
- Open-source implementation of the complete framework including failure mining, scenario generation, and curriculum construction modules
- Benchmark dataset of discovered failure modes in household manipulation with both simulated and real-world instances
- Pre-trained models and curriculum schedules for common household tasks
- Comprehensive ablation studies quantifying the contribution of each component

### 4.2 Scientific Impact

**Advancing Robot Learning Theory**: This research contributes to fundamental understanding of:
- How to efficiently explore and learn from long-tail distributions in embodied AI
- The relationship between failure mode diversity and policy robustness
- Optimal strategies for balancing exploitation (mastering known scenarios) and exploration (discovering failures)
- Principles for effective sim-to-real transfer in safety-critical applications

**Methodological Contributions**:
- Novel combination of uncertainty quantification, anomaly detection, and generative modeling for automated failure discovery
- Theoretically grounded curriculum learning framework with provable convergence properties under certain assumptions
- Practical techniques for validating sim-to-real transfer of rare events

### 4.3 Practical Impact

**Accelerating Household Robot Development**: Our framework directly addresses the deployment gap by:
- Providing automated tools for identifying robustness issues early in development
- Reducing the cost and time required for real-world testing and validation
- Enabling safer deployment through systematic exposure to potential failures during training

**Broader Applicability**: While focused on household manipulation, our methods generalize to:
- **Autonomous vehicles**: Discovering and training for rare traffic scenarios
- **Medical robotics**: Ensuring reliability across patient variability
- **Warehouse automation**: Handling diverse object properties and configurations
- **Assistive robotics**: Adapting to individual user needs and environments

**Industry Adoption Potential**: The framework's emphasis on data efficiency and automated discovery makes it particularly attractive for commercial robotics applications where real-world data collection is expensive and time-consuming.

### 4.4 Future Research Directions

This work opens several promising research avenues:
- **Continual learning from failures**: Extending the framework to continuously discover and adapt to new failure modes during deployment
- **Transfer across embodiments**: Investigating whether failure modes discovered for one robot transfer to different embodiments
- **Human-in-the-loop failure discovery**: Incorporating human feedback to identify safety-critical failure modes that may not be statistically frequent
- **Theoretical analysis**: Developing formal guarantees on robustness and sample complexity under the proposed curriculum learning framework
- **Multi-task failure mode sharing**: Exploring how failure modes discovered in one task can inform learning in related tasks

### 4.5 Workshop Relevance

This proposal directly addresses the workshop's central question: "How far are we from robots with human-level abilities?" by tackling one of the key gaps—robust operation in the face of rare but critical edge cases. Humans excel at learning from failures and exceptional cases; our framework brings this capability to robot learning systems. By demonstrating significant improvements in robustness with minimal real-world data requirements, we move closer to robots that can reliably perform everyday household activities "without much thinking," as humans do.

The interdisciplinary nature of our approach—combining curriculum learning, generative modeling, uncertainty quantification, and sim-to-real transfer—exemplifies the diverse perspectives the workshop seeks to attract, while our focus on practical deployment addresses the workshop's emphasis on real-world applications and system integration.