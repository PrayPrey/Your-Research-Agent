# Research Proposal: SRALT: Self-Validating Spaced Repetition Architecture for LLM Tutoring with Deep Knowledge Tracing

## 1. Introduction

### 1.1 Background

The emergence of large language models (LLMs) such as GPT-4 has catalyzed a paradigm shift in educational technology, offering unprecedented opportunities for personalized, dialogue-based tutoring at scale. These models demonstrate remarkable capabilities in generating contextually appropriate explanations, answering student questions, and adapting to individual learning needs. However, despite their conversational sophistication, current LLM-based tutoring systems suffer from a fundamental limitation: they lack mechanisms for optimizing long-term knowledge retention and validating their own pedagogical effectiveness.

Cognitive science research has established robust principles for enhancing memory consolidation, with the spacing effect being among the most well-documented phenomena in learning science. Meta-analyses by Dunlosky et al. (2013) classify distributed practice as a "high utility" learning strategy, demonstrating that information reviewed at strategically spaced intervals is retained significantly longer than information studied in massed sessions. The SM-2 algorithm, originally developed for flashcard systems, provides a computational framework for implementing optimal review scheduling based on learner performance.

Simultaneously, advances in educational data mining have produced Deep Knowledge Tracing (DKT) models capable of predicting student mastery with high accuracy. Hooshyar et al. (2025) report that DKT achieves an AUC of 0.83 in predicting student performance, outperforming both traditional Bayesian Knowledge Tracing and LLM-based prediction approaches. This predictive capability offers a foundation for intelligent scheduling of learning activities.

Despite these advances, a critical gap exists: current LLM tutoring systems operate without integration of spacing-based retention optimization or validated mastery prediction. Students may demonstrate understanding during tutoring sessions but experience significant forgetting weeks later, with no system-level feedback mechanism to detect or correct this problem. This creates an educational technology that optimizes for immediate performance rather than durable learning.

### 1.2 Research Objectives

This research proposes SRALT (Self-Validating Spaced Repetition Architecture for LLM Tutoring), a hybrid architecture that combines DKT's predictive strength with LLM's dialogue capabilities to address the retention and validation gaps in current educational AI systems. Our specific objectives are:

1. **Design and implement** a hybrid architecture integrating independent DKT-based mastery prediction with LLM-based tutoring dialogue generation, connected through SM-2 algorithm-based review scheduling.

2. **Validate the retention hypothesis** that SRALT produces 20%+ higher long-term retention at 4-week intervals compared to standard LLM tutoring without spaced repetition integration.

3. **Establish self-validation capability** by demonstrating that DKT predictions correlate strongly (r > 0.7) with actual retention outcomes, enabling continuous system calibration.

4. **Evaluate feasibility** of the self-validating architecture in realistic educational deployments through a randomized controlled trial in Python programming education.

### 1.3 Significance

This research addresses the GAI→ED thrust of the GAIED workshop by exploring how generative AI can be enhanced through integration with established learning science principles and predictive modeling. The significance of this work is threefold:

**Theoretical Contribution**: SRALT resolves a key tension identified in recent literature—DKT excels at mastery prediction while LLMs excel at dialogue generation. Our hybrid architecture leverages each component's strengths, providing a principled framework for combining predictive and generative AI in education.

**Practical Impact**: By optimizing for long-term retention rather than immediate performance, SRALT addresses a fundamental limitation of current educational AI. The self-validation mechanism enables continuous improvement without requiring external evaluation studies, making the system sustainable for real-world deployment.

**Methodological Innovation**: The architecture generates prediction-outcome pairs that allow educational AI systems to verify and improve their own effectiveness—a capability essential for building trustworthy AI tutors that educators and policymakers can confidently deploy.

## 2. Methodology

### 2.1 System Architecture

SRALT operates through a four-step causal mechanism connecting mastery prediction, review scheduling, dialogue generation, and retention validation.

#### 2.1.1 Deep Knowledge Tracing Module

The DKT module processes student interaction sequences to estimate concept-level mastery probabilities. We employ a Long Short-Term Memory (LSTM) network that takes as input a sequence of student interactions:

$$\mathbf{x}_t = [\mathbf{q}_t \oplus \mathbf{a}_t]$$

where $\mathbf{q}_t$ is a one-hot encoding of the concept addressed at time $t$, $\mathbf{a}_t$ is the binary correctness indicator, and $\oplus$ denotes concatenation. The hidden state update follows:

$$\mathbf{h}_t = \text{LSTM}(\mathbf{x}_t, \mathbf{h}_{t-1})$$

Mastery prediction for concept $c$ at time $t$ is computed as:

$$P(a_{t+1} = 1 | c) = \sigma(\mathbf{W}_c \cdot \mathbf{h}_t + b_c)$$

where $\sigma$ is the sigmoid function, $\mathbf{W}_c$ is a concept-specific weight vector, and $b_c$ is the bias term.

The DKT model is trained on historical student interaction data using binary cross-entropy loss:

