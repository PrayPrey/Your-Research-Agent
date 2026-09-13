# Hierarchical Grounding Framework: Bridging MFM High-Level Reasoning with Low-Level Embodied Control via Learned Action Primitives

## 1. Introduction

### Background

The recent emergence of Multi-modal Foundation Models (MFMs) such as GPT-4V, CLIP, and Gemini has revolutionized artificial intelligence by demonstrating unprecedented capabilities in understanding and reasoning about visual and linguistic information. These models have shown remarkable proficiency in high-level cognitive tasks including scene understanding, visual question answering, and task planning. However, despite their impressive reasoning capabilities, a critical challenge persists when attempting to deploy these models in embodied AI systems: the "reasoning-to-action gap."

Current MFM-powered embodied agents face a fundamental disconnect between abstract, high-level reasoning and the precise, continuous control actions required for physical interaction with the environment. When instructed to perform tasks such as "make coffee" or "organize the desk," MFMs can effectively decompose these into logical subgoals like "grasp the cup" or "place item on shelf." However, translating these symbolic descriptions into executable motor commands that account for object geometry, environmental dynamics, contact physics, and sensorimotor feedback remains a formidable challenge. This gap severely limits the practical deployment of otherwise sophisticated AI systems in real-world robotics applications.

Recent work has attempted to address this challenge through various approaches. Vision-Language-Action (VLA) models like Lumo-1 and VLAC have demonstrated promise by directly mapping perceptual inputs to action sequences, while systems like OK-Robot have shown that integrating MFMs with hand-crafted primitives can achieve reasonable performance in open-ended tasks. However, these approaches either require extensive end-to-end training data that is difficult to collect at scale, or rely on rigid, manually-designed primitives that lack adaptability to diverse environments and tasks.

### Research Objectives

This research proposes a novel Hierarchical Grounding Framework (HGF) that systematically bridges the reasoning-to-action gap through three primary objectives:

1. **Develop a scalable action primitive library**: Create a repertoire of reusable, parameterized motor skills learned through reinforcement learning that can be composed to execute complex tasks while maintaining adaptability to environmental variations.

2. **Design an intelligent grounding mechanism**: Construct a lightweight vision-language-action grounding module that translates abstract MFM outputs into concrete action primitive sequences with appropriate parameters, conditioned on real-time sensory feedback.

3. **Establish comprehensive evaluation protocols**: Develop rigorous benchmarks and metrics that assess not only task success rates but also execution efficiency, generalization capabilities, and failure recovery in both simulated and real-world environments.

### Significance

This research addresses several critical gaps in current embodied AI systems:

**Theoretical Contribution**: The hierarchical decomposition framework provides a principled approach to connecting symbolic reasoning with continuous control, offering insights into how abstract knowledge can be grounded in physical action.

**Practical Impact**: By enabling MFMs to control embodied agents effectively, this work opens pathways for deploying advanced AI systems in real-world applications including household robotics, warehouse automation, elderly care, and disaster response scenarios.

**Scalability and Generalization**: Unlike end-to-end approaches that require task-specific training, our primitive-based framework enables compositional generalization, where learned skills transfer across tasks and domains with minimal additional training.

**Data Efficiency**: The hierarchical structure reduces the amount of paired demonstration data needed, as primitive skills can be learned separately and combined in novel ways, addressing a key bottleneck in real-world robot learning.

## 2. Methodology

### 2.1 Overall Framework Architecture

The Hierarchical Grounding Framework consists of three interconnected components operating at different levels of abstraction:

**Level 1 - MFM Planner**: Processes natural language instructions and visual observations to generate high-level task plans represented as sequences of subgoals.

**Level 2 - Grounding Module**: Translates subgoals into parameterized action primitive sequences while incorporating real-time sensory feedback.

**Level 3 - Action Primitive Library**: Executes low-level motor control through learned, reusable skills.

### 2.2 MFM Planner Design

We leverage pre-trained vision-language models (specifically GPT-4V or equivalent open-source alternatives like LLaVA-v1.6) as the high-level planner. The planner receives:

- Natural language task instruction $\mathcal{I}$
- Visual observation $\mathcal{O}_t$ at time $t$
- Scene context information $\mathcal{C}$ (object detections, spatial relationships)

The planner outputs a structured plan $\mathcal{P} = \{g_1, g_2, ..., g_N\}$ where each subgoal $g_i$ is represented as a tuple:

$$g_i = (\text{action\_type}, \text{target\_object}, \text{spatial\_relation}, \text{constraints})$$

For example: `("grasp", "red_cup", "from_table", "upright_orientation")`

To generate structured outputs, we employ few-shot prompting with chain-of-thought reasoning, providing the model with exemplar task decompositions. The prompt template includes:

1. Scene description with detected objects and their properties
2. Task instruction and success criteria
3. Request for step-by-step plan with specific format
4. Constraint specification (safety, temporal ordering)

### 2.3 Action Primitive Library Construction

#### 2.3.1 Primitive Skill Design

We define a library $\mathcal{A} = \{a_1, a_2, ..., a_K\}$ of $K$ parameterized action primitives. Each primitive $a_k$ is characterized by:

- **Skill type**: Navigation, manipulation, or perception primitives
- **Parameter space**: $\Theta_k$ defining valid configurations
- **Preconditions**: Required environmental states
- **Postconditions**: Expected state changes upon completion

Core primitives include:

**Manipulation primitives**: 
- `reach(target_pose, trajectory_type)`: Move end-effector to target
- `grasp(object_id, grasp_type)`: Execute grasping motion
- `place(target_location, placement_orientation)`: Release object at location
- `push(object_id, direction, distance)`: Apply contact force

**Navigation primitives**:
- `navigate_to(waypoint, obstacle_avoidance)`: Move base to location
- `align_with(object_id, relative_pose)`: Position relative to object

**Perception primitives**:
- `observe(target_region, duration)`: Gather visual information
- `verify(condition, timeout)`: Check state satisfaction

#### 2.3.2 Primitive Learning via Reinforcement Learning

Each primitive is trained as a separate reinforcement learning agent with:

**State space**: $s_t \in \mathcal{S}$ includes:
- Robot proprioceptive state (joint positions, velocities)
- Visual observations (RGB-D images)
- Object poses and properties
- Task-specific parameters from $\Theta_k$

**Action space**: $u_t \in \mathcal{U}$ consists of continuous control commands (joint torques or velocities)

**Reward function**: Primitive-specific dense rewards combining:

$$r_t = w_1 r_t^{\text{progress}} + w_2 r_t^{\text{safety}} + w_3 r_t^{\text{efficiency}} + w_4 r_t^{\text{success}}$$

where:
- $r_t^{\text{progress}}$: Distance to goal reduction
- $r_t^{\text{safety}}$: Collision avoidance, force limits
- $r_t^{\text{efficiency}}$: Energy consumption, smoothness
- $r_t^{\text{success}}$: Binary terminal reward

We employ Soft Actor-Critic (SAC) as the learning algorithm due to its sample efficiency and stability:

$$J(\pi) = \mathbb{E}_{\tau \sim \pi}\left[\sum_{t=0}^{T} \gamma^t \left(r_t + \alpha \mathcal{H}(\pi(\cdot|s_t))\right)\right]$$

where $\mathcal{H}$ is the entropy term promoting exploration, and $\alpha$ is the temperature parameter.

Training occurs in a curriculum across multiple environments with domain randomization over:
- Object geometries and physical properties
- Lighting conditions and textures
- Robot dynamics and sensor noise
- Initial state distributions

### 2.4 Grounding Module Architecture

The grounding module serves as the critical bridge between symbolic plans and executable primitives. It is implemented as a transformer-based sequence model that learns the mapping:

$$f_{\text{ground}}: (g_i, \mathcal{O}_t, \mathcal{H}_t) \rightarrow (a_k, \theta_k)$$

where:
- $g_i$ is the current subgoal from the MFM planner
- $\mathcal{O}_t$ is the current visual observation
- $\mathcal{H}_t$ is the execution history
- $a_k$ is the selected primitive
- $\theta_k$ are the primitive parameters

#### 2.4.1 Model Architecture

The grounding module consists of:

**Multimodal Encoder**:
- Vision encoder: Pre-trained CLIP ViT for image features
- Language encoder: Pre-trained BERT for subgoal text
- Proprioception encoder: MLP for robot state

**Cross-Modal Fusion**: Multi-head attention mechanism:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Applied across vision, language, and proprioceptive modalities.

**Action Primitive Decoder**: 
- Primitive selector: Categorical distribution over $\mathcal{A}$
- Parameter regressor: Continuous outputs for $\theta_k$

$$p(a_k, \theta_k | g_i, \mathcal{O}_t) = p(a_k | h_{\text{fused}}) \cdot p(\theta_k | a_k, h_{\text{fused}})$$

where $h_{\text{fused}}$ is the fused multimodal representation.

#### 2.4.2 Training Strategy

The grounding module is trained via behavioral cloning on a dataset $\mathcal{D} = \{(g_i, \mathcal{O}_t, a_k^*, \theta_k^*)\}$ where:

