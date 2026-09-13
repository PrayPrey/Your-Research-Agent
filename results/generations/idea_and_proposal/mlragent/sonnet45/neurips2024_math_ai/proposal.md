# Research Proposal: Hierarchical Error Taxonomy Learning for Personalized Mathematical Reasoning Assistance

## 1. Title

**Hierarchical Error Taxonomy Learning for Personalized Mathematical Reasoning Assistance in Educational Contexts**

## 2. Introduction

### 2.1 Background

Mathematical reasoning is a cornerstone of human cognition, essential for problem-solving across diverse domains from scientific research to everyday decision-making. Despite its importance, mathematics education faces persistent challenges, particularly in providing individualized feedback to students. Traditional classroom settings often cannot accommodate personalized instruction at scale, and this limitation is especially acute in resource-constrained educational environments where student-to-teacher ratios are high.

Recent advances in large language models (LLMs) have demonstrated remarkable capabilities in mathematical problem-solving, with systems achieving high accuracy on standardized mathematics benchmarks. However, a critical gap exists between solving problems correctly and providing effective pedagogical support. Human expert tutors excel not merely by knowing correct solutions, but by diagnosing the specific nature of student errors—distinguishing between conceptual misunderstandings, procedural mistakes, algebraic manipulation errors, and simple computational slips. This diagnostic capability enables targeted interventions that address the root cause of confusion rather than simply presenting correct solutions.

Current AI-based tutoring systems typically provide binary feedback (correct/incorrect) or complete worked solutions, missing the pedagogical opportunity to guide students through their specific misconceptions. As evidenced by recent work on stepwise verification (Daheim et al., 2024), identifying the precise location and nature of errors in student reasoning remains challenging for existing models. Furthermore, while systems like LeanTutor (Patel et al., 2025) can verify formal proofs and MathAgent (Yan et al., 2025) can detect errors in multimodal mathematical content, these approaches have not fully addressed the creation of comprehensive, hierarchical error taxonomies aligned with pedagogical theory.

### 2.2 Research Objectives

This research proposes to develop a novel AI system capable of:

1. **Automatically classifying mathematical errors** according to a hierarchical taxonomy grounded in mathematics education research
2. **Providing personalized, targeted feedback** that matches the diagnosed error type and student proficiency level
3. **Adapting intervention strategies** based on individual student learning trajectories
4. **Validating effectiveness** through rigorous empirical evaluation measuring actual student learning gains

The hierarchical error taxonomy will encompass five primary categories:
- **Conceptual errors**: Misunderstanding of fundamental mathematical principles
- **Procedural errors**: Incorrect selection or sequencing of solution strategies
- **Algebraic manipulation errors**: Mistakes in applying algebraic rules and transformations
- **Computational errors**: Arithmetic calculation mistakes
- **Notation and representation errors**: Misuse of mathematical symbols and conventions

### 2.3 Significance

This research addresses a critical need at the intersection of artificial intelligence and education. By enabling AI systems to provide diagnostic, personalized feedback, we can:

- **Enhance learning efficiency**: Students receive targeted guidance addressing their specific knowledge gaps rather than generic explanations
- **Improve educational equity**: High-quality, personalized tutoring becomes accessible in resource-limited contexts where individual human tutoring is unavailable
- **Advance AI capabilities**: Develop models that not only solve problems but understand the reasoning process itself, contributing to interpretable AI
- **Inform pedagogical practice**: Generate large-scale data on common error patterns that can guide curriculum design and teacher training

The significance extends beyond immediate educational applications. Understanding error patterns in mathematical reasoning can illuminate fundamental questions about how both humans and machines process mathematical information, contributing to cognitive science and the broader goal of developing AI systems capable of genuine mathematical understanding.

## 3. Methodology

### 3.1 Data Collection and Dataset Creation

#### 3.1.1 Multi-Source Data Acquisition

We will construct a comprehensive dataset combining:

**Real Student Data**: Partner with educational platforms (e.g., Khan Academy, ASSISTments) to collect anonymized student solution attempts with timestamps, covering algebra, geometry, calculus, and word problems. Target sample size: 50,000+ student solutions across 2,000+ unique problems.

**Expert Annotation**: Recruit 15-20 mathematics educators with 5+ years teaching experience to annotate a subset of 5,000 solutions with:
- Primary error classification according to our taxonomy
- Secondary error types (for solutions with multiple mistakes)
- Error severity (minor/major)
- Recommended intervention type
- First error location (step number where reasoning breaks down)

Inter-annotator agreement will be measured using Fleiss' kappa, with disagreements resolved through discussion to establish annotation guidelines.

