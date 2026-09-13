# Research Proposal: Emergent Compositional Grounding through Multi-Agent Negotiation Games

## 1. Title

**Compositional Language Grounding via Strategic Multi-Agent Negotiation: A Game-Theoretic Framework for Enhanced LLM Reasoning and Semantic Robustness**

## 2. Introduction

### 2.1 Background

Large Language Models (LLMs) have demonstrated remarkable capabilities in natural language understanding and generation. However, they exhibit persistent limitations in compositional reasoning, grounding abstract concepts to concrete scenarios, and maintaining semantic consistency across varying contexts. These deficiencies stem primarily from their training paradigm, which relies heavily on supervised learning from static text corpora and human preference data through imitation-based approaches.

Wittgenstein's concept of "language games" provides a compelling theoretical foundation for addressing these limitations. His philosophy posits that meaning emerges not from fixed definitions but through dynamic use within social contexts. This perspective aligns with findings in cognitive science demonstrating that human language acquisition thrives on interactive, context-driven exchanges rather than passive observation. Recent work in language emergence simulations and multi-agent learning further reinforces that language transmission within populations of interacting agents plays a crucial role in shaping robust linguistic capabilities.

Current approaches to LLM training, while effective for many tasks, lack the interactive pressure that characterizes natural language development. Supervised fine-tuning and reinforcement learning from human feedback (RLHF) represent unidirectional learning paradigms where models passively absorb patterns from data. This absence of genuine interaction may explain persistent issues with compositional generalization, ambiguity resolution, and collaborative planning—skills that humans develop through strategic communication requiring negotiation, clarification, and mutual understanding.

### 2.2 Research Objectives

This research proposes a novel framework called **Strategic Negotiation for Compositional Grounding (SNCG)**, which addresses the following specific objectives:

1. **Design and implement a multi-agent negotiation environment** where LLM agents with asymmetric information must collaboratively solve compositional reasoning tasks through strategic dialogue.

2. **Develop a population-based training methodology** using multi-agent reinforcement learning with language as the action space, incorporating mechanisms to prevent semantic drift while promoting compositional consistency.

3. **Establish quantitative evaluation metrics** for measuring improvements in compositional generalization, ambiguity handling, and collaborative reasoning capabilities.

4. **Demonstrate that interactive strategic pressure** yields superior compositional understanding compared to traditional supervised learning approaches.

### 2.3 Significance

This research addresses fundamental gaps at the intersection of multi-agent learning, language emergence, and modern NLP. The significance of this work includes:

- **Theoretical Contribution**: Bridging game theory, cognitive science perspectives on language acquisition, and practical LLM training methodologies, providing empirical validation of Wittgensteinian language game concepts in modern AI systems.

- **Methodological Innovation**: Introducing the semantic drift penalty and asymmetric information negotiation framework as novel mechanisms for grounding compositional semantics through interaction.

- **Practical Impact**: Enhancing LLM capabilities in critical areas including collaborative planning, handling ambiguous instructions, and maintaining semantic consistency—capabilities essential for real-world deployment in multi-agent systems, embodied AI, and human-AI collaboration scenarios.

- **Broader Applications**: Providing a scalable framework applicable to various domains including resource allocation, strategic planning, collaborative problem-solving, and situated language understanding in embodied agents.

## 3. Methodology

### 3.1 Multi-Agent Negotiation Environment Design

#### 3.1.1 Task Framework

We design a suite of compositional reasoning tasks requiring negotiation for successful completion:

**Resource Allocation Domain**: Agents must distribute resources based on complex, compositionally-expressed constraints. For example: "Allocate supplies such that teams with both specialists and equipment receive priority, but no team gets more than twice the average allocation."

**Collaborative Planning Domain**: Agents possess partial information about a planning problem and must negotiate to construct valid plans. Each agent knows different preconditions, effects, or constraints.

**Semantic Disambiguation Domain**: Agents receive instructions containing deliberately ambiguous references requiring negotiation to establish shared interpretation.

Each task $\tau$ is formally defined as a tuple $\langle S, A_1, A_2, O_1, O_2, T, R \rangle$ where:
- $S$ is the state space representing task context
- $A_i$ is the action space (language utterances) for agent $i$
- $O_i$ is the observation function for agent $i$ (asymmetric information)
- $T: S \times A_1 \times A_2 \rightarrow S$ is the state transition function
- $R: S \times A_1 \times A_2 \rightarrow \mathbb{R}$ is the joint reward function

#### 3.1.2 Asymmetric Information Design

To necessitate negotiation, we implement information asymmetry through:

1. **Partial Observability**: Agent 1 observes $O_1(s) = \{s_{\text{shared}}, s_1\}$ while Agent 2 observes $O_2(s) = \{s_{\text{shared}}, s_2\}$, where $s_1 \cap s_2 = \emptyset$.

2. **Complementary Expertise**: Agents are initialized with different fine-tuning on domain knowledge, creating natural information gaps.

3. **Context Fragmentation**: Task-critical information is distributed such that success requires information integration through dialogue.

### 3.2 Population-Based Multi-Agent Training

#### 3.2.1 Agent Architecture

Each agent consists of:
- **Base LLM**: Pre-trained language model (e.g., LLaMA, GPT-style architecture)
- **Policy Head**: $\pi_\theta(a_t | h_t, o_t)$ mapping conversation history $h_t$ and observation $o_t$ to action distribution over language tokens
- **Value Network**: $V_\phi(h_t, o_t)$ estimating expected cumulative reward

#### 3.2.2 Training Algorithm

We employ a multi-agent proximal policy optimization (MAPPO) variant with the following key components:

**Turn-level Advantage Estimation**: Following MARS (Yuan et al., 2025), we compute advantages at each conversational turn rather than episode-level:

$$A_t^i = \sum_{k=0}^{T-t} (\gamma \lambda)^k \delta_{t+k}^i$$

where $\delta_t^i = r_t^i + \gamma V_\phi(h_{t+1}, o_{t+1}) - V_\phi(h_t, o_t)$ and $\gamma, \lambda$ are discount and GAE parameters.

**Agent-Specific Advantage Normalization**: To stabilize multi-agent training:

$$\hat{A}_t^i = \frac{A_t^i - \mu_i}{\sigma_i + \epsilon}$$

where $\mu_i, \sigma_i$ are mean and standard deviation computed over agent $i$'s experiences in the current batch.

**Policy Update**: 

$$\mathcal{L}_{\text{policy}}^i = \mathbb{E}_t \left[ \min\left( \frac{\pi_{\theta'}(a_t^i | h_t, o_t)}{\pi_\theta(a_t^i | h_t, o_t)} \hat{A}_t^i, \text{clip}\left(\frac{\pi_{\theta'}(a_t^i | h_t, o_t)}{\pi_\theta(a_t^i | h_t, o_t)}, 1-\epsilon, 1+\epsilon\right) \hat{A}_t^i \right) \right]$$

#### 3.2.3 Semantic Drift Penalty

The key innovation is a compositional consistency loss term. We define semantic drift penalty $\mathcal{L}_{\text{drift}}$ as:

$$\mathcal{L}_{\text{drift}} = \lambda_{\text{drift}} \cdot \mathbb{E}_{c,c'} \left[ D_{\text{KL}}\left( p_\theta(\text{meaning} | c) \| p_\theta(\text{meaning} | c') \right) \right]$$

where $c, c'$ are different contexts requiring the same compositional interpretation, and $p_\theta(\text{meaning} | c)$ represents the agent's interpretation distribution.

Operationally, we implement this through:

1. **Paraphrase Consistency**: Given semantically equivalent instructions $i_1, i_2$, penalize divergent actions: $D_{\text{KL}}(\pi_\theta(\cdot | i_1) \| \pi_\theta(\cdot | i_2))$

2. **Compositional Substitution**: For compositional expressions with substitutable components (e.g., "red triangle" vs "red square"), enforce that semantic differences align with compositional structure:

$$\mathcal{L}_{\text{comp}} = \| \text{emb}(a|b) - \text{emb}(a|b') - (\text{emb}(b) - \text{emb}(b')) \|^2$$

where $\text{emb}(a|b)$ represents the contextual embedding of concept $a$ in context $b$.

**Total Loss Function**:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{policy}} - \beta \mathcal{H}(\pi_\theta) + \alpha \mathcal{L}_{\text{value}} + \lambda_{\text{drift}} \mathcal{L}_{\text{drift}} + \lambda_{\text{comp}} \mathcal{L}_{\text{comp}}$$

where $\mathcal{H}(\pi_\theta)$ is entropy bonus for exploration.

#### 3.2.4 Population Diversity

To prevent convergence to homogeneous strategies, we maintain a population of $N=20$ agents with:

1. **Diverse Initialization**: Agents fine-tuned on different subsets of domain knowledge
2. **Opponent Sampling**: Each training episode samples opponent from population distribution $p(\text{opp})$ favoring diversity
3. **Archive Mechanism**: Maintain archive of historically successful strategies for periodic training

### 3.3 Data Collection

#### 3.3.1 Task Dataset Construction

We construct three primary datasets:

**CompositionalResourceAllocation (CRA)**: 10,000 procedurally generated resource allocation problems with compositionally-structured constraints varying in:
- Nesting depth (2-5 levels)
- Logical operators (AND, OR, NOT, IMPLIES)
- Numerical constraints (inequalities, ratios)

**CollaborativePlanning (CP)**: 5,000 planning problems adapted from PDDL benchmarks with information split between agents.

**AmbiguousInstructions (AI)**: 3,000 deliberately ambiguous task specifications requiring clarification dialogues for resolution.

#### 3.3.2 Evaluation Datasets

**Held-out Compositional Generalization**: Novel compositions not seen during training, testing systematic generalization.

**Cross-Domain Transfer**: Tasks from domains different from training to assess grounding robustness.

### 3.4 Experimental Design

#### 3.4.1 Training Protocol

1. **Phase 1 - Warm-up (Epochs 1-10)**: Train with standard supervised fine-tuning on human-annotated negotiation dialogues
2. **Phase 2 - Self-Play Initialization (Epochs 11-30)**: Begin MAPPO training without semantic drift penalty
3. **Phase 3 - Full Training (Epochs 31-100)**: Incorporate full loss including drift penalties

#### 3.4.2 Baseline Comparisons

We compare SNCG against:

1. **Supervised Fine-Tuning (SFT)**: Standard instruction tuning on task demonstrations
2. **Single-Agent RL**: Individual agents trained with task reward without multi-agent interaction
3. **RLHF**: Reinforcement learning from human feedback on task quality
4. **MARS Baseline**: State-of-art multi-agent RL without semantic drift penalty (Yuan et al., 2025)
5. **ReMA**: Meta-thinking framework without negotiation (Wan et al., 2025)

#### 3.4.3 Evaluation Metrics

**Primary Metrics**:

1. **Task Success Rate (TSR)**: Percentage of tasks successfully completed
2. **Compositional Generalization Score (CGS)**: Performance on novel compositional structures relative to training distribution:

$$\text{CGS} = \frac{\text{TSR}_{\text{novel}}}{\text{TSR}_{\text{train}}}$$

3. **Semantic Consistency Score (SCS)**: Agreement in agent interpretations across paraphrased contexts:

$$\text{SCS} = 1 - \mathbb{E}_{c,c'} \left[ \frac{1}{2} \| \pi_\theta(\cdot | c) - \pi_\theta(\cdot | c') \|_1 \right]$$

**Secondary Metrics**:

4. **Negotiation Efficiency**: Average dialogue turns required for task completion
5. **Ambiguity Resolution Accuracy**: Success rate in disambiguating ambiguous instructions
6. **Collaborative Planning Quality**: Optimality of jointly-constructed plans
7. **Communication Coherence**: Human evaluation of dialogue naturalness (1-5 scale)

#### 3.4.4 Ablation Studies

We conduct ablations to isolate contributions of:
- Semantic drift penalty ($\lambda_{\text{drift}} = 0$)
- Compositional consistency loss ($\lambda_{\text{comp}} = 0$)
- Population diversity (single opponent vs. population)
- Information asymmetry (symmetric vs. asymmetric information)
- Turn-level advantages (episode-level vs. turn-level)

#### 3.4.5 Analysis Experiments

**Emergent Communication Analysis**: Analyze whether agents develop compositional communication protocols by measuring:
- **Topographic Similarity** (Lazaridou et al., 2018): Correlation between semantic distance and message distance
- **Positional Disentanglement**: Whether message components consistently refer to specific semantic attributes

**Grounding Robustness**: Test trained agents on:
- Out-of-distribution linguistic variations
- Novel task contexts requiring transfer
- Multi-step compositional reasoning chains

**Semantic Drift Measurement**: Track interpretation divergence across training by periodically evaluating SCS on fixed test set.

### 3.5 Implementation Details

**Hardware**: 8×A100 GPUs for distributed training
**Base Models**: LLaMA-2-7B and LLaMA-2-13B
**Training Duration**: Approximately 100 epochs (~2 weeks on specified hardware)
**Hyperparameters**: 
- Learning rate: $3 \times 10^{-5}$ with cosine annealing
- Batch size: 256 episodes (128 per GPU with gradient accumulation)
- $\gamma = 0.99$, $\lambda = 0.95$, $\epsilon = 0.2$
- $\lambda_{\text{drift}} = 0.1$, $\lambda_{\text{comp}} = 0.05$, $\beta = 0.01$

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Improvements**: Based on preliminary experiments and related work, we anticipate:

1. **Compositional Generalization**: 25-40% improvement in CGS over supervised baselines, with trained agents achieving >0.85 CGS compared to ~0.60 for SFT models.

2. **Task Success Rate**: 15-30% absolute improvement over single-agent RL baselines on complex negotiation tasks, reaching 75-85% success rate.