- Subgoals $g_i$ are generated by the MFM planner on training scenarios
- Ground-truth primitive sequences $(a_k^*, \theta_k^*)$ are obtained through:
  1. Kinesthetic teaching demonstrations
  2. Teleoperation with automatic primitive segmentation
  3. Inverse planning from successful trajectories

The training objective combines:

$$\mathcal{L} = \mathcal{L}_{\text{cls}} + \lambda_{\text{param}} \mathcal{L}_{\text{param}} + \lambda_{\text{reg}} \mathcal{L}_{\text{reg}}$$

where:
- $\mathcal{L}_{\text{cls}} = -\log p(a_k^* | g_i, \mathcal{O}_t)$: Cross-entropy for primitive selection
- $\mathcal{L}_{\text{param}} = \|\theta_k - \theta_k^*\|_2^2$: MSE for parameter prediction
- $\mathcal{L}_{\text{reg}}$: Regularization preventing overfitting

**Online Refinement**: After initial training, we employ DAgger (Dataset Aggregation) to improve robustness:

1. Deploy policy to collect trajectories
2. Query expert (human or oracle planner) for corrections at failure points
3. Augment dataset with corrections
4. Retrain model iteratively

### 2.5 Closed-Loop Execution with Feedback

During deployment, the system operates in a hierarchical closed-loop manner:

**Outer Loop (MFM Planner)**:
- Frequency: 0.5-2 Hz
- Monitors subgoal completion via vision-based verification
- Replans if environment state diverges from expectations
- Incorporates user feedback and intervention

**Inner Loop (Grounding + Primitives)**:
- Frequency: 10-30 Hz
- Executes primitive with real-time parameter adaptation
- Monitors execution success criteria
- Triggers recovery behaviors on primitive failure

The system maintains a probabilistic belief state $b_t$ over world state, updated via Bayesian filtering:

$$b_t(s) \propto p(\mathcal{O}_t | s) \int p(s | s_{t-1}, u_{t-1}) b_{t-1}(s_{t-1}) ds_{t-1}$$

### 2.6 Data Collection

#### 2.6.1 Simulation Environment

We utilize PyBullet and Isaac Sim as primary simulation platforms, implementing:

- **Task suites**: 50 manipulation tasks, 30 mobile manipulation tasks
- **Object datasets**: YCB objects, Google Scanned Objects, procedurally generated items
- **Scene diversity**: Kitchen, office, warehouse, outdoor environments
- **Robot platforms**: Franka Panda arm, UR5e, Fetch mobile manipulator

#### 2.6.2 Real-World Data Collection

Real-world validation uses:

- 2 Franka Panda robots in laboratory settings
- 15 hours of kinesthetic demonstrations across 20 tasks
- 200 hours of autonomous practice with human supervision
- Multi-camera setup (RGB-D, wrist-mounted, third-person)

### 2.7 Experimental Design

#### 2.7.1 Evaluation Tasks

**Manipulation Tasks**:
- Pick-and-place with clutter (varying object numbers: 5, 10, 20)
- Multi-step assembly (IKEA furniture benchmark)
- Deformable object manipulation (cloth folding, rope arrangement)

**Mobile Manipulation**:
- Fetch-and-deliver across rooms
- Rearrangement planning with obstacle navigation
- Human-robot handover scenarios

**Long-Horizon Tasks**:
- "Prepare breakfast" (10-15 subgoals)
- "Clean workspace" (open-ended, variable completion)
- "Organize bookshelf" (spatial reasoning emphasis)

#### 2.7.2 Baseline Comparisons

- **End-to-end VLA**: Direct vision-language-action models (RT-2 style)
- **MFM + Hand-crafted primitives**: OK-Robot approach
- **Hierarchical RL**: Options framework without MFM
- **Pure MFM**: GPT-4V with code generation for control

#### 2.7.3 Evaluation Metrics

**Success Metrics**:
- Task completion rate (TCR): Percentage of successful task executions
- Subgoal success rate (SSR): Percentage of individual subgoals achieved
- Partial credit score: Weighted sum of completed subgoals

**Efficiency Metrics**:
- Execution time compared to expert demonstrations
- Number of primitive calls vs. optimal plan
- Energy consumption and smoothness (jerk metric)

**Generalization Metrics**:
- Zero-shot transfer to novel objects (same category, different geometry)
- Cross-domain transfer (simulation to real-world)
- Compositional generalization (new task compositions from known primitives)

**Robustness Metrics**:
- Recovery rate from primitive failures
- Performance degradation under noise (vision, dynamics)
- Adaptation speed to environment perturbations

#### 2.7.4 Ablation Studies

- Impact of primitive library size (K = 5, 10, 20, 50)
- Grounding module architecture variations (LSTM vs. Transformer)
- Effect of online refinement (DAgger iterations)
- Contribution of multimodal inputs (vision, language, proprioception)