**Synthetic Data Generation**: Leverage LLMs to generate diverse incorrect solutions by:
- Prompting GPT-4 to produce solutions with specific error types
- Applying rule-based perturbations to correct solutions (e.g., sign flips, incorrect formula substitutions)
- Using chain-of-thought prompting to generate plausible incorrect reasoning chains

This yields an additional 20,000 synthetic examples, providing coverage of rare error types.

#### 3.1.2 Hierarchical Taxonomy Structure

The error taxonomy will be formalized as a tree structure:

**Level 1** (Broad Categories):
- Conceptual (C)
- Procedural (P)
- Algebraic (A)
- Computational (M)
- Notation (N)

**Level 2** (Specific Error Types):
- C1: Misunderstanding of definitions
- C2: Incorrect theorem application
- C3: Faulty mathematical intuition
- P1: Wrong strategy selection
- P2: Incomplete solution steps
- P3: Incorrect step sequencing
- A1: Sign errors
- A2: Distribution errors
- A3: Fraction manipulation errors
- M1: Arithmetic calculation mistakes
- M2: Order of operations errors
- N1: Variable misuse
- N2: Symbol confusion

Each solution will be annotated with a path through this hierarchy (e.g., C→C2 indicates incorrect theorem application).

### 3.2 Model Architecture and Training

#### 3.2.1 Multi-Task Learning Framework

We propose a transformer-based architecture with shared encoder and specialized heads:

**Encoder**: Fine-tune a mathematical reasoning model (base: Llama-3 or Minerva) to produce contextual representations of problem statements and solution steps.

For a problem $p$ and solution sequence $s = [s_1, s_2, ..., s_n]$, the encoder produces representations:

$$h_i = \text{Encoder}(p, s_1, ..., s_i), \quad i \in \{1, ..., n\}$$

**Task Heads**:

1. **Error Detection Head**: Binary classifier identifying whether step $s_i$ contains an error
   $$P(\text{error}_i) = \sigma(W_d h_i + b_d)$$

2. **Error Localization Head**: Identifies the first erroneous step
   $$P(\text{first\_error} = i | \text{error exists}) = \text{softmax}(W_l [h_1, ..., h_n])_i$$

3. **Error Classification Head**: Multi-label classifier for error taxonomy
   $$P(\text{error\_type}_i) = \sigma(W_c h_i + b_c)$$
   where output dimension equals number of taxonomy categories

4. **Solution Generation Head**: Autoregressive decoder producing correct solution
   $$P(s_i^{\text{correct}} | p, s_1^{\text{correct}}, ..., s_{i-1}^{\text{correct}}) = \text{Decoder}(h_{i-1})$$

**Multi-Task Loss**:
$$\mathcal{L} = \lambda_d \mathcal{L}_{\text{detection}} + \lambda_l \mathcal{L}_{\text{localization}} + \lambda_c \mathcal{L}_{\text{classification}} + \lambda_s \mathcal{L}_{\text{solution}}$$

where:
- $\mathcal{L}_{\text{detection}}$ = binary cross-entropy for error detection
- $\mathcal{L}_{\text{localization}}$ = cross-entropy for first error position
- $\mathcal{L}_{\text{classification}}$ = hierarchical cross-entropy (described below)
- $\mathcal{L}_{\text{solution}}$ = negative log-likelihood of correct solution
- $\lambda_d, \lambda_l, \lambda_c, \lambda_s$ are task weights optimized via grid search

#### 3.2.2 Hierarchical Classification Loss

To leverage taxonomy structure, we employ hierarchical softmax:

$$\mathcal{L}_{\text{classification}} = -\sum_{i=1}^{L} \alpha_i \log P(c_i | c_1, ..., c_{i-1})$$

where $c_i$ is the correct category at level $i$, $L$ is taxonomy depth, and $\alpha_i$ are level weights (increasing with depth to prioritize fine-grained classification).

#### 3.2.3 Contrastive Learning for Error Representations

To learn discriminative representations distinguishing correct reasoning from near-miss errors, we incorporate contrastive learning:

For each correct solution step $s_i^+$, generate counterfactual erroneous steps $\{s_i^{-,1}, s_i^{-,2}, ..., s_i^{-,k}\}$ by applying error-inducing transformations. The contrastive loss is:

$$\mathcal{L}_{\text{contrastive}} = -\log \frac{\exp(h_i^+ \cdot h_i^+ / \tau)}{\exp(h_i^+ \cdot h_i^+ / \tau) + \sum_{j=1}^k \exp(h_i^+ \cdot h_i^{-,j} / \tau)}$$

where $\tau$ is temperature parameter and $h_i^+, h_i^{-,j}$ are normalized encoder outputs.

This encourages the model to learn that small changes in reasoning steps can indicate significant errors, improving error detection sensitivity.

### 3.3 Adaptive Tutoring System

#### 3.3.1 Feedback Generation Module

