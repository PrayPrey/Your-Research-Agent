# Research Proposal: Adaptive Pedagogical Prompting: Training LLMs to Scaffold Learning Through Socratic Dialogue

## 1. Title

**Adaptive Pedagogical Prompting: Training Large Language Models to Scaffold Learning Through Context-Aware Socratic Dialogue**

## 2. Introduction

### Background

The rapid advancement of generative AI, particularly large language models (LLMs) like GPT-4 and ChatGPT, has created unprecedented opportunities for personalized education. However, a critical misalignment exists between the capabilities of current AI tutors and established pedagogical principles. Research in learning sciences consistently demonstrates that effective tutoring involves strategic questioning, scaffolding, and maintaining "productive struggle" rather than simply providing direct answers (Chi et al., 2001). Unfortunately, standard LLMs, when deployed as educational assistants, tend to provide complete solutions, potentially undermining the development of independent problem-solving skills and fostering learned helplessness.

The Socratic method, which emphasizes guided questioning to stimulate critical thinking and illuminate ideas through dialogue, has proven effective across educational contexts. Yet, implementing authentic Socratic dialogue requires sophisticated pedagogical awareness: knowing when to intervene, what level of hint to provide, how to address misconceptions without revealing answers, and when to let students struggle productively. Current LLM-based tutoring systems lack this pedagogical intelligence, operating primarily as question-answering systems rather than learning facilitators.

Recent work has begun addressing this gap. SocraticAI (Sunil & Thakkar, 2025) demonstrated that scaffolded interactions can guide students toward more sophisticated problem-solving approaches. The framework proposed by Cohn et al. (2025) integrates Evidence-Centered Design with Social Cognitive Theory to develop adaptive scaffolding. However, these approaches primarily focus on system design and interaction patterns rather than fundamentally training the underlying LLM to internalize pedagogical strategies. Furthermore, existing systems often optimize for student satisfaction rather than learning outcomes, creating perverse incentives for models to provide excessive assistance.

### Research Objectives

This research proposes to develop and validate a comprehensive fine-tuning framework that trains LLMs to employ pedagogically-sound Socratic questioning strategies adaptively. The specific objectives are:

1. **Develop a Pedagogically-Annotated Dialogue Dataset**: Create a comprehensive dataset of expert tutor-student interactions across multiple STEM domains, annotated with pedagogical strategy labels, student knowledge states, and learning outcomes.

2. **Design an Adaptive Scaffolding Fine-Tuning Framework**: Implement a reinforcement learning from human feedback (RLHF) approach where rewards explicitly prioritize learning gains, productive struggle duration, and student self-explanation quality over immediate satisfaction.

3. **Create a Context-Aware Prompting System**: Build a dynamic intervention mechanism that adjusts scaffolding levels based on real-time inference of student affect, prior attempts, and knowledge state from dialogue history.

4. **Validate Educational Effectiveness**: Conduct rigorous A/B testing comparing the pedagogically-trained model against standard LLM tutors, measuring learning gains, transfer performance, and development of metacognitive skills.

### Significance

This research addresses both GAI→ED and ED→GAI thrusts identified in the GAIED workshop framework. For GAI→ED, it advances educational technology by creating AI tutors that embody evidence-based pedagogical practices, potentially democratizing access to high-quality tutoring. For ED→GAI, it provides safeguards against over-reliance on AI by training models to promote independent thinking rather than dependency.

The broader impact extends beyond immediate educational applications. This work contributes methodologically to value-aligned AI by demonstrating how to optimize LLMs for complex, long-term objectives (learning) rather than immediate metrics (answer accuracy). It also provides insights into training AI systems that balance support with challenge—a pattern applicable across domains requiring skill development.

## 3. Methodology

### 3.1 Data Collection and Dataset Construction

#### 3.1.1 Expert Tutor-Student Dialogue Collection

We will collect dialogue data through three complementary approaches:

