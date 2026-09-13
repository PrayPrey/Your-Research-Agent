# Research Proposal

## Title
Stakeholder-Adaptive Explanation Framework (SAEF): Ontology-Constrained Explainable AI for LLM-Based Educational Assessment

---

## 1. Introduction

### 1.1 Background

The integration of large language models (LLMs) into educational assessment represents a transformative opportunity to enhance the efficiency, consistency, and scalability of evaluation processes. Models such as GPT-4, Llama, and Gemini have demonstrated remarkable capabilities in understanding and generating human-like text, making them promising candidates for automated essay scoring, item generation, and personalized feedback delivery. However, despite their technical prowess, the adoption of LLMs in high-stakes educational assessment remains significantly constrained by a fundamental challenge: the lack of adequate explainability for diverse stakeholders.

Educational assessment ecosystems involve multiple stakeholder groups—teachers, students, parents, and administrators—each possessing fundamentally different mental models of what constitutes meaningful assessment feedback. A teacher requires pedagogically actionable insights that inform instructional decisions; a student needs clear guidance on specific areas for improvement; a parent seeks understandable summaries that contextualize their child's performance; and an administrator demands accountability metrics that ensure fairness and compliance. Current explainable AI (XAI) approaches, such as SHAP (SHapley Additive exPlanations) visualizations and attention weight displays, provide technically accurate but generically formatted outputs that fail to address these distinct informational needs.

This disconnect between powerful LLM assessment capabilities and stakeholder-appropriate explanations creates a critical trust barrier. Research by Haas et al. (2024) demonstrates that stakeholder-centric XAI significantly increases trust across all user types, while Mohammed (2025) shows that adaptive explanations tailored to expertise levels can improve comprehension by 27% and trust by 19%. However, no existing framework systematically addresses the challenge of translating LLM scoring rationales into role-appropriate explanations grounded in established educational ontologies.

### 1.2 Research Objectives

This research proposes the Stakeholder-Adaptive Explanation Framework (SAEF), a novel three-stage pipeline designed to transform LLM scoring explanations into role-appropriate formats. The primary objectives are:

1. **To develop a systematic methodology** for mapping technical XAI outputs (SHAP feature attributions) to established educational ontologies (CEFR, Bloom's Taxonomy, Webb's Depth of Knowledge).

2. **To design and validate role-specific explanation templates** that generate tailored explanations matching each stakeholder's mental model of educational assessment.

3. **To empirically evaluate** whether ontology-constrained, role-adapted explanations significantly improve stakeholder comprehension, trust calibration, and perceived actionability compared to generic XAI outputs.

### 1.3 Research Significance

This research addresses a critical gap at the intersection of AI and educational assessment. By bridging the divide between technical explainability and stakeholder understanding, SAEF has the potential to:

- **Enable broader adoption** of LLM-based assessment in educational settings by addressing trust and accountability concerns
- **Establish a replicable framework** for stakeholder-adaptive XAI that can extend beyond essay scoring to other assessment modalities
- **Contribute theoretical insights** into how educational ontologies can serve as semantic bridges between machine learning outputs and human understanding
- **Provide practical tools** for educational technology developers seeking to implement trustworthy AI systems

---

## 2. Methodology

### 2.1 Research Design Overview

The research employs a mixed-methods approach combining system development with empirical validation. The methodology consists of three phases: (1) SAEF pipeline development, (2) ontology mapping and template construction, and (3) empirical validation through a controlled experimental study.

### 2.2 Phase 1: SAEF Pipeline Development

#### 2.2.1 Architecture Overview

SAEF implements a three-stage pipeline that transforms raw LLM scoring decisions into stakeholder-appropriate explanations:

**Stage 1: SHAP Feature Extraction**

Given an essay $e$ and an LLM scoring function $f: E \rightarrow \mathbb{R}$, we compute SHAP values for interpretable features:

$$\phi_i(f, e) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} [f(S \cup \{i\}) - f(S)]$$

where $\phi_i$ represents the contribution of feature $i$ to the prediction, $N$ is the set of all features, and $S$ represents feature subsets. Features include linguistic dimensions such as coherence, vocabulary sophistication, grammatical accuracy, argument structure, and evidence usage.

