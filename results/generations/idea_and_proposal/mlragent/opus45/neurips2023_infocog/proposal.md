# Research Proposal: Cognitive-Constrained Information Bottleneck for Emergent Communication in Human-AI Cooperative Tasks

## 1. Introduction

### Background

Effective human-AI cooperation represents one of the most pressing challenges in contemporary artificial intelligence research. As AI systems become increasingly integrated into collaborative workflows—from autonomous vehicles communicating with human drivers to AI assistants coordinating with human teams—the quality of communication between humans and machines becomes paramount. However, a fundamental tension exists: communication protocols that emerge through multi-agent reinforcement learning often optimize for agent-agent efficiency while remaining opaque to human collaborators.

The Information Bottleneck (IB) principle, introduced by Tishby et al. (2000), provides an elegant information-theoretic framework for learning representations that compress input information while preserving task-relevant features. Formally, the IB objective minimizes $I(X; Z) - \beta I(Z; Y)$, where $X$ is the input, $Z$ is the compressed representation, $Y$ is the task-relevant variable, and $\beta$ controls the trade-off between compression and relevance. Recent work has successfully applied IB principles to emergent communication (Karten et al., 2023) and collaborative perception (Wei et al., 2025), demonstrating significant improvements in communication efficiency.

However, existing approaches treat all communicating agents as having equivalent channel capacities and processing constraints. This assumption fundamentally fails when one communicating partner is human. Cognitive science research has established well-documented limitations on human information processing: Miller's "magical number seven" for working memory chunks, attention bandwidth constraints, and categorical perception boundaries. These asymmetric capacity constraints between human and artificial communicators are systematically ignored in current emergent communication frameworks.

Furthermore, research on emergent communication has revealed that neural agents tend toward entropy minimization (Kharitonov et al., 2019), producing languages that are often maximally compressed but lack the compositional structure and semantic alignment characteristic of human language. Galke et al. (2022) explicitly identified the absence of cognitive constraints as a key factor preventing emergent communication from producing human-like language properties.

### Research Objectives

This proposal introduces the **Cognitive-Constrained Information Bottleneck (CCIB)** framework, which addresses these limitations through three primary objectives:

1. **Develop a formal extension of the Information Bottleneck objective** that incorporates empirically-grounded human cognitive constraints as capacity penalties, creating principled pressure toward human-interpretable communication.

2. **Design and implement training algorithms** that optimize this cognitive-constrained objective using variational bounds, enabling scalable training of AI agents for human-AI cooperation.

3. **Validate the framework through rigorous human-subject experiments** comparing CCIB-trained agents against standard emergent communication baselines, measuring both task performance and human interpretability.

### Significance

This research bridges information theory, cognitive science, and AI alignment in a novel and principled manner. By grounding the compression term of the IB objective in measured human cognitive capacities, we create AI agents that spontaneously develop communication protocols matching human processing capabilities. This approach offers theoretical advances in understanding the role of cognitive constraints in communication emergence, practical benefits for human-AI teaming applications, and methodological contributions for incorporating human factors into information-theoretic machine learning frameworks.

## 2. Methodology

### 2.1 Theoretical Framework: Cognitive-Constrained Information Bottleneck

We extend the standard Information Bottleneck formulation to incorporate asymmetric cognitive constraints. Let $X$ denote the AI agent's observation of the environment, $M$ the message transmitted to the human collaborator, and $Y$ the task-relevant outcome. The standard IB objective is:

$$\mathcal{L}_{\text{IB}} = I(X; M) - \beta I(M; Y)$$

We propose the Cognitive-Constrained Information Bottleneck objective:

$$\mathcal{L}_{\text{CCIB}} = I(X; M) + \lambda \cdot \Psi_H(M) - \beta I(M; Y)$$

where $\Psi_H(M)$ is a **human cognitive cost functional** that penalizes message characteristics misaligned with human processing capabilities. We decompose this functional into three empirically-grounded components:

**Working Memory Constraint:** Based on Cowan's (2001) refined estimate of 4±1 chunks, we penalize messages requiring excessive chunking:

$$\Psi_{\text{WM}}(M) = \max(0, N_{\text{chunks}}(M) - 4) \cdot \alpha_{\text{WM}}$$