Given an identified error of type $e$ at step $i$, the feedback generator produces targeted hints using a retrieval-augmented generation approach:

1. **Retrieve** examples of similar errors and effective interventions from a pedagogical knowledge base
2. **Rank** interventions by:
   - Error type match
   - Student proficiency level (estimated from historical performance)
   - Intervention complexity
3. **Generate** personalized feedback via fine-tuned LLM conditioned on:
   - Problem context
   - Error classification
   - Student model (knowledge state)
   - Top-ranked intervention strategies

**Feedback Types** (selected based on error severity and student proficiency):
- **Socratic hints**: Guiding questions without revealing solutions
- **Worked examples**: Similar problems with correct solutions
- **Conceptual explanations**: Addressing underlying misconceptions
- **Immediate correction**: Direct feedback for computational errors

#### 3.3.2 Student Modeling

Maintain a dynamic student knowledge model tracking:
- Mastery level for each mathematical concept (via Bayesian Knowledge Tracing):
  $$P(L_{t+1} = 1) = P(L_t = 1 | \text{evidence}_t) + (1 - P(L_t = 1 | \text{evidence}_t)) \cdot P(\text{learn})$$
- Error pattern history (frequency of each error type)
- Response to different intervention types

This model informs feedback personalization and problem sequencing.

### 3.4 Experimental Design and Evaluation

#### 3.4.1 Offline Evaluation

**Error Classification Performance**:
- **Metrics**: Precision, Recall, F1-score for each taxonomy category; Hierarchical F1-score accounting for taxonomy structure
- **Baselines**: GPT-4 with few-shot prompting; fine-tuned BERT classifier; LeanTutor error detection
- **Test Set**: 1,000 held-out student solutions with expert annotations

**Error Localization Accuracy**:
- Percentage of solutions where first error is correctly identified
- Mean absolute error in predicted error location

**Ablation Studies**:
- Impact of multi-task learning (vs. single-task error classification)
- Effect of contrastive learning component
- Contribution of synthetic data

#### 3.4.2 Online Evaluation: Randomized Controlled Trial

**Experimental Design**:
- **Participants**: 600 students (ages 14-18) from partner schools, stratified by prior math achievement
- **Duration**: 12 weeks
- **Conditions**:
  1. **Control**: Standard online practice with correct/incorrect feedback
  2. **Generic AI Tutor**: LLM-based tutor providing full solutions
  3. **Hierarchical Error Tutor (HET)**: Our system with diagnostic feedback
  
**Procedure**:
- Pre-test measuring mathematical proficiency across algebra and geometry
- Weekly practice sessions (3 × 30-minute sessions)
- Post-test (same format as pre-test)
- Delayed post-test (4 weeks after intervention)

**Primary Outcome Measures**:
- **Learning Gains**: Normalized gain $g = \frac{\text{post} - \text{pre}}{100 - \text{pre}}$
- **Transfer Performance**: Novel problem types not seen during training
- **Self-Efficacy**: Mathematics Confidence Scale survey

**Secondary Measures**:
- Time to problem completion
- Number of hints requested
- Solution attempt quality (partial credit scoring)
- Engagement metrics (session completion rate, time on task)