3. **Semantic Consistency**: SCS >0.90 for SNCG agents compared to ~0.70 for baseline models, demonstrating reduced semantic drift.

4. **Ambiguity Resolution**: 40-50% improvement in successfully disambiguating ambiguous instructions through clarification dialogues.

5. **Negotiation Efficiency**: Trained agents converging to solutions in 30-40% fewer dialogue turns while maintaining or improving success rates.

**Qualitative Insights**: 

1. **Emergent Communication Protocols**: Agents developing compositional communication strategies where message components systematically refer to specific semantic elements.

2. **Strategic Clarification Behavior**: Agents learning to proactively ask targeted questions when faced with ambiguity rather than guessing.

3. **Collaborative Planning Capabilities**: Improved ability to construct joint plans through information sharing and constraint negotiation.

### 4.2 Scientific Impact

**Theoretical Contributions**:

1. **Validation of Language Game Theory**: Empirical demonstration that Wittgensteinian language games can be operationalized to improve modern AI systems, bridging philosophy of language with machine learning.

2. **Multi-Agent Learning Theory**: Extension of self-play methods to cooperative-competitive scenarios requiring communication, contributing to understanding of emergence in multi-agent systems.

3. **Compositional Learning Principles**: Establishing that interactive strategic pressure creates stronger compositional inductive biases than supervised learning, with implications for cognitive science models of human language acquisition.

**Methodological Contributions**:

1. **Semantic Drift Prevention**: The semantic drift penalty and compositional consistency loss provide reusable mechanisms for maintaining semantic robustness in interactive learning settings.

2. **Scalable Interactive Training**: Demonstrating that population-based multi-agent RL can scale to train production-grade LLMs, opening new directions for interactive training paradigms.

3. **Evaluation Framework**: Comprehensive metrics for assessing compositional grounding and semantic consistency applicable to broader language understanding research.

### 4.3 Practical Impact

**Immediate Applications**:

1. **Collaborative AI Systems**: Enhanced LLMs for multi-agent coordination in domains like project management, resource allocation, and distributed problem-solving.

2. **Embodied AI**: Improved language grounding for robots and virtual agents requiring situated understanding and collaborative planning.

3. **Human-AI Interaction**: More robust conversational agents capable of handling ambiguity through clarification and maintaining consistent interpretations.

4. **Educational Technology**: AI tutors with improved ability to negotiate understanding and adapt explanations based on student clarification questions.

**Long-term Impact**:

1. **Paradigm Shift in LLM Training**: Demonstrating viability of interactive training at scale may catalyze broader adoption of game-theoretic and multi-agent approaches in foundation model development.

2. **Personalization**: Framework extensible to personalized language games where agents adapt to individual user communication styles through repeated interaction.

3. **Safety and Alignment**: Interactive grounding through negotiation provides mechanisms for agents to clarify uncertain interpretations before acting, improving safety in high-stakes applications.

4. **Cognitive Science Insights**: Findings may inform understanding of human language acquisition, particularly regarding role of strategic interaction in developing compositional reasoning.

### 4.4 Limitations and Future Directions

**Acknowledged Limitations**:

1. **Computational Cost**: Population-based multi-agent training requires significant computational resources, potentially limiting accessibility.

2. **Evaluation Challenges**: Human evaluation of semantic understanding remains partially subjective; developing fully automated metrics for grounding quality is ongoing work.

3. **Domain Specificity**: Initial experiments focus on structured tasks; generalization to open-ended natural language domains requires further investigation.

**Future Research Directions**:

1. **Scaling to Larger Models**: Investigating whether benefits persist and potentially amplify with larger foundation models (70B+ parameters).

2. **Hybrid Approaches**: Combining interactive training with traditional supervised and preference-based methods for optimal performance.

3. **Lifelong Learning**: Extending framework to continual learning scenarios where agents accumulate knowledge through ongoing interactions.

4. **Theoretical Analysis**: Formal game-theoretic analysis of convergence properties and equilibria in semantic negotiation games.

5. **Real-world Deployment**: Field studies deploying trained agents in practical collaborative scenarios with human users.

### 4.5 Broader Implications

This research contributes to the broader vision of **Language Gamification** by:

1. Providing concrete methodology for implementing interactive LLM training at scale
2. Demonstrating measurable benefits of game-theoretic frameworks for language grounding
3. Establishing evaluation standards for assessing interactive language learning
4. Creating open-source tools and datasets to facilitate community research

By bridging cognitive science insights about natural language acquisition with modern deep learning and multi-agent systems, this work represents a step toward more human-like language understanding in AI systems—not through passive imitation, but through active negotiation of meaning in strategic contexts.