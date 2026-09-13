# Research Proposal: Dual-Process Vision-Language Agents for Sequential Decision Making

## 1. Title

**Dual-Process Vision-Language Agents: Separating Intuitive Proposals from Deliberative Reasoning for Improved Sequential Decision Making**

---

## 2. Introduction

### 2.1 Background

Foundation models pretrained on diverse vision and language datasets have achieved remarkable success across a wide spectrum of downstream tasks, from image captioning and visual question answering to complex dialogue generation. These models, including large language models (LLMs) and vision-language models (VLMs), encode vast amounts of world knowledge acquired through exposure to internet-scale data. However, as these models are increasingly deployed in real-world applications—autonomous driving, healthcare diagnostics, robotics, and interactive dialogue systems—they encounter fundamental challenges that extend beyond static perception and generation tasks.

Sequential decision making, encompassing reinforcement learning (RL), imitation learning, planning, and optimal control, has traditionally addressed challenges such as learning from environmental feedback, adapting to dynamic task modalities, and performing long-horizon reasoning. Research in these fields has achieved superhuman performance in domains like board games (AlphaGo, AlphaZero) and Atari video games, as well as enabling robots to complete complex navigation and manipulation tasks. However, these methods typically learn task-specific policies from scratch without leveraging the broad semantic knowledge embedded in foundation models, resulting in poor sample efficiency and limited generalization to novel scenarios.

The intersection of foundation models and sequential decision making represents a rapidly emerging research frontier. Recent advances include optimizing dialogue agents through reinforcement learning with human feedback (RLHF), deploying large pretrained VLMs as perception and reasoning components in embodied agents, and adapting foundation models to interact with external tools such as search engines, calculators, and simulators. Despite these promising developments, significant scientific challenges remain unresolved. Foundation models are trained on static datasets without action labels, creating a fundamental mismatch with the interactive nature of decision-making tasks. End-to-end fine-tuning of VLMs with RL often leads to training instability and catastrophic forgetting of pretrained knowledge. Conversely, using VLMs as frozen components fails to enable task-specific optimization and adaptation.

### 2.2 Research Motivation

Human cognition provides a compelling framework for addressing these challenges. Dual-process theory, extensively studied in cognitive psychology, posits that human reasoning operates through two distinct systems: System 1, which is fast, intuitive, and automatic, and System 2, which is slow, deliberate, and analytical. System 1 rapidly generates candidate responses based on pattern recognition and prior experience, while System 2 evaluates these candidates through explicit reasoning and selects the most appropriate action.

We hypothesize that this cognitive architecture can be translated into a computational framework for vision-language decision making. Specifically, we propose that a frozen VLM can serve as System 1, leveraging its pretrained knowledge to rapidly generate diverse action proposals without requiring action-specific training. A separate RL-trained deliberator module can serve as System 2, learning to reason over these proposals through chain-of-thought (CoT) processes and selecting optimal actions based on task-specific feedback. This architectural separation offers several potential advantages: (1) preserving the VLM's pretrained knowledge while enabling task-specific learning, (2) improving credit assignment by localizing learning to the deliberation module, (3) enhancing interpretability through explicit reasoning traces, and (4) improving sample efficiency by constraining the action space to semantically meaningful proposals.

### 2.3 Research Objectives

This research aims to:

1. **Design and implement** a dual-process vision-language agent (DP-VLA) architecture that separates intuitive proposal generation from deliberative reasoning.
2. **Validate** the hypothesis that this architectural separation improves task success rate, sample efficiency, and interpretability compared to monolithic end-to-end VLM-RL approaches.
3. **Investigate** the causal mechanisms underlying performance improvements through systematic ablation studies.
4. **Demonstrate** generalization across diverse vision-language decision-making domains including text-based games, open-world environments, and robotic manipulation.

### 2.4 Significance

This research addresses fundamental questions at the intersection of foundation models and sequential decision making. By providing a principled framework for combining pretrained knowledge with learned reasoning, this work has the potential to advance both theoretical understanding and practical deployment of foundation model agents. The explicit reasoning traces produced by the deliberation module enhance interpretability, a critical requirement for real-world deployment in safety-critical domains. Furthermore, the proposed architecture offers a modular design that can accommodate advances in both VLM capabilities and RL algorithms, providing a sustainable framework for future research.

---

## 3. Methodology

### 3.1 Architecture Design

The Dual-Process Vision-Language Agent (DP-VLA) consists of two primary components:

**System 1: VLM Proposer**

The proposer module utilizes a frozen vision-language model (LLaVA-7B) to generate diverse action proposals. Given an observation $o_t$ (comprising visual input $v_t$ and textual context $c_t$), the proposer generates $K$ candidate actions:

$$\{a_t^{(1)}, a_t^{(2)}, \ldots, a_t^{(K)}\} = \text{VLM}_{\text{proposer}}(o_t; \tau)$$

where $\tau$ is the sampling temperature controlling diversity. The VLM is prompted with task-specific instructions and few-shot examples to generate semantically meaningful action candidates. Importantly, the VLM parameters remain frozen throughout training, preserving pretrained knowledge.

