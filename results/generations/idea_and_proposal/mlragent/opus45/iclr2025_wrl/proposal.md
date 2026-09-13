# Research Proposal

## Title
Adaptive Skill Primitives via Multi-Modal Foundation Models for Zero-Shot Task Generalization in Unstructured Environments

## 1. Introduction

### Background

The pursuit of robots with human-level abilities represents one of the most ambitious frontiers in artificial intelligence and robotics research. While humans effortlessly perform everyday activities such as cooking, cleaning, and organizing—tasks that involve complex reasoning, perception, and motor coordination—current robotic systems struggle to generalize beyond narrowly defined scenarios. The year 2024 has witnessed remarkable progress in specialized domains, including drone racing and table tennis, demonstrating that achieving human-level performance in specific tasks is attainable. However, the broader challenge of creating generally capable robots that can robustly operate in unstructured environments like homes remains largely unsolved.

Recent advances in large multi-modal foundation models (e.g., GPT-4V, Gemini, LLaVA) have revolutionized natural language understanding and visual reasoning, enabling unprecedented capabilities in parsing complex instructions and understanding diverse visual scenes. Simultaneously, the robotics community has made significant strides in sim-to-real transfer, enabling motor skills learned in simulation to be deployed on physical robots. Yet, a critical gap persists between semantic task comprehension and reliable motor execution—the ability to translate high-level understanding into precise, adaptive physical actions in novel situations.

Existing literature reveals several persistent challenges. Zhou et al. (2023) demonstrated that language-conditioned approaches with base skill priors can improve zero-shot performance, but their methods require substantial task-specific training data. The Robot Utility Models framework (Etukuru et al., 2024) achieved impressive generalization but emphasized the necessity of diverse, high-quality training data at scale. Furthermore, investigations into foundation models like RT-1-X (Salzer & Visser, 2024) revealed significant limitations in zero-shot generalization to unseen robot morphologies. The theoretical analysis by researchers studying pretraining concept frequency (2024) underscores that achieving zero-shot generalization requires exponentially more data, highlighting fundamental sample inefficiency in current approaches.

### Research Objectives

This research proposes a novel hierarchical framework—**Adaptive Skill Primitives (ASP)**—that bridges the gap between semantic understanding from foundation models and reliable motor execution through composable skill primitives. Our specific objectives are:

1. **Develop a hierarchical architecture** that leverages frozen multi-modal foundation models for task decomposition while maintaining a library of transferable motor skill primitives.

2. **Design lightweight adapter networks** that efficiently map semantic representations to primitive parameters, enabling real-time adaptation to novel scenarios.

3. **Create an automatic curriculum generation system** for training adapters on diverse simulated tasks, maximizing generalization to unseen instructions.

4. **Establish comprehensive evaluation protocols** on a standardized household task suite spanning 50+ activities to benchmark zero-shot generalization capabilities.

### Significance

This research addresses fundamental challenges in achieving human-level robot adaptability. By decoupling high-level semantic reasoning from low-level motor execution, our framework offers several advantages: (1) leveraging the vast knowledge encoded in foundation models without expensive fine-tuning, (2) enabling compositional generalization through modular skill primitives, and (3) improving sample efficiency through curriculum-based adapter training. Success in this endeavor would significantly advance deployable home assistance robots, directly impacting applications in elderly care, household management, and accessibility assistance.

## 2. Methodology

### 2.1 System Architecture Overview

The ASP framework consists of three interconnected components operating in a hierarchical manner:

**Layer 1: Semantic Task Parser (STP)** — A frozen multi-modal foundation model that processes natural language instructions and visual observations to generate structured subtask decompositions.

**Layer 2: Primitive Library (PL)** — A collection of pre-trained, composable motor skills learned via sim-to-real transfer, each parameterized for flexible execution.

**Layer 3: Semantic-Motor Adapter (SMA)** — A lightweight neural network that maps semantic representations to primitive parameters conditioned on real-time perceptual input.

### 2.2 Semantic Task Parser

We utilize a frozen vision-language model $\mathcal{F}$ (e.g., GPT-4V) that takes as input a task instruction $\tau$ and visual observation $I_t$ at time $t$, producing a structured subtask sequence:

$$\mathcal{S} = \mathcal{F}(\tau, I_t) = \{(s_1, o_1), (s_2, o_2), \ldots, (s_n, o_n)\}$$

