# Research Proposal: Curriculum Self-Play via LLM-Generated Environment Perturbations for Open-Ended Skill Acquisition

## 1. Introduction

### Background

The pursuit of artificial general intelligence has increasingly focused on open-ended learning (OEL) systems—learning frameworks that generate an endless stream of progressively challenging problems to continually expand agent capabilities. Unlike traditional reinforcement learning paradigms where training concludes once a specific task is mastered, OEL systems mirror the evolutionary dynamics that shaped human intelligence through continuous environmental challenges and adaptive responses.

Recent advances in deep reinforcement learning and large language models (LLMs) have produced agents capable of remarkable performance on complex tasks. However, a fundamental limitation persists: these systems typically optimize for fixed objectives within static environments, lacking the open-ended adaptability observed in biological intelligence. The challenge lies not merely in solving difficult problems, but in automatically generating meaningful problems that reside within what Vygotsky termed the "zone of proximal development"—challenges that are neither trivially easy nor impossibly hard, but precisely calibrated to promote learning.

Current approaches to curriculum learning face significant limitations. Random environment generation produces highly variable task difficulties, often yielding trivial or impossible scenarios that waste computational resources. Hand-designed curricula, while more controlled, lack the open-endedness necessary for emergent general capabilities. Quality-diversity algorithms and unsupervised environment design methods have shown promise but often generate semantically arbitrary variations that may not correspond to meaningful skill acquisition.

Large language models represent a transformative resource for addressing these limitations. Trained on vast corpora of human knowledge, LLMs possess rich semantic understanding of physical environments, task structures, and progressive skill development. This knowledge could be leveraged to generate environment perturbations that are not only computationally tractable but also semantically meaningful—variations that human designers might construct but at scales impossible through manual design.

### Research Objectives

This research proposes a novel framework—**Curriculum Self-Play via LLM-Generated Environment Perturbations (CSP-LEP)**—that positions an LLM as an intelligent environment designer operating in a closed loop with a learning agent. The primary objectives are:

1. To develop a systematic methodology for translating agent capability profiles into natural language representations that LLMs can process effectively.

2. To design prompting strategies that elicit targeted, achievable environment perturbations from LLMs based on identified capability gaps.

3. To establish regret-based filtering mechanisms that ensure generated perturbations maintain productive difficulty levels.

4. To create feedback loops enabling iterative refinement of LLM proposals based on observed learning outcomes.

5. To empirically validate that this approach produces agents with superior generalization, particularly for sim2real transfer and out-of-distribution scenarios.

### Significance

This research addresses fundamental questions at the intersection of open-ended learning and foundation models. By leveraging LLM world knowledge for curriculum design, we bridge the gap between semantic meaningfulness and algorithmic scalability in environment generation. Success in this endeavor would provide a principled framework for producing agents with broader, more robust capabilities while reducing the extensive human effort currently required for curriculum engineering. Furthermore, understanding how to effectively couple LLM reasoning with embodied agent learning represents a crucial step toward more general AI systems.

## 2. Methodology

### 2.1 System Architecture Overview

The CSP-LEP framework consists of four interconnected modules: (1) Capability Profiling, (2) LLM-Driven Perturbation Generation, (3) Regret-Based Filtering, and (4) Iterative Refinement. These modules operate in a continuous cycle, as illustrated in Figure 1 (conceptual).

### 2.2 Capability Profiling Module

The capability profiling module periodically evaluates the agent across a diverse evaluation suite and translates performance metrics into structured natural language summaries.

**Evaluation Protocol**: Let $\mathcal{E} = \{e_1, e_2, ..., e_K\}$ denote a diverse set of evaluation scenarios spanning different skill dimensions (e.g., navigation, manipulation, planning). For each scenario $e_k$, we collect trajectory data $\tau_k = (s_0, a_0, r_0, s_1, ..., s_T)$ from the current policy $\pi_\theta$.

**Performance Metrics**: For each evaluation scenario, we compute:
- Success rate: $\text{SR}_k = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{goal reached in episode } i]$
- Average return: $\bar{R}_k = \frac{1}{N}\sum_{i=1}^{N} \sum_{t=0}^{T} \gamma^t r_t^{(i)}$
- Behavioral entropy: $H_k = -\sum_a \pi_\theta(a|s) \log \pi_\theta(a|s)$ averaged over visited states

