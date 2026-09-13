# Research Proposal: Theory of Mind-Guided Prompt Engineering for Improved Human-AI Collaboration

## 1. Introduction

### Background

The proliferation of Large Language Models (LLMs) in human-facing applications has fundamentally transformed how humans interact with AI systems. From customer service chatbots to educational tutoring platforms, LLMs are increasingly deployed in contexts requiring nuanced understanding of user needs. However, a persistent challenge undermines these interactions: LLMs frequently generate responses misaligned with user intent, necessitating multiple clarification exchanges before achieving satisfactory outcomes. This misalignment stems from a fundamental limitation—current LLMs lack explicit mechanisms for reasoning about users' mental states, including their knowledge levels, unstated goals, implicit assumptions, and expectations.

Theory of Mind (ToM), the cognitive capacity to attribute mental states to oneself and others, represents a cornerstone of human social cognition. In human communication, ToM operates seamlessly: speakers automatically adjust their explanations based on perceived listener knowledge, anticipate potential misunderstandings, and calibrate responses to inferred emotional states. When humans collaborate, they naturally engage in perspective-taking, considering what their partner knows, believes, and desires. This capacity enables efficient communication with minimal explicit negotiation.

Recent research has begun exploring ToM in AI systems. Zhang et al. (2024) demonstrated that AI agents with ToM capabilities improve human understanding of AI and feelings of being understood, even when team performance metrics remain unchanged. Baughman et al. (2025) introduced meta-prompting methods for ToM alignment through reinforcement learning, while Gurney et al. (2024) distinguished between prompted and spontaneous ToM, arguing for principled approaches to artificial social intelligence. The work by Westby and Riedl (2023) on Bayesian Theory of Mind in human-AI teams further demonstrates that modeling teammates' mental states can enhance collective intelligence. Despite these advances, practical frameworks that systematically incorporate ToM reasoning into everyday LLM interactions remain underdeveloped.

### Research Objectives

This research proposes **ToM-Aware Prompting (TAP)**, a novel framework that augments LLM interactions with explicit mental state inference and response calibration mechanisms. Our objectives are:

1. To develop a computational framework that infers user mental states (knowledge level, goals, assumptions) from conversational context
2. To design perspective-taking modules that anticipate potential misunderstandings before generating responses
3. To implement response calibration mechanisms that adjust content depth and style based on inferred user states
4. To empirically validate TAP across diverse collaborative tasks, measuring efficiency gains and user satisfaction improvements

### Significance

This research addresses critical gaps identified in the literature. The challenge of accurate user intent modeling (Key Challenge 1) is tackled through our user modeling component. The integration of ToM in AI systems (Key Challenge 2) is operationalized through modular, interpretable components. By reducing clarification exchanges, we address communication load concerns (Key Challenge 3). Our framework provides a systematic approach to bridging semantic gaps in prompt engineering (Key Challenge 4) and establishes comprehensive evaluation metrics for human-AI collaboration (Key Challenge 5).

## 2. Methodology

### 2.1 Framework Architecture

TAP comprises three interconnected modules that operate sequentially during each interaction turn:

**Module 1: User State Inference (USI)**

The USI module constructs and maintains a dynamic user model from conversational history. For each user turn $u_t$ at time $t$, we extract three mental state dimensions:

- **Knowledge State** $K_t$: The estimated user expertise level in the relevant domain
- **Goal State** $G_t$: The inferred immediate and overarching objectives
- **Assumption State** $A_t$: Implicit presuppositions underlying the user's query

The user model at time $t$ is represented as:

$$M_t = \{K_t, G_t, A_t\}$$

Knowledge state estimation employs a hierarchical classification approach. Given conversation history $H_t = \{(u_1, r_1), ..., (u_{t-1}, r_{t-1}), u_t\}$ where $r_i$ represents system responses, we compute:

$$K_t = f_K(H_t; \theta_K) = \text{softmax}(W_K \cdot \text{BERT}(H_t) + b_K)$$

where $K_t \in \{novice, intermediate, expert\}$ and $\theta_K$ represents learned parameters.

Goal inference utilizes a multi-label classification approach combined with generative hypothesis formation:

$$G_t = \{g_t^{explicit}, g_t^{implicit}\}$$

where $g_t^{explicit}$ are directly stated goals extracted through semantic parsing, and $g_t^{implicit}$ are inferred through:

$$g_t^{implicit} = \text{LLM}(\text{prompt}_{goal}(H_t))$$

The prompt template instructs the LLM to generate hypotheses about unstated user objectives based on conversation patterns and domain context.

Assumption extraction identifies presuppositions through:

$$A_t = \text{LLM}(\text{prompt}_{assumption}(u_t, H_t))$$

where the prompt explicitly asks the model to identify what the user appears to take for granted.

**Module 2: Perspective-Taking Reasoning (PTR)**

Before generating a response, the PTR module simulates potential misunderstandings. This module implements what Gurney et al. (2024) term "prompted ToM" but extends it with systematic misunderstanding anticipation.

Given the current query $u_t$ and user model $M_t$, PTR generates a set of potential misalignment hypotheses:

$$\mathcal{H}_t = \{h_1, h_2, ..., h_k\}$$

Each hypothesis $h_i$ represents a specific way the response might fail to meet user expectations. We categorize misalignments into three types:

1. **Depth Mismatch** ($h^{depth}$): Response complexity inappropriate for user knowledge state
2. **Scope Mismatch** ($h^{scope}$): Response breadth not aligned with user goals
3. **Assumption Conflict** ($h^{assumption}$): Response contradicts or fails to address implicit user assumptions