$$\mathcal{L}_{DKT} = -\sum_{t} [a_t \log(\hat{p}_t) + (1-a_t) \log(1-\hat{p}_t)]$$

#### 2.1.2 Spacing Scheduler Module

The spacing scheduler implements a modified SM-2 algorithm that incorporates DKT mastery predictions. For each concept $c$, the review interval $I_c$ is calculated as:

$$I_c(n) = I_c(n-1) \times EF_c$$

where $n$ is the review number and $EF_c$ is the easiness factor for concept $c$, updated based on DKT mastery prediction:

$$EF_c = \max(1.3, EF_c + 0.1 - (3 - q_c) \times (0.08 + (3 - q_c) \times 0.02))$$

Here, $q_c$ is a quality score derived from DKT mastery prediction:

$$q_c = \lfloor 5 \times P(a = 1 | c) \rfloor$$

Concepts with lower predicted mastery receive shorter review intervals, while high-mastery concepts are scheduled for longer gaps, optimizing the spacing effect across the concept hierarchy.

#### 2.1.3 LLM Tutoring Dialogue Module

When the scheduler triggers a review for concept $c$, the LLM generates contextual tutoring dialogue. The prompt construction follows:

```
System: You are a Python programming tutor. The student is reviewing 
{concept_name} with current mastery level {mastery_level}. Generate a 
review question appropriate for their level, then provide scaffolded 
feedback based on their response.

Context: Previous interactions: {interaction_history}
Student's common errors: {error_patterns}
Time since last review: {days_elapsed}
```

The LLM generates: (1) a review question calibrated to the student's mastery level, (2) scaffolded hints if the student struggles, and (3) explanatory feedback connecting the concept to previously mastered material.

#### 2.1.4 Validation and Calibration Module

The self-validation mechanism operates by comparing DKT predictions with delayed assessment outcomes. For each student $s$ and concept $c$, we record:

- $\hat{p}_{s,c}$: DKT-predicted mastery at end of learning phase
- $y_{s,c}$: Actual performance on 4-week delayed assessment

The system computes running correlation:

$$r = \frac{\sum_{s,c}(\hat{p}_{s,c} - \bar{\hat{p}})(y_{s,c} - \bar{y})}{\sqrt{\sum_{s,c}(\hat{p}_{s,c} - \bar{\hat{p}})^2 \sum_{s,c}(y_{s,c} - \bar{y})^2}}$$

When sufficient prediction-outcome pairs accumulate (≥100 pairs), the system can recalibrate DKT parameters through fine-tuning on the validation data, enabling continuous improvement.

### 2.2 Experimental Design

#### 2.2.1 Study Design

We conduct a randomized controlled trial comparing SRALT against standard LLM tutoring. The study follows a between-subjects design with two conditions:

- **SRALT Condition**: Full system with DKT-based mastery prediction, SM-2 spacing scheduler, and LLM tutoring dialogues
- **Control Condition**: Same LLM tutor without DKT integration or spaced repetition scheduling; students receive tutoring on-demand without optimized review timing

#### 2.2.2 Participants

We recruit $n = 100$ undergraduate students (50 per condition) from introductory computer science courses with the following inclusion criteria:
- No prior Python programming experience
- Commitment to 6-week study duration
- Access to computer with internet connection

Sample size is determined by power analysis: assuming Cohen's $d = 0.8$ (large effect based on spacing effect literature), $\alpha = 0.05$ (one-tailed), and power = 0.80, minimum required sample is $n = 26$ per group. We recruit 50 per group to account for anticipated 30% attrition.

#### 2.2.3 Learning Content

The curriculum covers Python programming fundamentals organized into 15 concepts:
1. Variables and data types
2. Arithmetic operators
3. String operations
4. Boolean logic
5. Conditional statements (if/else)
6. While loops
7. For loops
8. Lists
9. List operations
10. Dictionaries
11. Functions (definition)
12. Functions (parameters/returns)
13. File I/O
14. Error handling
15. Basic algorithms

Each concept includes 10 practice problems and 5 assessment items, calibrated for equivalent difficulty using Item Response Theory.

#### 2.2.4 Procedure

**Week 1-2 (Learning Phase)**:
- All participants complete initial tutoring sessions covering all 15 concepts
- SRALT condition: DKT tracks mastery; scheduler determines review timing
- Control condition: Students access tutoring on-demand without scheduling

**Week 2-4 (Review Phase)**:
- SRALT condition: System-initiated review sessions based on spacing schedule
- Control condition: Student-initiated review sessions (self-paced)
- Both conditions: Same LLM tutor for dialogue generation

**Week 6 (Assessment Phase)**:
- All participants complete delayed assessment (4 weeks after learning phase completion)
- Assessment includes 3 items per concept (45 total items)
- Proctored online administration with randomized item order

#### 2.2.5 Data Collection

**Interaction Data**:
- All student-system interactions logged with timestamps
- Problem attempts, correctness, response time, hint requests
- LLM dialogue transcripts

**DKT Predictions**:
- Concept-level mastery predictions recorded at end of each session
- Final mastery predictions at end of learning phase

