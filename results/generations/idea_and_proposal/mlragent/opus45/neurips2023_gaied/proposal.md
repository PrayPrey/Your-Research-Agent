# Research Proposal: Calibrated Uncertainty Signals for AI Tutors: Teaching Students When to Trust (and Doubt) Machine-Generated Explanations

## 1. Introduction

### Background

The rapid proliferation of large language models (LLMs) in educational settings presents both unprecedented opportunities and significant challenges. AI-powered tutoring systems, exemplified by tools like ChatGPT-based educational assistants, have demonstrated remarkable capabilities in generating explanations, solving problems, and providing personalized learning support. However, a critical limitation undermines their educational value: these systems typically present information with uniform confidence, regardless of underlying accuracy. This phenomenon creates a dangerous epistemic environment where students may uncritically accept incorrect explanations or unnecessarily doubt correct ones.

The educational implications are profound. Students in formative learning stages are particularly vulnerable to misinformation, as they lack the domain expertise to evaluate AI-generated content critically. Research in educational psychology consistently demonstrates that incorrect information, once encoded, can be extraordinarily difficult to remediate—a phenomenon known as the "continued influence effect." Furthermore, the polished, authoritative tone of LLM outputs exacerbates this problem, creating what researchers term "automation bias" wherein users defer to algorithmic outputs despite contradictory evidence.

Recent advances in uncertainty quantification for LLMs offer promising avenues for addressing this challenge. Work by Stangel et al. (2025) demonstrates that reinforcement learning can fine-tune models to express calibrated confidence estimates, while Stengel-Eskin et al. (2024) show that listener-aware finetuning can align confidence markers with actual expertise. However, these technical advances have not been systematically translated into pedagogically-grounded educational applications.

### Research Objectives

This research proposes developing the **Uncertainty-Aware Educational AI (UAEI)** framework, which augments LLM-based tutors with calibrated confidence signals and metacognitive scaffolding. Our specific objectives are:

1. **Technical Objective**: Develop a multi-source uncertainty quantification system that combines semantic entropy, retrieval-based verification, and ensemble disagreement to produce calibrated confidence estimates for educational explanations.

2. **Design Objective**: Create pedagogically-informed uncertainty communication mechanisms that translate technical uncertainty metrics into developmentally-appropriate cues that promote verification behaviors without undermining productive trust.

3. **Empirical Objective**: Evaluate the UAEI framework's impact on calibration quality, student learning outcomes, and the development of critical AI literacy through controlled experimental studies.

### Significance

This research addresses both thrusts of the GAIED workshop agenda. For GAI→ED, UAEI represents a fundamental advancement in educational AI by creating tutoring systems that model not just domain knowledge but also epistemic humility. For ED→GAI, the framework provides technical safeguards against misinformation propagation while fostering the development of AI-literate learners capable of navigating an increasingly AI-mediated information landscape. The resulting system would transform AI tutors from potential sources of authoritative misinformation into tools for developing critical thinking skills—a meta-educational benefit that extends far beyond any specific domain.

## 2. Methodology

### 2.1 Overall Framework Architecture

The UAEI framework consists of three interconnected modules: (1) Multi-Source Uncertainty Quantification (MSUQ), (2) Pedagogical Uncertainty Communication (PUC), and (3) Adaptive Verification Scaffolding (AVS). These modules operate in sequence, with the MSUQ module computing raw uncertainty estimates, the PUC module transforming these into student-appropriate signals, and the AVS module generating context-aware verification prompts.

### 2.2 Multi-Source Uncertainty Quantification (MSUQ)

The MSUQ module integrates three complementary uncertainty estimation approaches to produce robust confidence scores.

**Semantic Entropy Estimation**: Following recent advances in uncertainty quantification, we compute semantic entropy by generating multiple responses to the same query and measuring their semantic clustering. For a given educational query $q$ and a set of $N$ generated responses $\{r_1, r_2, ..., r_N\}$, we compute:

$$SE(q) = -\sum_{c \in C} P(c|q) \log P(c|q)$$