The hypothesis generation process is:

$$\mathcal{H}_t = \text{LLM}(\text{prompt}_{PTR}(u_t, M_t, \mathcal{D}))$$

where $\mathcal{D}$ represents domain-specific misunderstanding patterns learned from training data.

**Module 3: Response Calibration (RC)**

The RC module synthesizes inputs from USI and PTR to generate appropriately calibrated responses. The calibration process adjusts three response parameters:

- **Explanation Depth** $d$: Amount of background information and step-by-step detail
- **Technical Register** $\tau$: Vocabulary complexity and formality level
- **Anticipatory Content** $\alpha$: Proactive clarifications addressing potential misunderstandings

The final response $r_t$ is generated through:

$$r_t = \text{LLM}(\text{prompt}_{RC}(u_t, M_t, \mathcal{H}_t, d, \tau, \alpha))$$

The calibration parameters are computed as:

$$d = f_d(K_t, G_t)$$
$$\tau = f_\tau(K_t, H_t)$$
$$\alpha = f_\alpha(\mathcal{H}_t)$$

where $f_d$, $f_\tau$, and $f_\alpha$ are rule-based functions derived from cognitive science principles of audience design.

### 2.2 Data Collection

**Training Data**

We will collect and annotate data from three collaborative task domains:

1. **Code Assistance**: 2,000 programming help conversations from Stack Overflow and GitHub Copilot interactions
2. **Educational Tutoring**: 2,000 tutoring sessions from online learning platforms covering STEM subjects
3. **Creative Writing**: 1,500 collaborative writing sessions from writing assistance platforms

For each conversation, expert annotators will label:
- User knowledge states per turn
- Explicit and implicit user goals
- Implicit assumptions
- Points of misunderstanding or clarification need

**Annotation Protocol**

Three trained annotators per conversation will provide labels, with disagreements resolved through discussion. Inter-annotator agreement will be measured using Fleiss' kappa, with a target $\kappa > 0.7$ for all annotation categories.

### 2.3 Experimental Design

**Baselines**

We compare TAP against:
1. **Standard Prompting (SP)**: Direct LLM response without ToM augmentation
2. **Chain-of-Thought Prompting (CoT)**: LLM with reasoning chain elicitation
3. **Few-Shot Exemplar Prompting (FSE)**: LLM with domain-specific examples
4. **Meta-Prompting (MP)**: Implementation following Baughman et al. (2025)

**Evaluation Metrics**

*Efficiency Metrics:*
- **Turns to Task Completion (TTC)**: Number of conversation turns required to complete the user's objective
- **Clarification Request Frequency (CRF)**: Proportion of turns containing user clarification requests

*Quality Metrics:*
- **Task Success Rate (TSR)**: Percentage of interactions achieving user goals
- **First-Response Adequacy (FRA)**: Expert rating (1-5) of initial response appropriateness

*User Experience Metrics:*
- **Perceived Understanding (PU)**: User rating of feeling understood (1-7 Likert scale)
- **Satisfaction Score (SS)**: Overall interaction satisfaction (1-7 Likert scale)
- **Cognitive Load Index (CLI)**: NASA-TLX adapted for conversational AI

**User Study Protocol**

We will conduct a between-subjects experiment with 300 participants (100 per domain), randomly assigned to TAP or baseline conditions. Each participant will complete three task scenarios of varying complexity. Post-interaction surveys will collect subjective metrics, while conversation logs will provide objective metrics.

### 2.4 Implementation Details

TAP will be implemented using GPT-4 as the base LLM, with modular prompts for each component. The system will be deployed as a web application with logging capabilities. All prompts will be iteratively refined through pilot testing with 30 participants before the main study.

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following quantitative outcomes:

1. **Efficiency Improvements**: 25-40% reduction in Turns to Task Completion compared to standard prompting, based on preliminary pilots and findings from Westby and Riedl (2023) showing ToM benefits in collaborative settings

2. **Enhanced First-Response Quality**: 30% improvement in First-Response Adequacy scores, reducing the need for immediate clarification

3. **User Experience Gains**: Significant improvements in Perceived Understanding scores (effect size $d > 0.5$), consistent with Zhang et al. (2024) findings that ToM capabilities enhance feelings of being understood

4. **Reduced Cognitive Burden**: Lower Cognitive Load Index scores, addressing the communication load challenge identified in the literature

### Theoretical Contributions

This research will advance understanding of:
- How explicit mental state modeling can be operationalized in LLM systems
- The relative importance of different ToM components (knowledge inference, goal modeling, assumption extraction) for response quality
- The relationship between computational ToM mechanisms and human perception of AI understanding

### Practical Impact

TAP provides immediately deployable improvements for:
- **Customer Service**: Reduced resolution times and improved satisfaction
- **Educational Technology**: Adaptive tutoring with appropriate scaffolding
- **Healthcare Communication**: Better-calibrated patient information delivery
- **Accessibility Tools**: Responses tailored to diverse user capabilities

### Broader Implications

By demonstrating that explicit ToM reasoning improves human-AI collaboration, this research contributes to the broader agenda of human value alignment. As Sharma et al. (2023) showed in mental health contexts, human-AI collaboration quality improves when systems respond appropriately to user states. TAP extends this principle to general-purpose interactions, offering a scalable approach to more empathic AI systems.

The modular, interpretable nature of TAP also addresses explainability concerns—users and developers can inspect what mental states the system inferred and how they influenced responses. This transparency is crucial for building appropriate trust in AI collaborators and enables iterative refinement of ToM mechanisms.