**Capability Profile Generation**: We construct a structured capability profile $\mathcal{C}$ as:

$$\mathcal{C} = \{(d_j, \text{score}_j, \text{description}_j)\}_{j=1}^{M}$$

where $d_j$ represents skill dimension $j$, $\text{score}_j \in [0, 1]$ is the normalized competency score, and $\text{description}_j$ is a templated natural language description. For example: "Navigation in cluttered environments: 0.73 - Agent successfully navigates around static obstacles but struggles with narrow passages and dynamic obstacles."

### 2.3 LLM-Driven Perturbation Generation

The perturbation generation module prompts an LLM to propose environment modifications targeting identified capability gaps.

**Prompt Structure**: We design a structured prompt $P$ consisting of:

```
[System Context]: You are an expert curriculum designer for embodied AI agents. 
Your task is to propose environment modifications that challenge the agent's 
weaknesses while remaining achievable given current capabilities.

[Environment Description]: {base_environment_specification}

[Agent Capability Profile]: {capability_profile_C}

[Perturbation History]: {previous_perturbations_and_outcomes}

[Instructions]: Propose 5 environment modifications that:
1. Target the agent's lowest-scoring capabilities
2. Maintain physical plausibility
3. Are achievable given demonstrated strengths
4. Introduce novel challenges not seen in training

For each modification, provide:
- Natural language description
- Specific parameter changes (JSON format)
- Expected skill requirements
- Estimated difficulty relative to current capabilities
```

**Perturbation Parameterization**: Environment modifications are represented as structured perturbations $p = (\text{type}, \text{params}, \text{magnitude})$ where:
- $\text{type} \in \{\text{obstacle}, \text{physics}, \text{goal}, \text{agent}, \text{terrain}\}$
- $\text{params}$ specifies modification details (e.g., obstacle positions, friction coefficients)
- $\text{magnitude} \in [0, 1]$ indicates deviation from base environment

The LLM outputs are parsed into executable environment configurations through a structured JSON interface compatible with the simulation platform.

### 2.4 Regret-Based Filtering

Not all LLM-generated perturbations will provide productive learning signals. We employ a regret-based filtering mechanism to select perturbations with high learning potential.

**Regret Estimation**: For a perturbation $p$ generating environment $\mathcal{M}_p$, we estimate the learning potential using the regret metric:

$$\text{Regret}(p) = V^*(s_0; \mathcal{M}_p) - V^{\pi_\theta}(s_0; \mathcal{M}_p)$$

where $V^*$ is the optimal value function and $V^{\pi_\theta}$ is the current policy's value function. Since $V^*$ is unknown, we approximate it using:

$$\hat{V}^*(s_0; \mathcal{M}_p) \approx \max\left(V^{\pi_\theta}(s_0; \mathcal{M}_p), \hat{V}_{\text{upper}}(s_0; \mathcal{M}_p)\right)$$

where $\hat{V}_{\text{upper}}$ is estimated via optimistic rollouts or learned upper-bound models.

**Filtering Criterion**: We select perturbations satisfying:

$$\alpha \cdot R_{\max} \leq \text{Regret}(p) \leq \beta \cdot R_{\max}$$

where $\alpha, \beta \in (0, 1)$ with $\alpha < \beta$ define the productive difficulty range, and $R_{\max}$ is the maximum achievable return. Empirically, we set $\alpha = 0.2$ and $\beta = 0.7$ based on curriculum learning literature.

**Diversity Maintenance**: To ensure diverse skill coverage, we additionally filter using a quality-diversity criterion:

$$\text{Select } p^* = \arg\max_{p \in \mathcal{P}_{\text{valid}}} \text{Regret}(p) + \lambda \cdot d(p, \mathcal{P}_{\text{selected}})$$

where $d(\cdot, \cdot)$ measures behavioral diversity from previously selected perturbations.

### 2.5 Iterative Refinement via Feedback

The LLM's perturbation generation improves over time through structured feedback on proposal outcomes.

