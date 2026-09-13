# Adaptive Memory Consolidation for Long-Horizon LLM Agents via Hierarchical Episodic Compression

## 1. Introduction

### Background

Large Language Models (LLMs) have demonstrated remarkable capabilities in reasoning, planning, and natural language understanding, making them ideal candidates for autonomous agent systems. However, deploying LLM agents in real-world scenarios requiring extended operation reveals a fundamental limitation: the inability to efficiently manage experiences over long horizons. Current LLM agents face a critical bottleneck when operating beyond their fixed context windows, typically ranging from 4K to 128K tokens. While recent advances have extended these limits, the quadratic computational complexity of attention mechanisms makes processing extremely long contexts prohibitively expensive.

Existing approaches to memory management in LLM agents fall into two problematic extremes. Some systems attempt to retain all historical interactions within the context window, leading to rapid saturation and computational inefficiency. Others employ naive summarization techniques that compress experiences into short descriptions, resulting in significant information loss and inability to retrieve specific details when needed. Neither approach mirrors how biological systems—particularly human cognition—handle long-term memory formation and retrieval.

Human memory systems exhibit sophisticated hierarchical organization, with experiences initially encoded as episodic memories (specific events with temporal and contextual details) that undergo selective consolidation into semantic memories (generalized knowledge). This process is neither uniformly compressive nor completely retentive; instead, it operates through importance-weighted selection, where emotionally salient, frequently accessed, or task-relevant experiences receive preferential retention. Recent neuroscience research has revealed that memory retrieval itself triggers reconsolidation processes, allowing memories to be updated with new information and merged with related experiences.

Recent work has begun exploring biologically-inspired memory architectures for LLMs. TiMem (arXiv:2601.02845) introduced temporal-hierarchical memory consolidation using a Memory Tree structure, while CogMem (arXiv:2512.14118) proposed a layered architecture with Long-Term Memory and Focus of Attention mechanisms. However, these approaches lack dynamic importance-based selection mechanisms and do not fully leverage reconsolidation processes for continual learning.

### Research Objectives

This research proposes to develop an **Adaptive Memory Consolidation (AMC)** system that enables LLM agents to operate effectively over extended time horizons through three primary innovations:

1. **Design a hierarchical episodic storage architecture** that organizes agent experiences into multi-granular temporal episodes (sub-task, task, and session levels) with explicit structural relationships.

2. **Implement a selective compression mechanism** that dynamically evaluates memory importance based on task relevance, reward signals (emotional salience), and retrieval frequency, applying differential compression strategies accordingly.

3. **Develop a dynamic retrieval and reconsolidation system** that updates memory representations upon access and merges similar experiences into generalized schematic knowledge.

### Significance

This research addresses fundamental challenges in deploying LLM agents for real-world applications requiring continuous operation, such as personal assistants, customer service agents, educational tutors, and robotic systems. The proposed AMC system promises several transformative impacts:

- **Extended Operational Capability**: Enabling agents to operate continuously across days, weeks, or months without degradation in performance or catastrophic forgetting.

- **Improved Sample Efficiency**: By consolidating similar experiences into generalized patterns, agents can learn from fewer interactions and transfer knowledge across related tasks.

- **Computational Efficiency**: Reducing memory overhead by 50% or more while maintaining task performance allows deployment on resource-constrained devices and reduces operational costs.

- **Continual Learning**: The reconsolidation mechanism provides a natural framework for continual learning without requiring explicit task boundaries or rehearsal buffers.

Beyond practical applications, this research contributes theoretical insights into the functional role of hierarchical memory organization and selective consolidation, potentially informing both AI and cognitive science research.

## 2. Methodology

### 2.1 Overall Architecture

The Adaptive Memory Consolidation system consists of four primary components: (1) Experience Encoding, (2) Hierarchical Episodic Storage, (3) Selective Compression Engine, and (4) Dynamic Retrieval and Reconsolidation Module. Figure 1 conceptually illustrates the architecture.

**Experience Encoding**: Each agent interaction step $t$ generates an experience tuple $e_t = (s_t, a_t, o_t, r_t, c_t)$ where $s_t$ represents the state observation, $a_t$ the action taken, $o_t$ the outcome, $r_t$ the reward signal, and $c_t$ the linguistic context (conversation history, task description). The LLM agent processes this tuple to generate an embedding $\mathbf{h}_t \in \mathbb{R}^d$ using the model's final layer representations.

### 2.2 Hierarchical Episodic Storage