where $N_{\text{chunks}}(M)$ estimates the number of cognitive chunks required to process message $M$, implemented through a learned chunking model calibrated on human memory span experiments.

**Attention Bandwidth Constraint:** Drawing from capacity theories of attention (Kahneman, 1973), we penalize high-entropy message distributions that demand sustained attention:

$$\Psi_{\text{ATT}}(M) = \alpha_{\text{ATT}} \cdot H(M | C)$$

where $H(M | C)$ is the conditional entropy of messages given task context $C$, and $\alpha_{\text{ATT}}$ is calibrated from human attention studies.

**Categorical Alignment Penalty:** Humans perceive and communicate using categorical representations. We encourage alignment with human semantic categories:

$$\Psi_{\text{CAT}}(M) = -\alpha_{\text{CAT}} \cdot \sum_i \sum_{c \in \mathcal{C}} p(m_i = c) \log p(m_i = c)$$

This term rewards messages that concentrate probability mass on discrete categorical boundaries rather than continuous distributions.

The complete cognitive cost functional is:

$$\Psi_H(M) = \Psi_{\text{WM}}(M) + \Psi_{\text{ATT}}(M) + \Psi_{\text{CAT}}(M)$$

### 2.2 Variational Training Algorithm

Direct optimization of the CCIB objective is intractable due to mutual information terms. We derive variational bounds following the approach of Alemi et al. (2017), with cognitive-specific modifications.

**Variational Upper Bound on Compression:** We bound $I(X; M)$ using a variational approximation $r(M)$:

$$I(X; M) \leq \mathbb{E}_{p(X)} \left[ D_{\text{KL}}(p(M|X) \| r(M)) \right]$$

**Variational Lower Bound on Relevance:** We bound $I(M; Y)$ using a variational decoder $q(Y|M)$:

$$I(M; Y) \geq \mathbb{E}_{p(M,Y)} \left[ \log q(Y|M) \right] + H(Y)$$

**Cognitive Cost Estimation:** The cognitive cost terms are estimated through:
- A pre-trained chunking network $f_{\text{chunk}}(M)$ trained on human memory span data
- Empirical entropy estimation from message distributions
- Softmax temperature annealing to encourage categorical concentration

The complete variational CCIB loss becomes:

$$\mathcal{L}_{\text{VCCIB}} = \mathbb{E}_{p(X)} \left[ D_{\text{KL}}(p_\theta(M|X) \| r(M)) \right] + \lambda \cdot \hat{\Psi}_H(M) - \beta \cdot \mathbb{E}_{p(M,Y)} \left[ \log q_\phi(Y|M) \right]$$

where $\theta$ parameterizes the sender (AI agent) and $\phi$ parameterizes the receiver (modeled human).

### 2.3 Training Procedure

**Algorithm: CCIB Training**

```
Input: Task environment E, cognitive parameters {α_WM, α_ATT, α_CAT, λ, β}
Initialize: Sender network θ, Receiver network φ, Prior r(M)

For each training iteration:
    1. Sample batch of observations X from E
    2. Generate messages: M ~ p_θ(M|X) using Gumbel-Softmax relaxation
    3. Compute task predictions: Ŷ = q_φ(Y|M)
    4. Estimate cognitive costs:
       - Chunk count via f_chunk(M)
       - Conditional entropy via batch statistics
       - Categorical concentration via entropy
    5. Compute L_VCCIB
    6. Update θ, φ via gradient descent
    7. Periodically anneal Gumbel temperature

Output: Trained sender θ* for human-AI communication
```

**Hyperparameter Calibration:** The cognitive parameters $\{\alpha_{\text{WM}}, \alpha_{\text{ATT}}, \alpha_{\text{CAT}}\}$ are calibrated through preliminary human studies measuring processing times and error rates across message complexity levels.

### 2.4 Experimental Design

We validate CCIB through two complementary experimental paradigms:

**Experiment 1: Referential Games**

*Setup:* A visual referential game where an AI sender observes a target image among distractors and must communicate to enable a human receiver to identify the target.

*Conditions:*
- **Baseline 1:** Standard emergent communication (EC) without cognitive constraints
- **Baseline 2:** Information Bottleneck EC (IB-EC) with standard compression
- **CCIB:** Our proposed cognitive-constrained approach
- **Human-Human:** Human sender-receiver pairs (gold standard)