where $C$ represents the set of semantic clusters identified through embedding-based clustering, and $P(c|q)$ is the proportion of responses belonging to cluster $c$. Higher semantic entropy indicates greater uncertainty.

**Retrieval-Based Verification Confidence**: We augment the LLM with retrieval from verified educational resources (textbooks, curricula standards, peer-reviewed educational materials). The retrieval confidence score is computed as:

$$RC(q, r) = \max_{d \in D} \text{sim}(e_r, e_d) \cdot \text{qual}(d)$$

where $D$ is the corpus of verified documents, $e_r$ and $e_d$ are embeddings of the response and document respectively, $\text{sim}(\cdot)$ computes cosine similarity, and $\text{qual}(d) \in [0,1]$ represents the source quality score.

**Ensemble Disagreement**: We employ a lightweight ensemble of $K$ model variants (achieved through dropout sampling or LoRA ensemble methods inspired by work on uncertainty-penalized RLHF). Disagreement is quantified as:

$$ED(q) = 1 - \frac{1}{K(K-1)} \sum_{i \neq j} \text{sim}(r_i, r_j)$$

**Unified Confidence Score**: The final calibrated confidence score combines these sources through a learned weighting function:

$$\text{Conf}(q, r) = \sigma\left(w_1 \cdot (1 - SE(q)) + w_2 \cdot RC(q, r) + w_3 \cdot (1 - ED(q)) + b\right)$$

where $\sigma$ is the sigmoid function, and weights $\{w_1, w_2, w_3, b\}$ are optimized using a calibration dataset with ground-truth correctness labels, minimizing expected calibration error (ECE):

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{n} |\text{acc}(B_m) - \text{conf}(B_m)|$$

where $B_m$ represents confidence bins, $\text{acc}(B_m)$ is the accuracy within bin $m$, and $\text{conf}(B_m)$ is the average confidence.

### 2.3 Pedagogical Uncertainty Communication (PUC)

Raw uncertainty scores must be translated into student-appropriate signals. The PUC module implements a multi-level communication strategy informed by research on metacognition and educational psychology.

**Confidence Level Discretization**: Continuous confidence scores are mapped to five pedagogically-meaningful levels:

| Level | Confidence Range | Student-Facing Language |
|-------|------------------|-------------------------|
| 5 | $\geq 0.90$ | "I'm confident this is correct." |
| 4 | $[0.75, 0.90)$ | "I believe this is right, but consider checking." |
| 3 | $[0.55, 0.75)$ | "This is my best understanding—let's verify together." |
| 2 | $[0.35, 0.55)$ | "I'm uncertain here. Please check other sources." |
| 1 | $< 0.35$ | "I'm really not sure. Let's find a reliable source." |

**Visual Uncertainty Indicators**: Alongside verbal cues, we implement visual signals including:
- Color-coded confidence meters (green to red gradient)
- Animated "thinking" indicators for uncertain responses
- Source attribution highlighting when retrieval confidence is high

**Adaptive Communication Based on Student Profile**: The PUC module adjusts communication style based on:
- Student age/grade level (simpler language for younger students)
- Prior interaction history (students who rarely verify receive more explicit prompts)
- Domain familiarity (more detailed uncertainty explanations in unfamiliar domains)

### 2.4 Adaptive Verification Scaffolding (AVS)

When uncertainty exceeds threshold $\tau$ (empirically determined through pilot studies), the AVS module generates verification prompts.

**Verification Strategy Selection**: Based on uncertainty source and educational context, the system selects from:
1. **Textbook reference**: "Let's check Chapter 5 of your textbook together."
2. **Worked example comparison**: "Can you compare this to the example problem we did earlier?"
3. **Instructor consultation**: "This might be a great question for your teacher."
4. **Peer discussion**: "Would you like to discuss this with a classmate?"

**Scaffolded Verification Process**: Rather than simply directing students elsewhere, AVS guides the verification process:

$$\text{Scaffold}(q, r, \text{source}) = \text{Generate}(\text{prompt}_\text{guide} | q, r, \text{source})$$

where $\text{prompt}_\text{guide}$ templates guide students through comparison, discrepancy identification, and resolution.

### 2.5 Training and Calibration