where each tuple $(s_i, o_i)$ represents a subtask identifier $s_i \in \mathcal{P}$ (mapping to a primitive in our library) and an object specification $o_i$ extracted from the scene. We employ structured prompting with chain-of-thought reasoning to ensure consistent output formatting:

```
Given the instruction "{τ}" and the current scene, decompose the task into 
primitive actions from: {GRASP, PLACE, POUR, WIPE, PUSH, ROTATE, OPEN, CLOSE}.
For each action, specify the target object and relevant parameters.
```

To enhance spatial reasoning capabilities—a key challenge identified by SpatialVLM (2024)—we augment the visual input with depth information and bounding box annotations from an off-the-shelf object detector, creating a structured scene representation.

### 2.3 Primitive Library Design

The Primitive Library $\mathcal{P} = \{p_1, p_2, \ldots, p_K\}$ contains $K$ parameterized motor skills. Each primitive $p_k$ is defined as a policy:

$$\pi_k(a_t | s_t, \theta_k)$$

where $s_t$ represents the robot state, $a_t$ is the action, and $\theta_k$ are skill-specific parameters. We define eight core primitives essential for household manipulation:

| Primitive | Parameters $\theta_k$ | Description |
|-----------|----------------------|-------------|
| GRASP | pose, aperture, force | Prehensile grasping |
| PLACE | target_pose, release_height | Controlled placement |
| POUR | angle, rate, duration | Liquid transfer |
| WIPE | trajectory, pressure, cycles | Surface cleaning |
| PUSH | direction, distance, force | Non-prehensile manipulation |
| ROTATE | axis, angle, grip_force | In-hand rotation |
| OPEN | handle_pose, arc_angle | Articulated object opening |
| CLOSE | handle_pose, final_angle | Articulated object closing |

Each primitive is trained using reinforcement learning in simulation with domain randomization. We employ Proximal Policy Optimization (PPO) with the objective:

$$L^{CLIP}(\phi) = \mathbb{E}_t \left[ \min\left( r_t(\phi) \hat{A}_t, \text{clip}(r_t(\phi), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]$$

where $r_t(\phi) = \frac{\pi_\phi(a_t|s_t)}{\pi_{\phi_{old}}(a_t|s_t)}$ is the probability ratio and $\hat{A}_t$ is the advantage estimate. Domain randomization includes variations in object geometry, mass, friction coefficients, and visual appearance to facilitate sim-to-real transfer, following principles established by Wang et al. (2022) for robust keypoint representations.

### 2.4 Semantic-Motor Adapter Network

The core innovation lies in the Semantic-Motor Adapter (SMA), which bridges semantic understanding and motor execution. Given a subtask specification $(s_i, o_i)$ from the STP and current visual observation $I_t$, the adapter predicts primitive parameters:

$$\hat{\theta}_i = \mathcal{A}_\psi(e_s, e_o, f_v)$$

where $e_s = \text{Embed}(s_i)$ is the subtask embedding, $e_o = \text{Embed}(o_i)$ is the object embedding extracted from the foundation model's latent space, and $f_v = \text{CNN}(I_t)$ is a visual feature vector from a lightweight convolutional encoder.

The adapter architecture employs a transformer-based design:

$$h_0 = [e_s; e_o; f_v] + \text{PE}$$
$$h_l = \text{TransformerBlock}(h_{l-1}), \quad l = 1, \ldots, L$$
$$\hat{\theta}_i = \text{MLP}(h_L)$$

where PE denotes positional encoding, and L=4 transformer blocks are used. The adapter contains approximately 12M parameters—significantly smaller than the frozen foundation model—enabling efficient training and real-time inference.

### 2.5 Automatic Curriculum Generation

To maximize zero-shot generalization, we employ automatic curriculum generation during adapter training. We construct a task grammar $\mathcal{G}$ that procedurally generates diverse training scenarios:

$$\mathcal{T}_{train} = \{(\tau_j, I_j^{init}, \theta_j^*)\}_{j=1}^{N}$$

where $\tau_j$ is a generated instruction, $I_j^{init}$ is the initial scene configuration, and $\theta_j^*$ are ground-truth parameters obtained from privileged simulation information.

The curriculum progression follows a competence-based scheme:

$$\text{Difficulty}(t) = \min\left(1, \frac{\bar{R}(t)}{\bar{R}_{target}}\right) \cdot D_{max}$$

where $\bar{R}(t)$ is the rolling average success rate and $D_{max}$ represents maximum task complexity (number of objects, instruction length, required primitives).

The adapter is trained using a composite loss:

$$\mathcal{L} = \lambda_1 \mathcal{L}_{param} + \lambda_2 \mathcal{L}_{success} + \lambda_3 \mathcal{L}_{contrastive}$$

where:
- $\mathcal{L}_{param} = \|\hat{\theta} - \theta^*\|_2^2$ is the parameter regression loss
- $\mathcal{L}_{success}$ is a binary cross-entropy loss for task completion prediction
- $\mathcal{L}_{contrastive}$ encourages similar semantic inputs to produce similar parameter outputs

### 2.6 Experimental Design

#### Simulation Environment
We utilize Isaac Gym for physics simulation with photorealistic rendering via NVIDIA Omniverse. The environment includes 100+ household objects with varied geometries and physical properties.

#### Evaluation Benchmark
We construct the **Household Activity Benchmark (HAB-50)**, comprising 50 activities across five categories:
- **Kitchen tasks** (15): cooking, pouring, stirring, cutting preparation
- **Cleaning tasks** (10): wiping, sweeping, organizing
- **Organization tasks** (10): sorting, shelving, drawer management  
- **Object manipulation** (10): tool use, assembly
- **Multi-step activities** (5): meal preparation, table setting

Each activity has 10 scene variations, totaling 500 evaluation scenarios.

#### Baselines
1. **End-to-End VLA**: Vision-language-action model trained directly on demonstrations
2. **RT-1-X**: Robotic transformer foundation model
3. **SayCan**: Language model with affordance functions
4. **Code-as-Policies**: LLM-generated code for robot control

#### Evaluation Metrics
- **Task Success Rate (TSR)**: Percentage of successfully completed tasks
- **Primitive Accuracy (PA)**: Correct primitive selection rate
- **Parameter Error (PE)**: Mean squared error of predicted parameters
- **Generalization Gap (GG)**: Performance difference between seen and unseen tasks
- **Execution Time (ET)**: Average time to complete tasks

#### Real-World Validation
We deploy on a Franka Emika Panda robot with wrist-mounted RGB-D camera. We evaluate on 20 representative tasks from HAB-50, with 5 trials per task under varying lighting and object positions.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Performance**: We anticipate achieving a 3x improvement in novel task success rates compared to end-to-end policies (targeting 75% TSR on unseen tasks versus ~25% for baselines). The modular primitive approach should yield >90% primitive selection accuracy.

2. **Sample Efficiency**: The curriculum-based adapter training is expected to require 10x fewer demonstrations than end-to-end approaches, addressing the data efficiency challenge highlighted in the literature.

3. **Generalization Analysis**: We expect to demonstrate that compositional primitive structures enable systematic generalization to instruction combinations never seen during training, validating the hypothesis that hierarchical decomposition mitigates the exponential data requirements identified in recent theoretical analyses.

4. **Sim-to-Real Transfer**: Real-world experiments should achieve >60% of simulation performance without additional fine-tuning, validating the robustness of our domain randomization and adapter design.

### Scientific Impact

This research contributes to the fundamental understanding of how to effectively leverage foundation models for embodied AI. By demonstrating that semantic understanding can be efficiently translated into motor execution through learned adapters, we provide a principled approach to the integration challenge that has limited previous attempts. The automatic curriculum generation methodology offers insights into training strategies for compositional generalization.

### Practical Impact

The ASP framework has direct applications in:
- **Home assistance robots** for elderly care and accessibility
- **Warehouse automation** requiring flexible manipulation
- **Healthcare settings** for assistive tasks
- **Disaster response** scenarios requiring adaptive manipulation

By reducing the data and engineering requirements for deploying robots in new environments, this work lowers barriers to practical robot deployment in unstructured settings.

### Open-Source Contributions

We will release: (1) the HAB-50 benchmark with evaluation protocols, (2) pre-trained primitive policies and adapter weights, (3) the curriculum generation framework, and (4) integration code for common robot platforms.

This research represents a significant step toward robots with human-level adaptability, bridging the gap between the remarkable capabilities of modern foundation models and the physical requirements of real-world manipulation tasks.