**System 2: RL Deliberator**

The deliberator module is a trainable transformer-based network that receives the observation $o_t$ and the $K$ proposals, then generates chain-of-thought reasoning followed by action selection:

$$r_t, \hat{a}_t = \text{Deliberator}_\theta(o_t, \{a_t^{(1)}, \ldots, a_t^{(K)}\})$$

where $r_t$ represents the reasoning trace and $\hat{a}_t \in \{1, \ldots, K\}$ is the index of the selected proposal. The deliberator is trained via reinforcement learning to maximize task rewards.

### 3.2 Training Algorithm

**Objective Function**

The deliberator is trained to maximize expected cumulative reward:

$$J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_{t=0}^{T} \gamma^t R(s_t, a_t)\right]$$

where $\gamma$ is the discount factor and $R(s_t, a_t)$ is the task reward.

**Policy Gradient with Chain-of-Thought**

We employ Proximal Policy Optimization (PPO) with a modified objective that encourages coherent reasoning:

$$L^{\text{PPO}}(\theta) = \mathbb{E}_t\left[\min\left(\rho_t(\theta)\hat{A}_t, \text{clip}(\rho_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t\right)\right]$$

where $\rho_t(\theta) = \frac{\pi_\theta(a_t|o_t, \{a^{(k)}\})}{\pi_{\theta_{\text{old}}}(a_t|o_t, \{a^{(k)}\})}$ and $\hat{A}_t$ is the advantage estimate.

**Reasoning Quality Regularization**

To encourage interpretable reasoning, we add a regularization term based on reasoning coherence:

$$L^{\text{total}}(\theta) = L^{\text{PPO}}(\theta) - \lambda \cdot L^{\text{CoT}}(\theta)$$

where $L^{\text{CoT}}(\theta)$ penalizes reasoning traces that are inconsistent with the selected action, computed via a frozen LLM judge.

**Complete Training Algorithm**

```
Algorithm: DP-VLA Training
Input: Frozen VLM proposer, initial deliberator θ₀, environment E
Output: Trained deliberator θ*

1. Initialize replay buffer B
2. For episode e = 1 to N_episodes:
   a. Reset environment: o₀ = E.reset()
   b. For timestep t = 0 to T:
      i.   Generate K proposals: {a^(k)} = VLM(oₜ; τ)
      ii.  Generate reasoning and select action: rₜ, âₜ = Deliberator_θ(oₜ, {a^(k)})
      iii. Execute action: oₜ₊₁, Rₜ = E.step(a^(âₜ))
      iv.  Store transition: B ← B ∪ {(oₜ, {a^(k)}, rₜ, âₜ, Rₜ, oₜ₊₁)}
   c. Compute advantages Âₜ using GAE
   d. Update θ using PPO with L^total
3. Return θ*
```

### 3.3 Experimental Design

**Benchmark Environments**

We evaluate DP-VLA across three diverse domains:

1. **ALFWorld**: A text-based game environment requiring multi-step household task completion. Tasks include finding objects, cleaning, heating, and organizing items across multiple rooms.

2. **Minecraft**: An open-world environment requiring long-horizon planning, resource gathering, and crafting. We use the MineDojo benchmark with tasks of varying complexity.

3. **RoboCasa**: A robotic manipulation simulation environment with realistic kitchen scenarios requiring object manipulation, tool use, and multi-step task completion.

**Baseline Methods**

1. **End-to-End VLM-RL**: Direct PPO fine-tuning of the full VLM on task rewards.
2. **Frozen VLM + Learned Policy Head**: VLM as frozen encoder with trainable action head.
3. **ReAct-style Prompting**: Zero-shot prompting with reasoning-action interleaving.

**Experimental Conditions**

| Condition | System 1 | System 2 | Training |
|-----------|----------|----------|----------|
| DP-VLA (Full) | Frozen VLM | RL Deliberator + CoT | PPO |
| DP-VLA (No CoT) | Frozen VLM | RL Deliberator | PPO |
| DP-VLA (K=1) | Frozen VLM (single proposal) | RL Deliberator | PPO |
| End-to-End | Trainable VLM | Integrated | PPO |
| Frozen + Head | Frozen VLM | MLP Policy Head | PPO |

**Evaluation Metrics**

1. **Task Success Rate (Primary)**: Percentage of episodes achieving the goal state, measured over 100 held-out evaluation episodes per task.

2. **Sample Efficiency**: Number of environment interactions required to reach 70% success rate.

3. **Reasoning Interpretability**: Human evaluation of CoT reasoning quality on a 5-point Likert scale assessing relevance, coherence, and correctness. We recruit 3 expert annotators to evaluate 50 randomly sampled reasoning traces per condition.

4. **Inference Latency**: Wall-clock time per decision step to assess practical applicability.

**Statistical Analysis**

- **Sample Size**: $n \geq 100$ episodes per condition per environment
- **Primary Test**: Two-proportion z-test for success rate comparison
- **Secondary Tests**: Paired t-test for sample efficiency, Mann-Whitney U for interpretability scores
- **Significance Level**: $\alpha = 0.05$ (two-tailed)
- **Effect Size**: Cohen's d with 95% confidence intervals

**Ablation Studies**

To validate the causal mechanism, we conduct systematic ablations:

1. **Proposal Diversity (H-M1, H-M2)**: Vary $K \in \{1, 3, 5, 10\}$ to assess impact of proposal count on exploration and performance.

2. **CoT Reasoning (H-M3)**: Compare CoT-enabled deliberation versus direct action selection to isolate reasoning contribution.

3. **RL Training (H-M4)**: Compare RL-trained deliberator versus supervised learning from expert demonstrations.

4. **VLM Quality**: Evaluate with different VLM backbones (LLaVA-7B, LLaVA-13B) to assess sensitivity to proposer capability.

### 3.4 Implementation Details

**Model Specifications**
- VLM Proposer: LLaVA-7B (frozen)
- Deliberator: 125M parameter transformer decoder
- Proposal count: $K = 5$ (default)
- Sampling temperature: $\tau = 0.7$

**Training Hyperparameters**
- Learning rate: $3 \times 10^{-4}$ with cosine decay
- Batch size: 64 episodes
- PPO clip parameter: $\epsilon = 0.2$
- Discount factor: $\gamma = 0.99$
- GAE parameter: $\lambda = 0.95$
- CoT regularization weight: $\lambda = 0.1$

**Computational Resources**
- Hardware: 4-8 NVIDIA A100 GPUs
- Training time: 1-2 weeks per environment
- Total compute budget: ~2000 GPU-hours

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Prediction (P1 - Task Success Rate)**

We predict that DP-VLA will achieve task success rates exceeding 75% on ALFWorld, outperforming end-to-end VLM-RL baselines by at least 10 percentage points. This improvement is expected because the architectural separation enables stable training of the deliberation module while preserving the VLM's pretrained knowledge for proposal generation.

**Secondary Prediction (P2 - Sample Efficiency)**

We expect DP-VLA to require at most 50% of the environment interactions needed by end-to-end baselines to reach 70% success rate. The constrained action space (selecting among $K$ proposals rather than generating actions from scratch) should accelerate learning by focusing exploration on semantically meaningful actions.

**Secondary Prediction (P3 - Interpretability)**

Human evaluators are expected to rate DP-VLA's chain-of-thought reasoning at 4.0/5.0 or higher on relevance and coherence. The explicit reasoning traces provide transparency into the decision-making process, enabling users to understand and verify agent behavior.

### 4.2 Falsification Criteria

The hypothesis will be rejected if:
1. Task success rate ≤ 65% (primary failure)
2. No significant improvement in sample efficiency (mechanism failure)
3. DP-VLA performs equivalent to or worse than baselines on all metrics (comparative failure)
4. CoT reasoning rated ≤ 3.0/5.0 (interpretability failure)

### 4.3 Scientific Contributions

1. **Architectural Innovation**: A novel dual-process framework that provides a principled approach to combining foundation model capabilities with sequential decision-making requirements.

2. **Mechanistic Understanding**: Systematic ablation studies will elucidate the causal mechanisms underlying performance improvements, advancing theoretical understanding of how architectural choices affect learning dynamics.

3. **Evaluation Framework**: Comprehensive evaluation protocols spanning multiple domains and metrics, providing a template for future research in foundation model agents.

### 4.4 Broader Impact

**Practical Applications**

The DP-VLA architecture has immediate applications in:
- **Robotics**: Enabling robots to leverage pretrained knowledge for manipulation tasks while learning from environmental feedback
- **Autonomous Systems**: Providing interpretable decision-making for safety-critical applications
- **Interactive Assistants**: Enhancing dialogue agents with principled reasoning capabilities

**Research Directions**

This work opens several avenues for future research:
- Extending to continuous action spaces through proposal refinement
- Investigating multi-agent coordination with dual-process architectures
- Exploring hierarchical deliberation for very long-horizon tasks

**Societal Considerations**

The interpretability benefits of explicit reasoning traces address growing concerns about AI transparency and accountability. By making decision-making processes visible, DP-VLA supports human oversight and enables identification of potential failure modes before deployment.

### 4.5 Limitations and Future Work

We acknowledge several limitations:
1. The sequential System 1→2 architecture differs from parallel human cognition, representing an engineering simplification
2. Proposal quality is bounded by the VLM's pretrained knowledge distribution
3. Inference latency may be higher than monolithic approaches due to the two-stage process

Future work will address these limitations through parallel proposal-deliberation architectures, domain-adaptive proposal fine-tuning, and efficiency optimizations for real-time deployment.

---

**Conclusion**

This research proposal presents a principled approach to combining foundation model capabilities with sequential decision-making through a dual-process architecture inspired by human cognition. By separating intuitive proposal generation from deliberative reasoning, DP-VLA offers a promising framework for achieving improved task success, sample efficiency, and interpretability in vision-language decision-making tasks. The comprehensive experimental design, including systematic ablations and multi-domain evaluation, will provide robust evidence for or against the proposed hypothesis while advancing our understanding of how to effectively deploy foundation models in interactive settings.