**Statistical Analysis**:
- ANCOVA with pre-test scores as covariate
- Effect sizes (Cohen's d) for pairwise comparisons
- Subgroup analyses by prior achievement level
- Significance threshold: α = 0.05 with Bonferroni correction

#### 3.4.3 Qualitative Evaluation

Conduct semi-structured interviews with:
- 30 students across experimental conditions (10 per condition)
- 10 mathematics teachers observing the system

**Interview Themes**:
- Perceived helpfulness and clarity of feedback
- Comparison to human tutoring experiences
- Suggestions for improvement

Analyze via thematic coding to identify emergent patterns in user experience.

### 3.5 Implementation Details

- **Computing Resources**: 4× NVIDIA A100 GPUs for model training
- **Training Time**: Estimated 7 days for full multi-task model
- **Frameworks**: PyTorch, Hugging Face Transformers, LangChain for feedback generation
- **Deployment**: Web-based interface accessible via standard browsers; backend API for integration with learning management systems

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Technical Contributions**:

1. **Novel Dataset**: A comprehensive, publicly-released dataset of 75,000+ annotated mathematical solutions with hierarchical error classifications, addressing the data scarcity challenge in mathematical education AI research

2. **State-of-the-Art Error Classification**: Anticipate achieving >85% accuracy in broad error category classification and >70% in fine-grained error type identification, surpassing current baselines by ≥15% based on preliminary experiments

3. **Effective Multi-Task Architecture**: Demonstrate that joint training on error detection, localization, classification, and solution generation improves performance across all tasks compared to single-task approaches, with expected improvements of 10-15% in error localization accuracy

4. **Validated Contrastive Learning Approach**: Show that contrastive learning on correct vs. erroneous reasoning steps produces more discriminative representations, improving error detection sensitivity particularly for subtle conceptual errors

**Educational Outcomes**:

1. **Significant Learning Gains**: Based on meta-analyses of intelligent tutoring systems, we anticipate the Hierarchical Error Tutor will produce learning gains of 0.4-0.6 standard deviations compared to control (medium to large effect size)

2. **Improved Transfer**: Students receiving diagnostic feedback are expected to show 20-30% better performance on novel transfer problems compared to those receiving generic feedback, indicating deeper conceptual understanding

3. **Enhanced Engagement**: Predict 15-20% higher session completion rates and increased time-on-task for the diagnostic feedback condition, as personalized feedback increases perceived relevance

4. **Equitable Benefits**: Expect the system to be particularly beneficial for students with lower prior achievement (potentially 50% larger effect sizes), helping to close achievement gaps

### 4.2 Broader Impact

**Advancing AI for Education**:

This research directly addresses the workshop's core question: "To what extent can machine learning models comprehend mathematics?" By moving beyond solution generation to error diagnosis, we develop models that demonstrate understanding of the reasoning process itself—not merely pattern matching but principled analysis of logical validity. This contributes to interpretable AI by producing systems that can explain why solutions are incorrect in pedagogically meaningful terms.

**Bridging Human and Machine Mathematical Reasoning**:

The hierarchical error taxonomy provides a structured framework for comparing human and machine reasoning errors. Analysis of which error types are more prevalent in student vs. AI-generated solutions will illuminate fundamental differences in how humans and machines approach mathematical problems, contributing to cognitive science and AI alignment research.

**Scalable Educational Equity**:

The practical deployment of this system can democratize access to high-quality mathematics tutoring. In resource-limited educational contexts—rural schools, developing regions, or any setting with high student-to-teacher ratios—students can receive personalized guidance approaching the quality of individual human tutoring. Conservative estimates suggest that if deployed at scale, such systems could reach 100,000+ students annually who would otherwise lack access to personalized support.

**Informing Curriculum Design**:

The large-scale error pattern data generated through system deployment will provide unprecedented insights into common mathematical misconceptions and their prevalence across different topics and student populations. This empirical foundation can guide curriculum designers, textbook authors, and teacher training programs to proactively address identified gaps.

**Future Research Directions**:

This work establishes foundations for several promising research directions:

1. **Multi-Step Error Recovery**: Extending the system to guide students through multi-step error correction processes
2. **Collaborative Problem-Solving**: Adapting the framework to analyze and support collaborative mathematical reasoning among student groups
3. **Cross-Domain Transfer**: Applying hierarchical error taxonomy learning to other domains requiring procedural reasoning (programming, physics problem-solving, logical argumentation)
4. **Metacognitive Skill Development**: Using error pattern feedback to help students develop self-monitoring and error-detection capabilities

**Ethical Considerations and Limitations**:

We acknowledge important limitations and ethical considerations:

- **Bias in Error Classification**: Taxonomy and training data may reflect biases in what errors are considered "serious" vs. "minor," potentially disadvantaging students from non-traditional mathematical backgrounds
- **Over-Reliance Risk**: Students might become dependent on AI feedback rather than developing independent problem-solving skills
- **Privacy**: Student performance data requires careful protection and informed consent
- **Teacher Displacement Concerns**: System should be positioned as augmenting, not replacing, human teachers

To address these concerns, we will:
- Conduct bias audits of error classifications across demographic groups
- Include pedagogical safeguards encouraging student independence (e.g., progressive hint systems)
- Implement rigorous data protection protocols and obtain IRB approval
- Engage teachers as collaborators in system design and evaluation

### 4.3 Dissemination Plan

Research outcomes will be disseminated through:

1. **Academic Publications**: Target venues including NeurIPS, ICML (AI/ML contributions), and educational technology conferences like EDM, AIED, and LAK
2. **Open-Source Release**: Public release of dataset, model code, and trained models via GitHub and Hugging Face
3. **Educational Partnerships**: Work with partner schools and educational platforms to enable real-world deployment
4. **Policy Briefs**: Translate findings for education policymakers and administrators
5. **Teacher Professional Development**: Develop workshops helping teachers effectively integrate AI tutoring into classroom practice

In conclusion, this research proposal presents a comprehensive plan to develop AI systems capable of diagnostic mathematical reasoning—a crucial capability for effective educational technology. By combining advances in deep learning with insights from mathematics education research, we aim to create systems that not only solve problems but understand the reasoning process well enough to guide human learners through their individual learning journeys. The expected outcomes promise significant contributions to both artificial intelligence research and educational practice, with potential for meaningful real-world impact on student learning and educational equity.