The storage architecture organizes experiences into a three-level hierarchy inspired by temporal abstraction in human episodic memory:

**Level 1 - Sub-task Episodes ($E^{sub}$)**: Short sequences of temporally contiguous experiences sharing a common immediate goal. A sub-task episode $E^{sub}_i = \{e_{t_i}, e_{t_i+1}, ..., e_{t_j}\}$ is formed when a boundary condition is detected, such as goal achievement, context shift, or a maximum length threshold $L_{sub}$ (default: 20 steps).

**Level 2 - Task Episodes ($E^{task}$)**: Collections of sub-task episodes contributing to a higher-level objective. Task episodes are formed through hierarchical clustering of sub-task episodes based on semantic similarity and temporal proximity.

**Level 3 - Session Episodes ($E^{session}$)**: Extended interaction periods spanning multiple tasks, bounded by natural breakpoints (explicit session termination, extended inactivity exceeding threshold $\tau_{session}$).

Each episode at any level is represented by:
- **Core Representation**: $\mathbf{m}_E = f_{compress}(\{e_t\}_{t \in E})$, an embedding vector
- **Metadata**: Temporal bounds $(t_{start}, t_{end})$, hierarchical links (parent/child episodes), access count $n_{access}$, creation timestamp
- **Importance Score**: $I_E \in [0, 1]$ (detailed below)
- **Compression Level**: $\lambda_E \in \{0, 1, 2, 3\}$ indicating detail retention (0=full, 3=maximum compression)

The compression function $f_{compress}$ uses a lightweight encoder-decoder Transformer:

$$\mathbf{m}_E = \text{Encoder}\left(\frac{1}{|E|}\sum_{t \in E} \mathbf{h}_t, \mathbf{v}_{meta}\right)$$

where $\mathbf{v}_{meta}$ encodes episode metadata (duration, reward statistics, hierarchical level).

### 2.3 Selective Compression Mechanism

The importance scoring function evaluates three dimensions:

**1. Task Relevance ($R_{task}$)**: Semantic similarity between the episode and current task context:
$$R_{task}(E, c_{current}) = \text{cosine}(\mathbf{m}_E, \text{Encode}(c_{current}))$$

**2. Emotional Salience ($S_{emotion}$)**: Based on reward signals, modeling the role of emotional significance in human memory consolidation:
$$S_{emotion}(E) = \sigma\left(\alpha \cdot \max_{t \in E} |r_t| + \beta \cdot \sum_{t \in E} r_t\right)$$
where $\sigma$ is the sigmoid function, and $\alpha, \beta$ are learnable parameters balancing peak and cumulative rewards.

**3. Retrieval Frequency ($F_{retrieval}$)**: Normalized access count with temporal decay:
$$F_{retrieval}(E, t_{current}) = \frac{n_{access}}{1 + \gamma \cdot (t_{current} - t_{last\_access})}$$

The composite importance score combines these dimensions:
$$I_E = w_1 R_{task} + w_2 S_{emotion} + w_3 F_{retrieval}$$

where weights $\{w_1, w_2, w_3\}$ are learned through meta-learning on a validation set of long-horizon tasks.

**Compression Policy**: Episodes are assigned compression levels based on importance thresholds:
$$\lambda_E = \begin{cases}
0 & \text{if } I_E > \theta_3 \\
1 & \text{if } \theta_2 < I_E \leq \theta_3 \\
2 & \text{if } \theta_1 < I_E \leq \theta_2 \\
3 & \text{if } I_E \leq \theta_1
\end{cases}$$

Compression is implemented through progressive abstraction:
- **Level 0**: Full episode details retained (individual experience embeddings)
- **Level 1**: Aggregate episode embedding + key moments (high-reward or high-uncertainty steps)
- **Level 2**: Episode embedding + schematic summary (generated by LLM)
- **Level 3**: Merged into generalized knowledge patterns (see Reconsolidation)

### 2.4 Dynamic Retrieval and Reconsolidation

**Retrieval**: Given a query context $c_q$ at time $t$, the retrieval system:

1. Computes query embedding: $\mathbf{q} = \text{Encode}(c_q)$
2. Retrieves top-$k$ episodes across all levels using hybrid scoring:
$$\text{score}(E, \mathbf{q}) = \phi \cdot \text{cosine}(\mathbf{m}_E, \mathbf{q}) + (1-\phi) \cdot I_E \cdot \exp(-\delta \cdot (t - t_{end}^E))$$
where $\phi$ balances relevance and importance, and $\delta$ controls temporal decay.