**Assessment Data**:
- Immediate post-test (end of Week 2)
- Delayed post-test (Week 6)
- Item-level responses for diagnostic analysis

**Engagement Metrics**:
- Session frequency and duration
- Review completion rates
- System-initiated vs. student-initiated interactions

### 2.3 Evaluation Metrics

#### 2.3.1 Primary Outcome: Long-term Retention

Retention accuracy is calculated as percentage correct on the 4-week delayed assessment:

$$\text{Retention}_s = \frac{\text{Correct Items}_s}{\text{Total Items}} \times 100\%$$

**Success Criterion**: Mean retention difference between SRALT and Control > 20 percentage points with $p < 0.05$ (one-tailed independent samples t-test).

#### 2.3.2 Secondary Outcome: Prediction Accuracy

DKT prediction accuracy is measured by Pearson correlation between predicted mastery and actual retention:

$$r_{prediction} = \text{corr}(\hat{p}_{s,c}, y_{s,c})$$

**Success Criterion**: $r > 0.7$ with $p < 0.01$.

#### 2.3.3 Tertiary Outcome: Self-Validation Feasibility

System generates sufficient prediction-validation pairs for calibration:

$$\text{Validation Pairs}_s = \text{Concepts Predicted} \times \text{Assessments Completed}$$

**Success Criterion**: ≥80% of students complete ≥10 prediction-validation cycles.

#### 2.3.4 Falsification Criteria

The hypothesis is rejected if any of the following occur:
1. Retention difference ≤ 5% between conditions
2. DKT prediction-retention correlation $r ≤ 0.3$
3. < 50% of students complete delayed assessments

### 2.4 Statistical Analysis Plan

**Primary Analysis**: Independent samples t-test comparing mean retention between conditions. Effect size reported as Cohen's $d$ with 95% confidence interval.

**Secondary Analysis**: Pearson correlation with Fisher z-transformation for confidence interval estimation.

**Exploratory Analyses**:
- Concept-level retention analysis using mixed-effects models
- Engagement moderator analysis (high vs. low engagement subgroups)
- Learning curve analysis comparing mastery trajectories

**Missing Data**: Intent-to-treat analysis with multiple imputation for participants who complete learning but not delayed assessment.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome**: We predict that SRALT will produce significantly higher 4-week retention (>20% improvement) compared to standard LLM tutoring. This prediction is grounded in the robust spacing effect literature, which demonstrates large effect sizes ($d > 0.5$) for distributed practice across educational domains.

**Secondary Outcome**: We expect DKT predictions to correlate strongly ($r > 0.7$) with actual retention outcomes, validating the self-validation mechanism. This correlation would demonstrate that the system can accurately forecast long-term learning outcomes, enabling proactive intervention for at-risk students.

**Tertiary Outcome**: We anticipate that the architecture will successfully generate sufficient prediction-outcome pairs for continuous calibration, establishing feasibility of self-validating educational AI systems.

### 3.2 Theoretical Impact

This research contributes to the theoretical understanding of how generative AI can be enhanced through integration with established learning science principles. The hybrid architecture resolves the tension between DKT's predictive strength and LLM's generative capabilities, providing a principled framework for combining different AI approaches in education.

The self-validation mechanism addresses a fundamental challenge in educational AI: building systems that can verify and improve their own effectiveness without requiring external evaluation studies. This capability is essential for sustainable deployment of AI tutors in real-world educational settings.

### 3.3 Practical Impact

**For Educators**: SRALT provides a tutoring system that optimizes for durable learning rather than immediate performance, addressing concerns about superficial engagement with AI tutors. The self-validation capability offers transparency into system effectiveness.

**For Students**: The system delivers personalized review scheduling that adapts to individual learning patterns, reducing the cognitive burden of self-regulated study planning while improving long-term retention.

**For Policymakers**: The research demonstrates how AI tutoring systems can be designed with built-in accountability mechanisms, addressing concerns about validating educational AI effectiveness.

### 3.4 Limitations and Future Directions

**Scope Limitations**: The current study focuses on structured domains (programming) with clear concept hierarchies. Generalization to open-ended creative domains requires further investigation.

**Technical Limitations**: The cold-start problem for DKT with new students (requiring 5-10 interactions minimum) may limit immediate personalization. Future work could explore transfer learning approaches.

**Future Directions**: Successful validation would motivate extension to other STEM domains, investigation of optimal spacing parameters for different content types, and development of multi-modal tutoring incorporating code execution feedback.

### 3.5 Conclusion

SRALT represents a principled approach to enhancing LLM-based tutoring through integration of cognitive science principles and predictive modeling. By combining DKT's mastery prediction with LLM's dialogue generation and SM-2's spacing optimization, the architecture addresses critical gaps in current educational AI: long-term retention optimization and self-validation capability. The proposed randomized controlled trial will provide rigorous evidence for the effectiveness of this hybrid approach, contributing both theoretical insights and practical tools for the emerging field of generative AI in education.