## 3. Expected Outcomes & Impact

### 3.1 Expected Technical Outcomes

**Quantitative Performance Targets**:

Based on preliminary experiments and literature benchmarks, we anticipate:

- **Task completion rate**: 75-85% on manipulation tasks (vs. 45-60% for end-to-end baselines, 58.5% for OK-Robot)
- **Generalization to novel objects**: 60-70% success rate without retraining (vs. <30% for end-to-end methods)
- **Execution efficiency**: 1.2-1.5× expert demonstration time (vs. 2-3× for MFM with code generation)
- **Data efficiency**: Achieving comparable performance with 10× less paired demonstration data compared to end-to-end VLA models

**Qualitative Capabilities**:

- Robust recovery from transient failures through primitive re-execution
- Interpretable execution allowing human intervention at subgoal boundaries
- Compositional generalization enabling zero-shot performance on novel task combinations
- Smooth integration of user corrections during execution

### 3.2 Scientific Contributions

**Theoretical Insights**:

1. **Hierarchical grounding principles**: Establishing design principles for connecting symbolic reasoning with continuous control through learned abstractions
2. **Compositionality in embodied AI**: Demonstrating how learned primitives enable systematic compositional generalization
3. **Multimodal integration**: Advancing understanding of effective fusion strategies for vision, language, and action

**Methodological Advances**:

1. **Scalable primitive learning framework**: Reproducible approach for building reusable skill libraries through curriculum RL
2. **Grounding module architecture**: Novel transformer-based design for translating symbolic plans to parameterized actions
3. **Evaluation protocols**: Comprehensive benchmarks for assessing MFM-powered embodied agents

### 3.3 Practical Impact

**Robotics Applications**:

- **Household assistance**: Enabling general-purpose home robots that understand natural instructions and adapt to varied home environments
- **Industrial automation**: Flexible manufacturing systems that reconfigure through language commands rather than reprogramming
- **Healthcare**: Assistive robots for elderly care and rehabilitation following natural language guidance

**Broader AI Systems**:

- **Virtual agents**: Transfer of learned primitives to simulated characters in games and virtual environments
- **Drone navigation**: Adaptation of framework to aerial manipulation and inspection tasks
- **Autonomous vehicles**: Application to complex driving scenarios requiring high-level planning and low-level control

### 3.4 Open-Source Contributions

To maximize impact and reproducibility, we commit to releasing:

1. **Complete codebase**: Training scripts, model architectures, and evaluation harness
2. **Primitive library**: Pre-trained primitive policies for common manipulation and navigation skills
3. **Datasets**: Paired demonstrations of MFM plans and primitive sequences
4. **Simulation environments**: Configured task suites with domain randomization
5. **Pre-trained grounding models**: Checkpoints for multiple robot platforms

### 3.5 Addressing Key Research Questions

This work directly addresses critical questions posed by the MFM-EAI workshop:

**Training and evaluation in open-ended environments**: Our hierarchical framework enables systematic evaluation through compositional task generation, while primitive-based execution naturally handles open-ended scenarios through skill composition.

**Effective system architecture**: The three-level hierarchy (MFM planner, grounding module, primitive library) provides a principled architecture balancing reasoning capabilities with execution precision.

**Balancing high-level and low-level control**: The grounding module explicitly bridges this gap, maintaining the generality of MFM reasoning while ensuring precise, adaptive low-level execution.

### 3.6 Limitations and Future Directions

**Acknowledged Limitations**:

- Primitive library requires initial investment in RL training across diverse environments
- Grounding module may struggle with highly novel primitives outside training distribution
- Current design focuses on discrete subgoal transitions, potentially missing continuous task variations

**Future Research Directions**:

1. **Lifelong learning**: Extending the framework to continuously acquire new primitives from experience
2. **Multi-agent coordination**: Generalizing to scenarios requiring multiple robots collaborating through shared primitives
3. **Safety verification**: Incorporating formal methods to verify safety properties of primitive compositions
4. **Foundation primitive models**: Developing universal primitive policies through massive-scale pre-training, analogous to MFMs

### 3.7 Timeline and Milestones

**Months 1-6**: Primitive library development and RL training in simulation  
**Months 7-12**: Grounding module implementation, demonstration collection, and initial training  
**Months 13-18**: Real-world deployment, baseline comparisons, and comprehensive evaluation  
**Months 19-24**: Ablation studies, refinement, and preparation of open-source release

This research promises to advance the frontier of MFM-powered embodied AI by providing a principled, scalable solution to the reasoning-to-action gap, with both immediate practical applications and long-term scientific impact.