**Outcome Tracking**: For each deployed perturbation $p$, we record:
- Initial agent performance: $\text{perf}_0(p)$
- Final agent performance after training: $\text{perf}_T(p)$
- Learning progress: $\Delta(p) = \text{perf}_T(p) - \text{perf}_0(p)$
- Training efficiency: $\eta(p) = \Delta(p) / \text{training\_steps}$

**Feedback Construction**: Outcomes are summarized as:

$$\text{Feedback}(p) = (\text{description}(p), \Delta(p), \eta(p), \text{qualitative\_assessment})$$

where qualitative assessment categorizes the perturbation as {highly productive, moderately productive, unproductive, impossible}.

**Prompt Refinement**: Feedback is incorporated into subsequent prompts, enabling in-context learning for improved proposals.

### 2.6 Experimental Design

**Environments**: We validate CSP-LEP across three domains:
1. **MuJoCo Locomotion**: Continuous control tasks with physics perturbations
2. **MiniGrid Navigation**: Discrete navigation with procedural obstacles
3. **Isaac Gym Manipulation**: Robot manipulation with object and goal variations

**Baselines**:
- Domain Randomization (DR): Uniform random perturbations
- Prioritized Level Replay (PLR): Regret-based curriculum without LLM
- POET: Co-evolutionary environment generation
- CurricuLLM: LLM-based curriculum without regret filtering

**Evaluation Metrics**:
1. **Zero-shot generalization**: Performance on held-out test environments
2. **Sim2Real transfer gap**: Performance degradation when deployed on physical robots
3. **Sample efficiency**: Training steps to reach performance thresholds
4. **Capability breadth**: Number of distinct skills mastered (measured via behavioral clustering)
5. **Open-endedness metrics**: Novel complexity emergence measured via AURORA-style metrics

**Ablation Studies**:
- LLM perturbation vs. random perturbation
- With vs. without regret filtering
- With vs. without iterative refinement
- Different LLM backbones (GPT-4, Claude, Llama)

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following empirical findings:

1. **Superior Generalization**: Agents trained with CSP-LEP will demonstrate 20-40% improved zero-shot performance on held-out test environments compared to domain randomization and PLR baselines, as LLM-generated perturbations target semantically meaningful skill gaps rather than arbitrary variations.

2. **Enhanced Sim2Real Transfer**: The semantic coherence of LLM-proposed perturbations will produce more realistic environment variations, reducing the sim2real gap by an estimated 15-30% compared to purely algorithmic approaches.

3. **Improved Sample Efficiency**: Regret-based filtering will eliminate unproductive training scenarios, achieving 2-4x faster capability acquisition compared to unfiltered LLM proposals or random curricula.

4. **Emergent Capability Breadth**: The combination of LLM creativity and regret-based selection will produce agents mastering a broader range of skills, measured through increased behavioral diversity metrics.

5. **Iterative Refinement Benefits**: LLM proposal quality will improve over training, with later-stage perturbations showing higher learning efficiency than initial proposals.

### Broader Impact

**Scientific Contributions**: This research advances understanding of how large language models can serve as components in open-ended learning systems, bridging symbolic world knowledge with embodied skill acquisition. The framework provides a template for human-AI collaborative curriculum design at scale.

**Practical Applications**: CSP-LEP has immediate applications in robotics, where sim2real transfer remains a critical bottleneck. By generating more realistic and diverse training scenarios, the framework could accelerate deployment of capable robots in unstructured real-world environments.

**Open-Ended Learning Theory**: This work contributes to theoretical understanding of what makes curricula effective for open-ended skill acquisition, potentially informing both artificial and biological learning research.

**Limitations and Risks**: The framework depends on LLM capabilities and may inherit biases present in language model training. Additionally, computational costs of LLM inference and environment simulation must be carefully managed for practical deployment.

### Conclusion

The proposed CSP-LEP framework represents a principled approach to leveraging large language models for open-ended curriculum generation in embodied agents. By combining LLM world knowledge with regret-based filtering and iterative refinement, we aim to produce agents with broader, more robust capabilities that transfer effectively to real-world deployment scenarios. This research directly addresses core challenges in open-ended learning while demonstrating practical applications of foundation models beyond traditional language tasks.