**Human Tutoring Sessions**: Partner with 30-50 expert tutors across mathematics, physics, and computer science to conduct 500+ one-on-one tutoring sessions with students at high school and undergraduate levels. Sessions will be video-recorded (with consent) and transcribed, capturing 20-30 minute problem-solving interactions.

**Existing Dialogue Corpora**: Integrate publicly available tutoring dialogue datasets, including portions of the Teachers' Discourse Moves (TDM) dataset and relevant subsets from existing intelligent tutoring system logs.

**Simulated Student Interactions**: Generate synthetic dialogues using a "student simulator" where human educators interact with an LLM role-playing students at varying knowledge levels, allowing controlled exploration of pedagogical strategies.

#### 3.1.2 Pedagogical Annotation Schema

Each dialogue turn will be annotated along multiple dimensions:

**Pedagogical Strategy Categories**:
- Metacognitive prompts (e.g., "What's your plan for solving this?")
- Conceptual probes (e.g., "Why does this relationship hold?")
- Procedural hints at levels 1-5 (from general to specific)
- Misconception diagnosis and addressing
- Encouragement and affective support
- Self-explanation elicitation

**Student State Indicators**:
- Inferred knowledge state: $K_t \in \{novice, partial, proficient\}$
- Affective state: $A_t \in \{confused, frustrated, engaged, confident\}$
- Struggle duration: number of unsuccessful attempts $n_{attempts}$
- Progress indicators: movement toward solution

**Outcome Measures**:
- Problem completion success
- Quality of student explanations (rated 1-5)
- Learning gain on isomorphic transfer problems

Annotation will be performed by trained educational researchers with inter-rater reliability target of Cohen's $\kappa > 0.75$.

### 3.2 Adaptive Scaffolding Model Development

#### 3.2.1 Base Model Selection and Initial Fine-Tuning

We will begin with a state-of-the-art open-source LLM (e.g., LLaMA-2 70B or Mistral-8x7B) and perform initial supervised fine-tuning (SFT) on the annotated dialogue dataset. The training objective maximizes the likelihood of expert tutor responses given dialogue history:

$$\mathcal{L}_{SFT} = -\sum_{i=1}^{N} \log P_\theta(r_i | h_i, s_i)$$

where $r_i$ is the tutor response, $h_i$ is the dialogue history, $s_i$ represents annotated student state features, and $\theta$ are model parameters.

#### 3.2.2 Reinforcement Learning from Human Feedback (RLHF)

The critical innovation lies in designing a reward model that prioritizes learning outcomes over immediate satisfaction. We formulate this as a multi-objective optimization problem:

**Reward Function Design**:

$$R(dialogue) = \alpha \cdot R_{learning} + \beta \cdot R_{struggle} + \gamma \cdot R_{explanation} - \delta \cdot R_{dependency}$$

Where:

- $R_{learning}$: Learning gain measured as performance improvement on post-interaction assessment relative to pre-test baseline:
$$R_{learning} = \frac{score_{post} - score_{pre}}{score_{max} - score_{pre}}$$

- $R_{struggle}$: Productive struggle maintenance, rewarding appropriate challenge duration:
$$R_{struggle} = \begin{cases} 
1 & \text{if } t_{min} \leq t_{struggle} \leq t_{max} \\
0.5 & \text{if } t_{struggle} < t_{min} \\
-0.5 & \text{if } t_{struggle} > t_{max}
\end{cases}$$

- $R_{explanation}$: Quality of student self-explanations, rated by human evaluators or a trained classification model:
$$R_{explanation} = \frac{1}{M}\sum_{j=1}^{M} quality(explanation_j)$$

- $R_{dependency}$: Penalty for over-assistance, measured by ratio of direct answers to prompting questions:
$$R_{dependency} = -\frac{n_{direct\_answers}}{n_{total\_turns}}$$

The coefficients $\alpha, \beta, \gamma, \delta$ will be tuned through educational expert consultation and validation studies, with initial values $\{0.5, 0.2, 0.2, 0.1\}$ respectively.

