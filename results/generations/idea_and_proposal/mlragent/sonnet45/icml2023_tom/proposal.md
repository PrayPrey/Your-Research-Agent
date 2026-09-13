# Hierarchical Theory of Mind Modeling for Multi-Party Dialogue Systems with Recursive Belief Tracking

## 1. Introduction

### Background

Theory of Mind (ToM)—the cognitive capacity to attribute mental states to oneself and others—is fundamental to human social interaction and communication. In computational systems, ToM enables agents to predict, explain, and influence the behavior of other agents by reasoning about their beliefs, desires, and intentions. While significant progress has been made in developing dialogue systems with basic ToM capabilities, current systems face substantial challenges in multi-party conversational contexts where understanding requires reasoning about nested beliefs across multiple agents.

Consider a workplace scenario where an AI assistant must navigate the following situation: "Alice thinks Bob doesn't know that Carol is upset about the project deadline." This requires third-order ToM reasoning: the system must track (1) Carol's emotional state, (2) Bob's (lack of) knowledge about Carol's state, and (3) Alice's belief about Bob's knowledge. Such hierarchical mental state reasoning is ubiquitous in human multi-party interactions but remains largely beyond the capabilities of existing dialogue systems.

Recent large language models (LLMs) have demonstrated promising but inconsistent ToM capabilities, primarily in simple two-party scenarios with first-order belief reasoning. However, they lack explicit architectural mechanisms for systematically tracking and updating hierarchical mental states as conversations unfold. This limitation becomes critical in applications requiring sophisticated social reasoning: collaborative AI systems, negotiation platforms, therapeutic chatbots, educational tutors, and social robots operating in group settings.

### Research Objectives

This research proposes to develop a novel **Hierarchical Theory of Mind Network (HToMNet)** that explicitly models and tracks nested mental states in multi-party dialogue systems through recursive belief tracking mechanisms. The specific objectives are:

1. **Architectural Innovation**: Design a hybrid neural-symbolic architecture that augments transformer-based language models with structured belief graph representations capable of maintaining hierarchical mental states up to n-th order ToM.

2. **Dynamic Belief Updating**: Develop graph neural network mechanisms for efficient propagation and updating of belief states as new information emerges in multi-party conversations.

3. **Training Framework**: Create a comprehensive training methodology combining synthetic data generation, semi-supervised learning from unannotated dialogues, and fine-tuning on human-annotated ToM reasoning tasks.

4. **Evaluation and Benchmarking**: Establish rigorous evaluation protocols and contribute new benchmark datasets specifically designed for assessing hierarchical ToM reasoning in multi-party dialogues.

### Significance

This research addresses critical gaps at the intersection of computational linguistics, cognitive science, and artificial intelligence. The expected contributions include:

- **Theoretical Advancement**: Providing computational insights into the mechanisms underlying hierarchical social cognition and how nested belief structures can be efficiently represented and manipulated.

- **Practical Impact**: Enabling more natural and effective human-AI collaboration in group settings, including virtual meetings, collaborative problem-solving, conflict mediation, and educational contexts.

- **Explainability**: Offering transparent belief state representations that make AI reasoning processes interpretable to human users, addressing critical concerns in trustworthy AI.

- **Interdisciplinary Bridge**: Connecting computational ToM research with psychological theories of metacognition and social reasoning, fostering productive dialogue between AI and cognitive science communities.

## 2. Methodology

### 2.1 Overall Architecture

The HToMNet architecture comprises three interconnected components:

**2.1.1 Base Dialogue Encoder**

We employ a pre-trained transformer model (e.g., RoBERTa or GPT-based architecture) as the foundation for encoding conversational context. Given a multi-party dialogue history $H = \{u_1, u_2, ..., u_t\}$ where $u_i = (s_i, a_i, c_i)$ represents utterance $i$ spoken by agent $a_i$ with content $c_i$ at turn $s_i$, the encoder produces contextualized representations:

$$\mathbf{h}_t = \text{Encoder}(u_1, u_2, ..., u_t)$$

**2.1.2 Hierarchical Belief Graph**

The core innovation lies in maintaining an explicit belief graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where:

- Nodes $\mathcal{V}$ represent belief states at different levels of nesting
- Edges $\mathcal{E}$ encode relationships between beliefs

For a dialogue with $N$ agents, we define belief states up to order $k$ as:

$$B^{(0)}_{a,p} = \text{belief of agent } a \text{ about proposition } p$$

$$B^{(1)}_{a,b,p} = \text{agent } a\text{'s belief about agent } b\text{'s belief about } p$$

$$B^{(n)}_{a,\{b_1,...,b_n\},p} = \text{agent } a\text{'s belief about } b_1\text{'s belief about ... } b_n\text{'s belief about } p$$

Each node in the graph is represented as a continuous vector $\mathbf{v}_i \in \mathbb{R}^d$ encoding the probability distribution over possible belief states.

**2.1.3 Graph Neural Network Belief Propagator**

We employ a specialized Graph Attention Network (GAT) architecture for belief propagation. At each dialogue turn $t$, belief states are updated through message passing:

$$\mathbf{m}_{i \rightarrow j}^{(l)} = \text{MLP}_m\left([\mathbf{v}_i^{(l)} \| \mathbf{v}_j^{(l)} \| \mathbf{e}_{ij} \| \mathbf{h}_t]\right)$$

$$\alpha_{ij} = \frac{\exp(\text{LeakyReLU}(\mathbf{w}^T \mathbf{m}_{i \rightarrow j}))}{\sum_{k \in \mathcal{N}(j)} \exp(\text{LeakyReLU}(\mathbf{w}^T \mathbf{m}_{i \rightarrow k}))}$$

$$\mathbf{v}_j^{(l+1)} = \sigma\left(\sum_{i \in \mathcal{N}(j)} \alpha_{ij} \mathbf{m}_{i \rightarrow j}^{(l)}\right)$$

where $\mathbf{e}_{ij}$ represents edge features encoding the relationship type, $\mathbf{h}_t$ provides conversational context, and $L$ layers of message passing are applied.

### 2.2 Recursive Belief Update Mechanism

The system employs a recursive algorithm for updating beliefs when new utterances are observed:

**Algorithm 1: Hierarchical Belief Update**

```
Input: Current belief graph G_t, new utterance u_{t+1}
Output: Updated belief graph G_{t+1}

1. Extract information content: I = ExtractInfo(u_{t+1})
2. Identify affected agents: A_affected = GetAffectedAgents(u_{t+1})
3. Initialize update queue: Q = [(a, 0) for a in A_affected]
4. While Q is not empty:
   a. (agent, level) = Q.dequeue()
   b. Update beliefs: UpdateBeliefNode(G, agent, level, I)
   c. If level < k_max:
      For each observer in Agents:
         Q.enqueue((observer, level+1))
5. Apply GNN propagation: G_{t+1} = GNN_Propagate(G_t)
6. Return G_{t+1}
```

The update function incorporates both direct observation and inference:

$$P(B^{(n)}_{new}) = \eta \cdot P(B^{(n)}_{obs} | u_{t+1}) + (1-\eta) \cdot P(B^{(n)}_{inferred} | \mathcal{G}_t)$$

where $\eta$ is a learned gating parameter determining the balance between observed evidence and inferred states.

### 2.3 Training Methodology

**2.3.1 Synthetic Data Generation**

We generate synthetic multi-party dialogues with ground-truth belief annotations using a two-stage process:

1. **Scenario Templating**: Define 50+ scenario templates involving 3-6 agents with clear belief dependencies (e.g., secret-sharing, collaborative planning, misinformation scenarios).

2. **Dialogue Simulation**: Use constrained LLM generation with explicit ToM state tracking to produce dialogues where belief states are known by construction.

Each synthetic example includes:
- Complete dialogue transcript
- Timestamped belief state annotations for all agents at all ToM levels
- Critical moments where belief updates occur

Target: Generate 100,000 synthetic dialogues across diverse scenarios.

**2.3.2 Semi-Supervised Learning on Real Dialogues**

For unannotated real multi-party conversations (sourced from Ubuntu IRC logs, AMI meeting corpus, and social media threads):

1. **Self-supervised pretraining**: Train the model to predict masked utterances conditioned on inferred belief states.

2. **Consistency regularization**: Enforce that belief states remain consistent with observable agent behaviors:

$$\mathcal{L}_{consist} = \sum_t \sum_a \text{KL}\left(P(\text{action}_a | B_a^t) \| P(\text{observed}_a^t)\right)$$

**2.3.3 Fine-tuning on Human-Annotated Data**

Collect human annotations for 5,000 challenging multi-party dialogue segments:

- Annotators mark belief states at critical junctures
- Multiple annotators per segment (Fleiss' kappa > 0.75)
- Annotations include uncertainty estimates

Fine-tune using multi-task objectives:

$$\mathcal{L}_{total} = \lambda_1 \mathcal{L}_{belief} + \lambda_2 \mathcal{L}_{response} + \lambda_3 \mathcal{L}_{consistency}$$

where:
- $\mathcal{L}_{belief}$: Cross-entropy loss for belief state prediction
- $\mathcal{L}_{response}$: Standard dialogue response generation loss
- $\mathcal{L}_{consistency}$: Regularization ensuring belief-action coherence

### 2.4 Experimental Design

**2.4.1 Benchmark Datasets**

Evaluate on multiple datasets with varying characteristics:

1. **MuMA-ToM** (existing): Multi-modal multi-agent ToM benchmark
2. **DialSim** (existing): Long-term multi-party dialogue understanding
3. **HiToM-Dialog** (new): Curated dataset specifically for hierarchical ToM evaluation with:
   - 2,000 multi-party dialogues (3-5 participants)
   - Explicit n-th order belief annotations (n = 1, 2, 3)
   - 10,000+ belief state queries

**2.4.2 Baseline Comparisons**

Compare HToMNet against:

1. **LLM Baselines**: GPT-4, Claude, Gemini (zero-shot and few-shot prompting)
2. **Structured Baselines**: 
   - Standard dialogue state tracking models adapted for multi-party settings
   - Neural-symbolic systems (Eva framework)
   - MetaMind multi-agent system
3. **Ablation Variants**:
   - HToMNet without hierarchical structure (flat belief representation)
   - HToMNet without GNN propagation
   - HToMNet with limited ToM depth (k=1, k=2)

**2.4.3 Evaluation Metrics**

**Belief State Accuracy**:
$$\text{BSA}_k = \frac{1}{|Q_k|} \sum_{q \in Q_k} \mathbb{1}[\arg\max(P(B_q)) = B_q^{true}]$$

where $Q_k$ is the set of queries requiring k-th order ToM.

**Hierarchical F1 Score**: Evaluate precision and recall at each ToM level separately.

**Dialogue Performance**:
- Response relevance (BLEU, ROUGE, BERTScore)
- Task success rate in collaborative scenarios
- Human evaluation of naturalness and appropriateness

**Computational Efficiency**:
- Inference time per belief update
- Memory scaling with number of agents and ToM depth

**Explainability Metrics**:
- Human interpretability of extracted belief graphs (user study)
- Consistency between stated reasoning and belief states

### 2.5 Implementation Details

- **Framework**: PyTorch with PyTorch Geometric for GNN components
- **Base Models**: RoBERTa-large for encoding, GPT-2 medium for generation
- **Hyperparameters**:
  - Belief vector dimension: $d = 256$
  - GNN layers: $L = 3$
  - Maximum ToM depth: $k_{max} = 3$
  - Learning rate: $2 \times 10^{-5}$ with warmup
  - Batch size: 16 dialogues
- **Training Infrastructure**: 4x A100 GPUs, estimated 200 GPU-hours for full training

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**3.1.1 Technical Achievements**

1. **Performance Gains**: We anticipate 15-25% improvement over LLM baselines on hierarchical ToM benchmarks, with particular strength in third-order belief reasoning where current models struggle most.

2. **Architectural Contribution**: The HToMNet architecture will provide a reusable framework for integrating structured belief representations with neural language models, applicable beyond dialogue to areas like narrative understanding and social reasoning.

3. **Benchmark Resources**: The HiToM-Dialog dataset will become a valuable community resource, enabling standardized evaluation of multi-party ToM capabilities.

4. **Scalability Analysis**: Empirical characterization of how belief tracking complexity scales with number of agents ($N$) and ToM depth ($k$), providing insights into computational limits of hierarchical social reasoning.

**3.1.2 Scientific Insights**

1. **Computational Mechanisms**: Understanding which graph structures and propagation algorithms most effectively capture hierarchical belief dynamics will inform cognitive models of human ToM.

2. **Depth-Performance Tradeoffs**: Quantifying the benefit of higher-order ToM reasoning for different dialogue tasks will reveal when sophisticated mental modeling is essential versus superfluous.

3. **Failure Mode Analysis**: Systematic characterization of where and why belief tracking fails (e.g., ambiguous pronouns, implicit cultural assumptions) will guide future research.

### 3.2 Broader Impact

**3.2.1 Applications**

1. **Collaborative AI Assistants**: Virtual assistants that can navigate complex group dynamics in workplace settings, managing information asymmetries and facilitating productive collaboration.

2. **Educational Technology**: Tutoring systems that track individual student knowledge states in classroom settings and adapt explanations based on what each student knows about others' understanding.

3. **Conflict Mediation**: Automated systems that identify belief misalignments causing interpersonal conflicts and suggest targeted interventions.

4. **Social Robotics**: Robots operating in homes or healthcare settings that navigate multi-person interactions with appropriate sensitivity to individual mental states.

**3.2.2 Societal Considerations**

This research requires careful attention to ethical implications:

- **Privacy**: Explicit belief tracking raises concerns about mental state inference without consent. We will develop privacy-preserving variants and establish ethical guidelines.

- **Manipulation Risks**: ToM capabilities could be misused for manipulation. We will investigate and document potential misuse vectors and develop mitigation strategies.

- **Bias and Fairness**: Belief attribution may encode cultural biases. We will evaluate performance across diverse populations and cultural contexts.

- **Transparency**: The explicit belief graph structure inherently provides interpretability advantages, supporting accountable AI development.

**3.2.3 Interdisciplinary Contributions**

This work bridges AI and cognitive science, offering:

- Computational models that can be tested against human behavioral data
- Predictions about cognitive mechanisms underlying human ToM that can inspire psychological experiments
- Platforms for investigating how language and ToM co-develop

### 3.3 Future Directions

Success in this project opens several promising research avenues:

1. **Multimodal ToM**: Extending belief tracking to incorporate visual, gestural, and prosodic cues in embodied multi-party interactions.

2. **Cultural Adaptation**: Developing mechanisms for belief tracking that adapt to cultural differences in communication norms and mental state attribution.

3. **Affective ToM**: Integrating emotional state modeling with cognitive belief tracking for more holistic social understanding.

4. **Interactive Learning**: Enabling systems to actively query humans to resolve belief uncertainties, creating collaborative ToM development.

5. **Longitudinal Belief Modeling**: Extending from single conversations to tracking evolving mental models across extended relationships.

This research represents a significant step toward AI systems capable of the sophisticated social reasoning that characterizes human communication, with implications spanning from theoretical understanding of cognition to practical applications in human-AI collaboration.