3. Decompresses selected episodes to appropriate detail level for context injection

**Reconsolidation**: Upon retrieval, episodes undergo two update processes:

*Update 1 - Contextualized Refinement*:
$$\mathbf{m}_E^{new} = (1-\eta)\mathbf{m}_E + \eta \cdot \text{Encoder}(\mathbf{m}_E, \mathbf{q})$$
where $\eta$ is a learning rate controlling update magnitude.

*Update 2 - Cross-Episode Consolidation*:
When episodes $E_i$ and $E_j$ are co-retrieved frequently and exhibit high similarity ($\text{cosine}(\mathbf{m}_{E_i}, \mathbf{m}_{E_j}) > \theta_{merge}$), they are merged into a generalized schema $S_{ij}$:

$$\mathbf{m}_{S_{ij}} = \frac{n_{access}^{E_i} \mathbf{m}_{E_i} + n_{access}^{E_j} \mathbf{m}_{E_j}}{n_{access}^{E_i} + n_{access}^{E_j}}$$

The schema inherits merged metadata and receives compression level 3, while original episodes may be downgraded or archived.

### 2.5 Integration with LLM Agent

The AMC system integrates with base LLM agents through:

**Context Assembly**: At each decision step, assemble context:
$$c_{input} = [c_{task}, c_{recent}, c_{retrieved}]$$
where $c_{task}$ is task description, $c_{recent}$ contains last $N$ experiences (short-term memory), and $c_{retrieved}$ contains decompressed relevant episodes from AMC.

**Memory Formation**: After each action, form experience tuple and update hierarchical storage asynchronously to avoid blocking agent execution.

**Periodic Consolidation**: Run compression and reconsolidation processes during idle periods or at fixed intervals (e.g., end of task/session).

### 2.6 Data Collection and Experimental Design

**Datasets**:
1. **LongHorizon Benchmark Suite**: Synthetic multi-step navigation, planning, and problem-solving tasks requiring memory of 100-1000+ steps
2. **ALFRED (Action Learning From Realistic Environments and Directives)**: Household robot tasks requiring long-horizon instruction following
3. **WebShop**: E-commerce task requiring navigation and information integration across multiple web pages
4. **Personalized Assistant Dialogues**: Multi-session conversational datasets (persona-based, e.g., MSC - Multi-Session Chat)

**Baseline Comparisons**:
- **Full Context**: Retain all history within extended context windows (up to limit)
- **Sliding Window**: Keep only recent $N$ experiences
- **Uniform Summarization**: Periodic summarization of all history
- **TiMem**: Temporal-hierarchical memory tree (arXiv:2601.02845)
- **CogMem**: Layered memory with LTM and Focus mechanisms (arXiv:2512.14118)
- **Retrieval-Augmented**: Standard dense retrieval without consolidation

**Implementation Details**:
- Base LLM: LLaMA-2-7B or GPT-3.5-turbo for fair comparison
- Episode encoder: 6-layer Transformer with 512 hidden dimensions
- Training: Meta-learning on validation tasks to optimize importance weights and compression thresholds
- Hardware: 4x NVIDIA A100 GPUs for parallel training

**Evaluation Metrics**:

1. **Task Performance**:
   - Success Rate (SR): Percentage of successfully completed tasks
   - Path Efficiency: Steps taken / optimal steps
   - Final Reward: Cumulative reward achieved

2. **Memory Efficiency**:
   - Memory Overhead: Average tokens consumed by memory context
   - Compression Ratio: Original data size / stored size
   - Retrieval Latency: Time to retrieve and decompress memories

3. **Knowledge Retention**:
   - Recall@k: Ability to recall specific past experiences when queried
   - Transfer Performance: Success on novel tasks related to past experiences
   - Forgetting Rate: Performance degradation on previously learned tasks over time

4. **Long-Horizon Capability**:
   - Maximum Operational Horizon: Longest task sequence without performance degradation
   - Cross-Session Consistency: Maintaining persona/preferences across sessions

**Ablation Studies**:
- Impact of each importance dimension (task relevance, emotional salience, retrieval frequency)
- Effect of hierarchical levels (flat vs. 2-level vs. 3-level)
- Reconsolidation mechanisms (with/without contextual refinement and schema merging)
- Compression strategies (different threshold configurations)

**Statistical Analysis**: All experiments will be run with 5 random seeds, reporting mean ± standard deviation. Statistical significance will be assessed using paired t-tests with Bonferroni correction for multiple comparisons.

## 3. Expected Outcomes & Impact

### Expected Outcomes