**PPO Training**: We implement Proximal Policy Optimization (PPO) to fine-tune the model using this reward structure:

$$\mathcal{L}_{PPO}(\theta) = \mathbb{E}_t[\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]$$

where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ is the probability ratio and $\hat{A}_t$ is the advantage estimate based on our composite reward function.

#### 3.2.3 Context-Aware Prompting System

To enable dynamic adaptation, we develop a student state inference module that processes dialogue history to estimate current student state:

**State Inference Model**: A separate neural classifier processes the dialogue history using a BERT-based encoder to predict:
- Current knowledge level: $\hat{K}_t = f_K(h_{1:t})$
- Affective state: $\hat{A}_t = f_A(h_{1:t})$
- Optimal intervention level: $\hat{I}_t = f_I(h_{1:t}, \hat{K}_t, \hat{A}_t)$

**Dynamic Prompt Construction**: The inferred state informs system prompts that guide the LLM's response generation:

```
System Prompt Template:
You are an expert tutor using Socratic dialogue. 
Student knowledge level: {K_t}
Student appears: {A_t}
Appropriate intervention: {I_t}
Strategy: {selected_strategy(K_t, A_t, I_t)}
Respond accordingly without giving direct answers.
```

The strategy selection function $selected\_strategy$ implements a decision tree based on pedagogical best practices, mapping state combinations to recommended approaches (e.g., if $K_t = novice$ and $A_t = confused$, use conceptual probe; if $K_t = partial$ and $n_{attempts} > 3$, provide level-2 hint).

### 3.3 Experimental Design and Validation

#### 3.3.1 Controlled Laboratory Study (Phase 1)

**Participants**: 120 undergraduate students recruited from introductory STEM courses, randomly assigned to three conditions:
1. Adaptive Pedagogical LLM (APL) - our trained model
2. Standard LLM tutor (baseline)
3. Human expert tutor (gold standard)

**Procedure**: 
- Pre-test on target domain knowledge (30 minutes)
- Tutoring session on 3 isomorphic problems (45 minutes)
- Immediate post-test (30 minutes)
- One-week delayed transfer test with novel problems (30 minutes)
- Metacognitive awareness inventory

**Metrics**:
- *Primary*: Learning gains = (post-test - pre-test) / (max - pre-test)
- *Transfer*: Performance on novel isomorphic problems
- *Self-explanation quality*: Coded using ICAP framework (Chi & Wylie, 2014)
- *Metacognitive development*: MAI inventory scores
- *Interaction patterns*: Dialogue turn analysis, hint level distribution
- *User experience*: Cognitive load (NASA-TLX), satisfaction surveys

#### 3.3.2 Ecological Validity Study (Phase 2)

**Deployment**: Integrate both APL and baseline systems into actual courses at 2-3 partner institutions across different STEM disciplines.

**Design**: Within-subjects crossover design where students use both systems across different problem sets, with order counterbalanced.

**Sample**: 300+ students over one semester

**Longitudinal Metrics**:
- Course performance on relevant assessments
- System usage patterns and engagement over time
- Self-reported dependency and confidence measures
- Instructor observations and feedback

#### 3.3.3 Statistical Analysis Plan

Primary analysis will use mixed-effects models accounting for student random effects:

$$Y_{ij} = \beta_0 + \beta_1 Condition_j + \beta_2 PreTest_i + u_i + \epsilon_{ij}$$

where $Y_{ij}$ is the outcome for student $i$ in condition $j$, $u_i$ is the random student effect, and $\epsilon_{ij}$ is residual error.

Effect sizes will be reported using Cohen's $d$ with target detection of medium effects ($d \geq 0.5$) at power $\geq 0.80$.

### 3.4 Ethical Considerations and Safeguards

**Data Privacy**: All student data will be de-identified and stored securely following IRB protocols. Consent forms will explicitly detail data usage.