*Stimuli:* 1,000 unique image sets using CLEVR-style synthetic images (controlling for object attributes) and 500 naturalistic image sets from Visual Genome.

*Participants:* 120 human participants (30 per AI condition, 30 for human-human), recruited via Prolific with demographic balancing.

*Measures:*
- Task accuracy (correct target identification)
- Communication efficiency (bits per successful transmission)
- Response time (human processing latency)
- Interpretability rating (7-point Likert scale: "How well did you understand the AI's message?")
- Protocol analysis (compositionality metrics, semantic alignment)

**Experiment 2: Collaborative Navigation**

*Setup:* A grid-world navigation task where an AI guide observes the full map and must communicate waypoint instructions to a human navigator with limited visibility.

*Conditions:* Same four conditions as Experiment 1.

*Task Variants:*
- Simple: Single obstacle, direct path
- Medium: Multiple obstacles, route planning required
- Complex: Dynamic obstacles, time pressure

*Participants:* 80 human participants across conditions.

*Measures:*
- Navigation success rate
- Path efficiency (actual vs. optimal path length)
- Communication overhead (messages per task)
- Cognitive load (NASA-TLX questionnaire)
- Qualitative interviews (thematic analysis of communication strategies)

### 2.5 Evaluation Metrics

**Information-Theoretic Metrics:**
- Compression ratio: $I(X; M) / H(X)$
- Task relevance: $I(M; Y) / H(Y)$
- Cognitive efficiency: $\text{Task Performance} / \Psi_H(M)$

**Compositionality Metrics:**
- Topographic similarity (Lazaridou et al., 2018): correlation between message distances and meaning distances
- Positional disentanglement: mutual information between message positions and semantic features
- Context independence: consistency of symbol meanings across contexts

**Human Alignment Metrics:**
- Semantic category overlap: Jaccard similarity between AI message clusters and human naming patterns
- Learnability: human accuracy improvement rate over exposure
- Transfer: performance on novel task instances

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Theoretical Contributions:**
1. A formal framework extending the Information Bottleneck principle to incorporate asymmetric cognitive constraints between communicating agents
2. Variational bounds enabling tractable optimization of cognitive-constrained objectives
3. Quantitative relationships between cognitive cost parameters and emergent language properties

**Empirical Findings:**
1. CCIB-trained agents are expected to achieve 15-25% higher human interpretability ratings compared to standard EC baselines while maintaining comparable task performance
2. Emergent protocols should exhibit significantly higher compositionality scores (predicted 40%+ improvement in topographic similarity)
3. Human cognitive load measures (NASA-TLX) should show 20-30% reduction when interacting with CCIB agents
4. Message structures should spontaneously align with human categorical boundaries without explicit supervision

**Methodological Contributions:**
1. Validated procedure for calibrating cognitive cost parameters from human behavioral data
2. Open-source implementation of CCIB training framework
3. Benchmark tasks and evaluation protocols for human-AI communication research

### Broader Impact

**Scientific Impact:** This work provides a principled bridge between information theory and cognitive science, demonstrating how empirical constraints can be formally incorporated into machine learning objectives. It advances our understanding of why human languages exhibit particular structural properties and how artificial systems can be designed to respect cognitive limitations.

**Practical Applications:** CCIB-trained agents have immediate applications in:
- Human-robot interaction where communication bandwidth is limited
- AI assistants that must convey complex information accessibly
- Collaborative AI systems in high-stakes domains (healthcare, emergency response) where interpretability is critical

**AI Alignment Implications:** By demonstrating that cognitive constraints can be formalized and incorporated into training objectives, this research contributes to the broader goal of developing AI systems that are inherently aligned with human capacities and preferences, rather than requiring post-hoc interpretability patches.

### Limitations and Future Directions

We acknowledge several limitations: cognitive cost parameters may vary across individuals and cultures; our experimental tasks, while controlled, may not capture full real-world complexity; and the variational bounds introduce approximation errors. Future work should explore personalized cognitive models, more naturalistic task settings, and tighter variational bounds.

This research establishes a foundation for information-theoretically principled human-AI communication, contributing both theoretical insights and practical tools for building AI systems that communicate in genuinely human-compatible ways.