Based on preliminary theoretical analysis and related work, we anticipate the following concrete outcomes:

**1. Memory Efficiency Improvements**:
- **50-70% reduction in memory overhead** compared to full context retention, while maintaining within 5% of full-context task performance on benchmarks
- **3-5x longer operational horizons** before memory saturation compared to sliding window approaches
- **Sub-100ms retrieval latency** for typical queries, enabling real-time agent operation

**2. Task Performance Enhancement**:
- **10-15% improvement in success rate** on long-horizon tasks (>500 steps) compared to baseline memory systems
- **20-30% better performance** on multi-session personalization tasks compared to non-consolidating systems
- **Improved sample efficiency**: 30% fewer training experiences needed to reach target performance through knowledge generalization

**3. Knowledge Organization**:
- Emergence of **hierarchical schema structures** representing generalized procedural knowledge
- **Automatic discovery of task decompositions** through episode clustering
- **Stable long-term knowledge retention** with <5% forgetting rate over extended operation

**4. System Capabilities**:
- Functional prototype system compatible with popular LLM agent frameworks (LangChain, AutoGPT)
- Open-source release of AMC module, benchmark tasks, and evaluation scripts
- Comprehensive ablation analysis revealing contribution of each component

### Scientific Impact

This research advances the theoretical understanding of memory systems in AI agents:

**Cognitive Modeling**: The AMC system provides a computational model of human-like memory consolidation, offering testable predictions about the functional role of hierarchical organization and selective retention. This may inform cognitive science research on memory mechanisms.

**Continual Learning Theory**: The reconsolidation mechanism offers a novel approach to continual learning that avoids catastrophic forgetting without requiring explicit task boundaries, expanding the theoretical toolkit for lifelong learning systems.

**Neurosymbolic Integration**: By combining neural representations (embeddings) with symbolic structures (hierarchical episodes, schemas), AMC demonstrates effective neurosymbolic architecture for knowledge organization.

### Practical Impact

The proposed system addresses critical bottlenecks in deploying LLM agents for real-world applications:

**Personal AI Assistants**: Enabling assistants that remember user preferences, past interactions, and long-term goals across weeks or months of interaction, while respecting computational and privacy constraints through selective retention.

**Embodied AI and Robotics**: Allowing robots to learn from extended operational experience, consolidating procedural knowledge while retaining specific episodic memories of important events (errors, novel situations).

**Educational Technology**: Supporting intelligent tutoring systems that track student progress across multiple sessions, identifying patterns in learning difficulties and adapting instruction accordingly.

**Enterprise Applications**: Customer service agents that maintain coherent long-term customer relationships, remembering past issues and preferences without storing all interaction details.

**Healthcare**: Clinical decision support systems that consolidate patient history while highlighting critical events, balancing comprehensive longitudinal views with focused attention on relevant details.

### Broader Implications

Beyond immediate applications, this research contributes to the broader trajectory of AI development:

**Resource Efficiency**: Reducing memory overhead directly translates to lower computational costs and energy consumption, supporting environmentally sustainable AI deployment.

**Accessibility**: More efficient memory systems enable deployment on edge devices and resource-constrained environments, democratizing access to sophisticated AI agents.

**Safety and Interpretability**: Hierarchical episodic organization provides natural explanations for agent behavior ("I did X because of past experience Y"), enhancing transparency and trustworthiness.

**Privacy Preservation**: Selective compression with configurable retention policies enables principled approaches to data minimization and "right to be forgotten" compliance.

### Limitations and Future Work

While promising, this research has limitations that suggest future directions:

**Scalability to Multimodal Experiences**: The current design focuses on linguistic representations; extending to visual, auditory, and sensorimotor experiences requires additional research on cross-modal consolidation.

**Social and Collaborative Memory**: Human memory is socially constructed; future work should explore how agent memories can be shared, merged, and collectively maintained in multi-agent systems.

**Meta-Learning for Importance Functions**: While this proposal includes learning importance weights, more sophisticated meta-learning approaches could enable agents to automatically discover domain-specific consolidation strategies.

**Theoretical Guarantees**: Developing formal bounds on forgetting rates and performance degradation as functions of compression parameters would strengthen theoretical foundations.

In conclusion, the Adaptive Memory Consolidation system represents a significant step toward LLM agents capable of human-like extended operation, learning from experience while managing computational constraints through biologically-inspired selective retention and hierarchical organization. The comprehensive experimental validation and open-source release will enable both immediate practical applications and continued research advancement in the nascent field of LLM agents.