**Stage 2: Ontology Mapping**

Technical features are mapped to educational ontology concepts through a mapping function $M: F \rightarrow O$, where $F$ is the feature space and $O$ is the ontology concept space. For each feature $f_i$ with SHAP value $\phi_i$, we identify the corresponding ontology concept $o_j$:

$$M(f_i, \phi_i) = \{(o_j, r_{ij}, \phi_i) : r_{ij} \in R, \text{sim}(f_i, o_j) > \theta\}$$

where $R$ represents the relationship types (e.g., "demonstrates," "lacks," "partially achieves"), $\text{sim}$ is a semantic similarity function, and $\theta$ is a threshold parameter.

The ontologies employed include:
- **CEFR (Common European Framework of Reference)**: For language proficiency levels (A1-C2)
- **Bloom's Taxonomy**: For cognitive complexity levels (Remember, Understand, Apply, Analyze, Evaluate, Create)
- **Webb's Depth of Knowledge (DOK)**: For cognitive demand levels (Recall, Skill/Concept, Strategic Thinking, Extended Thinking)

**Stage 3: Role-Specific Template Generation**

Ontology-mapped concepts are formatted using role-specific templates $T_r$ for each stakeholder role $r \in \{teacher, student, parent, administrator\}$:

$$E_r = T_r(M(F, \Phi), c)$$

where $E_r$ is the generated explanation for role $r$, and $c$ represents contextual parameters (essay topic, grade level, assessment purpose).

#### 2.2.2 Template Design Principles

Templates are designed following cognitive load theory and stakeholder mental model research:

| Stakeholder | Mental Model Focus | Template Characteristics |
|-------------|-------------------|-------------------------|
| Teacher | Pedagogical intervention | Specific skill gaps, instructional recommendations, rubric alignment |
| Student | Self-improvement | Concrete examples, growth-oriented language, next steps |
| Parent | Progress understanding | Comparative context, accessible language, support suggestions |
| Administrator | Accountability | Aggregate patterns, fairness metrics, compliance indicators |

### 2.3 Phase 2: Ontology Mapping and Template Construction

#### 2.3.1 Ontology Alignment Procedure

A panel of 3-5 educational measurement specialists will validate the mapping between SHAP features and ontology concepts. The procedure involves:

1. **Feature Inventory**: Catalog all extractable features from the LLM scoring model
2. **Concept Mapping**: Expert panel maps each feature to relevant ontology concepts
3. **Relationship Typing**: Define relationship types (positive/negative contribution, threshold-based)
4. **Validation**: Inter-rater reliability assessment (target: Krippendorff's $\alpha > 0.8$)

#### 2.3.2 Template Development

Templates undergo iterative refinement through:

1. **Initial Design**: Based on stakeholder mental model literature
2. **Cognitive Walkthrough**: Expert review for clarity and appropriateness
3. **Pilot Testing**: Small-scale testing with 5 representatives per stakeholder group
4. **Refinement**: Revision based on pilot feedback

#### 2.3.3 Semantic Fidelity Verification

To ensure explanations maintain fidelity to original XAI outputs, we compute BERTScore between source SHAP interpretations and generated explanations:

$$\text{BERTScore} = \frac{1}{|x|} \sum_{x_i \in x} \max_{y_j \in y} \text{cos}(\mathbf{x}_i, \mathbf{y}_j)$$

where $\mathbf{x}_i$ and $\mathbf{y}_j$ are contextual embeddings. Target threshold: BERTScore $> 0.7$.

### 2.4 Phase 3: Empirical Validation

#### 2.4.1 Experimental Design

A 4×4 mixed-design study will evaluate SAEF against baseline conditions:

**Independent Variables:**
- **Stakeholder Type** (between-subjects): Teacher, Student, Parent, Administrator
- **Explanation Format** (within-subjects): SAEF, GPT-4 prompt-only, Generic text, SHAP visualization

**Dependent Variables:**
- **Comprehension Score**: Quiz measuring understanding of assessment rationale (0-100%)
- **Trust Calibration**: Confidence-accuracy correlation coefficient ($r$)
- **Actionability Rating**: Likert scale rating on perceived usefulness (1-7)

**Controlled Variables:**
- Cognitive load (NASA-TLX subscales)
- Essay quality level (low/medium/high, balanced across conditions)
- Assessment domain (English language essay scoring)

#### 2.4.2 Participants

**Sample Size Calculation:**

Using G*Power for mixed-design ANOVA:
- Effect size: $f = 0.25$ (medium)
- Power: $1 - \beta = 0.80$
- Significance level: $\alpha = 0.05$
- Groups: 4 stakeholder types × 4 explanation formats

Required sample: $n \geq 30$ per cell = **480 total participants**

**Recruitment:**
- Teachers: K-12 and higher education instructors (n=120)
- Students: High school and undergraduate students (n=120)
- Parents: Parents of school-age children (n=120)
- Administrators: School principals, assessment coordinators (n=120)

#### 2.4.3 Materials

**Essay Corpus:**
The Automated Student Assessment Prize (ASAP) dataset containing 12,000+ essays across multiple prompts and score levels will serve as the primary corpus.

**Assessment Scenarios:**
Participants will review 4 essay-explanation pairs (one per explanation format), counterbalanced using a Latin square design to control for order effects.

**Measurement Instruments:**

1. **Comprehension Quiz** (10 items per scenario):
   - Multiple-choice questions testing understanding of score rationale
   - Items validated through pilot testing (target: Cronbach's $\alpha > 0.7$)

2. **Trust Calibration Protocol:**
   - Participants predict essay scores before viewing explanations
   - Rate confidence in predictions (1-10 scale)
   - Trust calibration = correlation between confidence and accuracy

3. **Actionability Scale** (7 items, 7-point Likert):
   - "This explanation helps me understand what to do next"
   - "I can use this information to support improvement"
   - Validated through factor analysis

#### 2.4.4 Procedure

1. **Informed Consent and Demographics** (5 minutes)
2. **Training Phase**: Introduction to essay scoring context (10 minutes)
3. **Evaluation Phase**: Review 4 essay-explanation pairs, complete measures after each (40 minutes)
4. **Post-Study Questionnaire**: Overall preferences, qualitative feedback (10 minutes)
5. **Debriefing** (5 minutes)

Total duration: Approximately 70 minutes per participant.

#### 2.4.5 Data Analysis Plan

**Primary Analysis:**

4×4 mixed-design ANOVA for each dependent variable:

$$Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \pi_{k(i)} + \epsilon_{ijk}$$

where $\alpha_i$ represents stakeholder type effect, $\beta_j$ represents explanation format effect, $(\alpha\beta)_{ij}$ represents interaction, $\pi_{k(i)}$ represents participant nested within stakeholder type, and $\epsilon_{ijk}$ represents error.

**Post-hoc Comparisons:**
Tukey HSD for pairwise comparisons with family-wise error rate control.

**Effect Size Reporting:**
Partial eta-squared ($\eta_p^2$) for ANOVA effects; Cohen's $d$ for pairwise comparisons.

**Reporting Standards:**
Mean ± SD, 95% confidence intervals, exact p-values.

#### 2.4.6 Ablation Study

To verify the causal mechanism, an ablation study will test component contributions:

| Condition | SHAP Extraction | Ontology Mapping | Role Templates |
|-----------|-----------------|------------------|----------------|
| Full SAEF | ✓ | ✓ | ✓ |
| No Templates | ✓ | ✓ | ✗ |
| No Ontology | ✓ | ✗ | ✓ |
| SHAP Only | ✓ | ✗ | ✗ |

This 2×2 factorial design (n=40 per cell, 160 total) will isolate the contribution of each pipeline component.

### 2.5 Evaluation Metrics Summary

| Metric | Measurement | Success Criterion |
|--------|-------------|-------------------|
| Comprehension | Quiz score (0-100%) | SAEF > 75%; SAEF > GPT-4 by ≥10 points |
| Trust Calibration | Confidence-accuracy $r$ | Δr > 0.15 improvement |
| Actionability | Likert scale (1-7) | SAEF > 5.5; Generic < 4.5 |
| Semantic Fidelity | BERTScore | > 0.7 |
| Statistical Significance | p-value | < 0.05 |

### 2.6 Falsification Criteria

The hypothesis will be considered falsified if:
1. **Primary Failure**: Comprehension(SAEF) ≤ Comprehension(SHAP visualization)
2. **Mechanism Failure**: BERTScore fidelity < 0.7
3. **Comparative Failure**: No significant difference on any measure across all comparisons

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcomes:**

1. **Comprehension Improvement**: We expect SAEF explanations to achieve comprehension scores exceeding 75%, with a minimum 10 percentage point improvement over GPT-4 prompt-only baselines. This prediction is grounded in Mohammed (2025)'s finding of 27% comprehension improvement with adaptive XAI.

2. **Trust Calibration Enhancement**: Role-adapted explanations are expected to improve trust calibration by Δr > 0.15, indicating that stakeholders develop more accurate confidence in their understanding of LLM assessments.

3. **Actionability Ratings**: SAEF explanations are expected to achieve actionability ratings above 5.5 on a 7-point scale, significantly exceeding generic explanations (expected < 4.5).

**Secondary Outcomes:**

4. **Stakeholder-Specific Patterns**: We anticipate differential effects across stakeholder types, with teachers showing strongest improvements in pedagogical actionability and students showing strongest improvements in self-regulation indicators.

5. **Component Contribution Analysis**: The ablation study is expected to reveal that ontology mapping contributes approximately 40% of the improvement, with role-specific templates contributing an additional 35%.

### 3.2 Theoretical Contributions

This research contributes to multiple theoretical domains:

1. **Explainable AI Theory**: Demonstrates that domain-specific ontologies can serve as effective semantic bridges between technical XAI outputs and human understanding, extending current XAI frameworks beyond generic visualization approaches.

2. **Educational Assessment Theory**: Provides empirical evidence for the importance of stakeholder mental models in assessment communication, supporting calls for differentiated feedback systems.

3. **Human-AI Interaction**: Advances understanding of how role-based adaptation affects trust calibration in AI-assisted decision-making contexts.

### 3.3 Practical Impact

**For Educational Technology Developers:**
- Replicable framework for implementing stakeholder-adaptive explanations
- Validated templates and ontology mappings for immediate application
- Design guidelines for trustworthy AI in educational contexts

**For Educational Institutions:**
- Evidence-based approach to deploying LLM assessment with appropriate transparency
- Tools for addressing accountability requirements in AI-assisted evaluation
- Framework for communicating AI decisions to diverse stakeholder groups

**For Policy and Standards:**
- Empirical foundation for explainability requirements in educational AI
- Model for stakeholder-inclusive AI governance in assessment contexts

### 3.4 Limitations and Future Directions

**Acknowledged Limitations:**
- Ontology construction requires domain expertise and may not generalize automatically to new assessment domains
- Template-based approach may feel formulaic compared to fully generative explanations
- Study focuses on English language essay scoring; transfer to other modalities requires validation

**Future Research Directions:**
1. Extension to multimodal assessment (mathematics, science with diagrams)
2. Longitudinal studies examining sustained trust and learning outcomes
3. Automated ontology mapping using knowledge graph techniques
4. Real-time adaptive explanation systems for formative assessment

### 3.5 Conclusion

The Stakeholder-Adaptive Explanation Framework represents a principled approach to addressing the critical trust barrier limiting LLM adoption in educational assessment. By grounding explanations in established educational ontologies and tailoring outputs to stakeholder mental models, SAEF bridges the gap between powerful AI capabilities and meaningful human understanding. The proposed empirical validation will provide rigorous evidence for the framework's effectiveness, contributing both theoretical insights and practical tools for the responsible deployment of AI in education.

---

**Keywords:** Large Language Models, Explainable AI, Educational Assessment, Automated Essay Scoring, Stakeholder Trust, Educational Ontologies, SHAP, Human-AI Interaction