**Bias Mitigation**: Regular auditing of model outputs across demographic groups to detect differential performance. Annotation team diversity to reduce cultural bias in labeling.

**Transparency**: Students will be clearly informed they are interacting with AI and can request human assistance at any time.

**Failure Handling**: Implement detection for when students are persistently struggling (>5 unsuccessful attempts) to automatically escalate to human tutors.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Technical Contributions**:
1. A novel RLHF framework optimizing for long-term educational outcomes rather than immediate satisfaction, demonstrating 15-25% improvement in learning gains compared to standard LLM tutors
2. An open-source pedagogically-annotated dialogue dataset of 500+ expert tutoring sessions across multiple STEM domains
3. A validated context-aware prompting architecture that dynamically adjusts scaffolding based on inferred student state
4. Detailed analysis of interaction patterns showing how pedagogically-trained models distribute hint levels and elicit self-explanation more effectively

**Educational Contributions**:
1. Empirical validation that LLMs can be trained to implement authentic Socratic dialogue, maintaining productive struggle while providing appropriate support
2. Evidence regarding transfer effects: students tutored by APL showing improved performance on novel problems (target: 20% better than baseline)
3. Demonstration of metacognitive skill development through AI interaction, measured via MAI inventory improvements
4. Guidelines for educators on effective integration of pedagogically-aware AI tutors in classroom settings

**Methodological Contributions**:
1. A replicable framework for value-aligned AI training in educational contexts
2. Novel reward function design balancing multiple pedagogical objectives
3. Validated approaches for measuring productive struggle and self-explanation quality in automated systems

### 4.2 Broader Impact

**Democratizing Access to Quality Tutoring**: By encoding expert pedagogical strategies in accessible AI systems, this research can help address educational inequality, providing students without access to human tutors with high-quality learning support.

**Informing Educational Policy**: Concrete evidence about AI tutors that promote rather than undermine learning will inform institutional policies around generative AI usage, moving beyond blanket prohibitions toward thoughtful integration.

**Advancing Human-AI Collaboration in Education**: This work exemplifies a model where AI augments rather than replaces human educators, handling routine scaffolding while human teachers focus on higher-order guidance and relationship building.

**Cross-Domain Applications**: The principles of adaptive scaffolding and context-aware prompting extend beyond education to any domain requiring skill development—professional training, health behavior change, creative skill acquisition.

**Contributing to Value-Aligned AI**: Demonstrates how to optimize AI systems for complex, multifaceted human values (learning, growth, autonomy) rather than simple metrics (accuracy, completion time), providing a blueprint for responsible AI development.

### 4.3 Limitations and Future Work

**Current Scope Limitations**: 
- Initial focus on STEM domains may limit generalizability to humanities and arts education
- Laboratory and semester-long studies cannot capture long-term developmental effects
- Reliance on predominantly English-language interactions

**Future Directions**:
- Extend to broader disciplines and multilingual contexts
- Investigate longer-term impacts on student self-regulated learning skills over multiple years
- Explore peer-learning scenarios where multiple students interact with AI-mediated collaborative problem-solving
- Develop educator-facing tools allowing teachers to customize pedagogical strategies for their specific contexts
- Investigate how pedagogical training interacts with other safety considerations (factual accuracy, bias mitigation)

### 4.4 Dissemination Plan

Results will be disseminated through:
- Publications in both AI venues (NeurIPS, ICLR) and education conferences (EDM, AIED, GAIED)
- Open-source release of dataset, fine-tuned models, and training code
- Workshops for educators on effective AI tutor integration
- Policy briefs for educational administrators and policymakers

This comprehensive research program directly addresses the GAIED workshop's dual mandate of advancing educational technology through generative AI while implementing crucial safeguards that align AI behavior with sound pedagogical principles. By training LLMs to scaffold learning rather than simply provide answers, we can harness the power of generative AI to genuinely enhance education rather than merely automate it.