**Dataset Construction**: We construct a calibration dataset comprising:
- 10,000 educational questions across STEM subjects (mathematics, physics, chemistry, biology)
- Multiple LLM-generated responses per question
- Expert-annotated correctness labels
- Difficulty ratings and common misconception tags

**Calibration Training**: The confidence weighting parameters are optimized using a held-out calibration set, minimizing a combined loss:

$$\mathcal{L} = \text{ECE} + \lambda \cdot \text{BCE}(\text{Conf}, y)$$

where BCE is binary cross-entropy with ground-truth correctness labels $y$, and $\lambda$ balances calibration with discrimination ability.

### 2.6 Experimental Design

**Study 1: Calibration Quality Evaluation**
- *Participants*: N/A (technical evaluation)
- *Materials*: 2,000 held-out educational questions with expert annotations
- *Metrics*: Expected Calibration Error (ECE), Maximum Calibration Error (MCE), Brier Score, AUROC for incorrect response detection
- *Baselines*: Raw LLM token probabilities, temperature-scaled probabilities, single-source uncertainty methods

**Study 2: Controlled Learning Experiment**
- *Participants*: 200 high school students (ages 14-18), randomly assigned to conditions
- *Conditions*: (1) Standard AI tutor, (2) UAEI with uncertainty signals, (3) UAEI with uncertainty + verification scaffolds
- *Task*: Two-week algebra tutoring intervention (30 minutes daily)
- *Measures*: 
  - Pre/post content knowledge assessments
  - Transfer problems testing conceptual understanding
  - Misconception prevalence assessment
  - Student verification behavior logs

**Study 3: AI Literacy Development**
- *Participants*: Same cohort as Study 2, plus 100 additional students
- *Measures*:
  - AI Literacy Scale (adapted from existing instruments)
  - Critical evaluation tasks (distinguishing reliable from unreliable AI outputs)
  - Think-aloud protocols during AI interaction
  - Six-month follow-up on AI usage patterns

**Evaluation Metrics Summary**:
1. *Technical*: ECE, MCE, Brier Score, AUROC
2. *Learning*: Pre-post gain scores, transfer task performance, misconception reduction rate
3. *Behavioral*: Verification frequency, time to verify, verification quality
4. *AI Literacy*: AI Literacy Scale scores, critical evaluation accuracy, appropriate trust calibration

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Contributions**:
1. A validated multi-source uncertainty quantification system achieving ECE < 0.05, representing state-of-the-art calibration for educational LLM applications
2. Open-source implementation of the UAEI framework, adaptable to various educational contexts and LLM backends
3. A curated dataset of 10,000+ educational questions with expert-annotated correctness and difficulty labels

**Empirical Findings**:
1. Evidence regarding the relationship between uncertainty communication and student learning outcomes, hypothesizing 15-20% improvement in learning gains for the UAEI condition
2. Characterization of optimal uncertainty thresholds and communication strategies across student populations
3. Longitudinal evidence of AI literacy development, anticipating significant improvements in critical AI evaluation skills

**Design Guidelines**:
1. Evidence-based recommendations for uncertainty communication in educational AI
2. Framework for adaptive verification scaffolding applicable across domains
3. Student-centered design patterns for trustworthy AI tutoring systems

### Broader Impact

This research addresses fundamental challenges at the intersection of AI and education. By developing AI tutors that model epistemic humility, we contribute to a future where AI enhances rather than undermines critical thinking development. The UAEI framework transforms the current paradigm—where students must independently assess AI reliability without support—into one where the AI itself scaffolds appropriate trust calibration.

For the GAI→ED thrust, this work demonstrates how advances in uncertainty quantification can be translated into tangible educational benefits, creating AI tutors that are not just knowledgeable but epistemically responsible. For ED→GAI, the framework provides technical solutions to educator concerns about AI misinformation while simultaneously developing the AI literacy skills students need to navigate an AI-rich world.

Ultimately, this research contributes to developing a generation of learners who can harness AI's educational benefits while maintaining the critical stance necessary for informed, autonomous learning. This balance—productive trust paired with healthy skepticism—represents the ideal outcome for AI-enhanced education.